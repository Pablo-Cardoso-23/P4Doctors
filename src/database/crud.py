import streamlit as st
import pandas as pd
from supabase import create_client, Client
import uuid
from datetime import datetime

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