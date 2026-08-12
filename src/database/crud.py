import streamlit as st
import pandas as pd
from supabase import create_client, Client
import uuid
from datetime import datetime, timedelta
import bcrypt

@st.cache_resource
def obter_conexao_supabase() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = obter_conexao_supabase()

def buscar_agendamentos(medico_id: str) -> list:
    resposta = supabase.table('agendamentos').select(
        'id, tipo_evento, data_hora_inicio, data_hora_fim, status, observacoes, pacientes(pessoas(nome_completo))'
    ).eq('medico_id', str(medico_id)).execute()
    
    dados_banco = resposta.data 
    
    cores_por_tipo = {
        "Primeira Consulta": "#1f77b4", 
        "Retorno": "#2ca02c",           
        "Cirurgia": "#9467bd",          
        "Bloqueio Pessoal": "#d62728"   
    }

    eventos_calendario = []
    
    for linha in dados_banco:
        dados_paciente = linha.get('pacientes') 
        dados_pessoa = dados_paciente.get('pessoas') if dados_paciente else None
        paciente_nome = dados_pessoa.get('nome_completo') if dados_pessoa else None
        
        tipo_evento = linha.get('tipo_evento')
        titulo = f"{paciente_nome} ({tipo_evento})" if paciente_nome else tipo_evento
        
        eventos_calendario.append({
            "id": linha.get('id'),
            "title": titulo,
            "start": linha.get('data_hora_inicio'), 
            "end": linha.get('data_hora_fim'),
            "color": cores_por_tipo.get(tipo_evento, "#333333"),
            "status": linha.get('status'),
            "observacoes": linha.get('observacoes')
        })
        
    return eventos_calendario

def buscar_pacientes_para_select() -> list:
    resposta = supabase.table('pacientes').select('pessoa_id, pessoas(nome_completo)').execute()
    
    lista_formatada = [{"id": None, "nome": "Bloqueio/Plantão"}]
    
    for linha in resposta.data:
        dados_pessoa = linha.get('pessoas')
        nome_paciente = dados_pessoa.get('nome_completo') if dados_pessoa else "Sem Nome"
        
        lista_formatada.append({
            "id": linha.get('pessoa_id'), 
            "nome": nome_paciente
        })
        
    return lista_formatada

def inserir_agendamento(
    medico_id: str,
    paciente_id: str,
    data_hora_inicio: datetime,
    data_hora_fim: datetime,
    tipo_evento: str,
    status: str,
    observacoes: str,
    criado_por_id: str
):
    dados_insercao = {
        "id": str(uuid.uuid4()),
        "medico_id": str(medico_id),
        "paciente_id": str(paciente_id) if paciente_id else None,
        "data_hora_inicio": data_hora_inicio.isoformat(),
        "data_hora_fim": data_hora_fim.isoformat(),
        "tipo_evento": tipo_evento,
        "status": status,
        "observacoes": observacoes,
        "criado_por_id": str(criado_por_id)
    }
    
    resposta = supabase.table('agendamentos').insert(dados_insercao).execute()
    
    return resposta.data

def buscar_dados_dashboard(medico_id: str) -> pd.DataFrame:
    resposta = supabase.table('atendimentos').select(
        'data_atendimento, local_atendimento, tipo_consulta, valor'
    ).eq('medico_id', str(medico_id)).execute()
    
    dados = resposta.data
    
    if not dados:
        return pd.DataFrame(columns=['data', 'local', 'tipo', 'valor'])
        
    df = pd.DataFrame(dados)
    
    df = df.rename(columns={
        'data_atendimento': 'data',
        'local_atendimento': 'local',
        'tipo_consulta': 'tipo',
        'valor': 'valor'
    })
    
    df['data'] = pd.to_datetime(df['data'])
    df['valor'] = pd.to_numeric(df['valor'], errors='coerce').fillna(0)
    
    return df

def buscar_medicos_vinculados(secretaria_id: str) -> list:
    """
    Busca apenas os médicos que estão vinculados à secretária/equipe logada.
    Caminho do Join: vinculo_equipe_medico -> medicos -> pessoas
    """
    resposta = supabase.table('vinculo_equipe_medico') \
        .select('medico_id, medicos(pessoas(nome_completo))') \
        .eq('equipe_id', str(secretaria_id)) \
        .execute()
    
    lista_formatada = []
    
    for linha in resposta.data:
        id_do_medico = linha.get('medico_id')
        dados_medico = linha.get('medicos') 
        dados_pessoa = dados_medico.get('pessoas') if dados_medico else None
        nome = dados_pessoa.get('nome_completo') if dados_pessoa else "Sem Nome"
        
        lista_formatada.append({
            "id": id_do_medico, 
            "nome": f"Dr(a). {nome}"
        })
        
    return lista_formatada

def listar_todos_usuarios():
    """
    Busca todas as pessoas e faz um join com medicos e equipe_apoio.
    """
    resposta = supabase.table('pessoas').select(
        'id, nome_completo, cpf, status, data_cadastro, '
        'medicos(crm, especialidade, email), '
        'equipe_apoio(papel, email)'
    ).execute()
    
    return resposta.data

def atualizar_status_usuario(pessoa_id: str, novo_status: str):
    """
    Atualiza o status de um usuário na tabela 'pessoas' (Aprovar, Recusar, Inativo).
    """
    resposta = supabase.table('pessoas').update(
        {'status': novo_status}
    ).eq('id', str(pessoa_id)).execute()
    
    return resposta.data

def criar_usuario_completo(nome, cpf, email, perfil, crm, especialidade, senha_hash):
    """
    Cadastra uma pessoa e a vincula automaticamente como Médico ou Equipe de Apoio.
    """
    res_pessoa = supabase.table('pessoas').insert({
        'nome_completo': nome,
        'cpf': cpf,
        'status': 'Ativo'
    }).execute()
    
    pessoa_id = res_pessoa.data[0]['id']
    
    if perfil == 'Médico':
        supabase.table('medicos').insert({
            'pessoa_id': pessoa_id,
            'email': email,
            'crm': crm,
            'especialidade': especialidade,
            'senha_hash': senha_hash
        }).execute()
    else:
        supabase.table('equipe_apoio').insert({
            'pessoa_id': pessoa_id,
            'email': email,
            'papel': perfil,
            'senha_hash': senha_hash
        }).execute()
        
    return pessoa_id

def atualizar_senha_usuario(pessoa_id: str, perfil: str, senha_texto_claro: str):
    """
    Gera o hash da nova senha e atualiza no banco de dados junto com a data atual.
    """
    senha_bytes = senha_texto_claro.encode('utf-8')
    novo_hash = bcrypt.hashpw(senha_bytes, bcrypt.gensalt()).decode('utf-8')
    data_atual = datetime.now().isoformat()
    
    if perfil == 'Médico':
        resposta = supabase.table('medicos').update({
            'senha_hash': novo_hash,
            'data_ultima_troca_senha': data_atual
        }).eq('pessoa_id', str(pessoa_id)).execute()
    else:
        resposta = supabase.table('equipe_apoio').update({
            'senha_hash': novo_hash,
            'data_ultima_troca_senha': data_atual
        }).eq('pessoa_id', str(pessoa_id)).execute()
        
    return resposta.data

def buscar_medicos_publico():
    """
    Busca os médicos ativos para exibir na página pública de agendamentos.
    """
    resposta = supabase.table('medicos').select(
        'pessoa_id, especialidade, pessoas!pessoa_id(nome_completo, status)'
    ).execute()
    
    medicos_ativos = []
    for m in resposta.data:
        if m.get('pessoas', {}).get('status') == 'Ativo':
            medicos_ativos.append({
                'id': m['pessoa_id'],
                'nome': f"Dr(a). {m['pessoas']['nome_completo']}",
                'especialidade': m.get('especialidade', 'Geral')
            })
    return medicos_ativos

def criar_agendamento_publico(medico_id, data_hora_inicio, nome, email, telefone, observacoes):
    """
    Salva a solicitação (Lead) feita pelo paciente na internet.
    """
    inicio_obj = datetime.fromisoformat(data_hora_inicio)
    fim_obj = inicio_obj + timedelta(minutes=30)
    
    resposta = supabase.table('agendamentos').insert({
        'medico_id': medico_id,
        'data_hora_inicio': inicio_obj.isoformat(),
        'data_hora_fim': fim_obj.isoformat(),
        'tipo_evento': 'Consulta',
        'status': 'Pendente', 
        'nome_solicitante': nome,
        'email_solicitante': email,
        'telefone_solicitante': telefone,
        'observacoes': f"[VIA WEB] {observacoes}"
    }).execute()
    
    return resposta.data

def aprovar_agendamento_web(agendamento_id: int, nome_paciente: str, email_paciente: str, telefone_paciente: str):
    """
    Verifica se o paciente já existe pelo e-mail. Se sim, apenas vincula. 
    Se não, cadastra o novo paciente antes de aprovar o agendamento.
    """
    busca_paciente = supabase.table('pacientes').select('pessoa_id').eq('email', email_paciente.strip().lower()).execute()
    
    if busca_paciente.data:
        paciente_oficial_id = busca_paciente.data[0]['pessoa_id']
    else:
        res_pessoa = supabase.table('pessoas').insert({
            'nome_completo': nome_paciente.strip(),
            'telefone': telefone_paciente.strip(),
            'status': 'Ativo'
        }).execute()
        
        paciente_oficial_id = res_pessoa.data[0]['id']
        
        supabase.table('pacientes').insert({
            'pessoa_id': paciente_oficial_id,
            'email': email_paciente.strip().lower()
        }).execute()

    resposta_agendamento = supabase.table('agendamentos').update({
        'paciente_id': paciente_oficial_id,
        'status': 'Confirmado'
    }).eq('id', agendamento_id).execute()
    
    return resposta_agendamento.data

def buscar_agendamentos_pendentes(medico_id: str):
    """
    Busca todas as solicitações vindas da internet (status = Pendente) para a caixa de entrada.
    """
    resposta = supabase.table('agendamentos').select(
        'id, data_hora_inicio, observacoes, nome_solicitante, email_solicitante, telefone_solicitante'
    ).eq('medico_id', medico_id).eq('status', 'Pendente').order('data_hora_inicio').execute()
    
    return resposta.data

def recusar_agendamento_web(agendamento_id: int):
    """
    Altera o status da solicitação web para 'Recusado', liberando o horário na agenda.
    """
    resposta = supabase.table('agendamentos').update({
        'status': 'Recusado'
    }).eq('id', agendamento_id).execute()
    
    return resposta.data

def buscar_dados_conversao_dashboard(medico_id: str) -> pd.DataFrame:
    """
    Busca os agendamentos e classifica a origem (Site/Web vs Interno) 
    para analise de conversao e captacao de leads.
    """
    resposta = supabase.table('agendamentos').select(
        'data_hora_inicio, status, criado_por_id'
    ).eq('medico_id', str(medico_id)).execute()
    
    dados = resposta.data
    
    if not dados:
        return pd.DataFrame(columns=['data', 'status', 'origem'])
        
    df = pd.DataFrame(dados)
    df['data'] = pd.to_datetime(df['data_hora_inicio']).dt.date
    df['origem'] = df['criado_por_id'].apply(
        lambda x: 'Site/Web' if pd.isna(x) or x is None else 'Recepcao/Interno'
    )
    
    return df[['data', 'status', 'origem']]

def cadastrar_paciente_rapido(nome: str, email: str, telefone: str) -> str:
    """
    Cadastra um paciente rapidamente pela tela de agendamento 
    ou retorna o ID existente se o e-mail ja constar no banco.
    """
    email_tratado = email.strip().lower()
    busca_paciente = supabase.table('pacientes').select('pessoa_id').eq('email', email_tratado).execute()
    
    if busca_paciente.data:
        return busca_paciente.data[0]['pessoa_id']
        
    res_pessoa = supabase.table('pessoas').insert({
        'nome_completo': nome.strip(),
        'telefone': telefone.strip(),
        'status': 'Ativo'
    }).execute()
    
    novo_id = res_pessoa.data[0]['id']
    
    supabase.table('pacientes').insert({
        'pessoa_id': novo_id,
        'email': email_tratado
    }).execute()
    
    return novo_id