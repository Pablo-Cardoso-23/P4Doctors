import streamlit as st
from supabase import create_client, Client
import uuid
from datetime import datetime

# 1. FUNÇÃO PARA PEGAR A CONEXÃO COM O SUPABASE
@st.cache_resource
def obter_conexao_supabase() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = obter_conexao_supabase()

def buscar_agendamentos(medico_id: str) -> list:
    """
    Busca os agendamentos no Supabase e faz um Join aninhado para pegar o nome.
    """
    resposta = supabase.table('agendamentos').select(
        'id, tipo_evento, data_hora_inicio, data_hora_fim, pacientes(pessoas(nome_completo))'
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
            "color": cores_por_tipo.get(tipo_evento, "#333333")
        })
        
    return eventos_calendario


def buscar_pacientes_para_select() -> list:
    """
    Busca os pacientes no banco para popular o selectbox do formulário.
    """
    # 1. Mudamos a busca de 'id' para 'pessoa_id'
    resposta = supabase.table('pacientes').select('pessoa_id, pessoas(nome_completo)').execute()
    
    # A primeira opção sempre será o Bloqueio/Plantão (sem paciente vinculado)
    lista_formatada = [{"id": None, "nome": "Bloqueio/Plantão"}]
    
    for linha in resposta.data:
        dados_pessoa = linha.get('pessoas')
        nome_paciente = dados_pessoa.get('nome_completo') if dados_pessoa else "Sem Nome"
        
        lista_formatada.append({
            # 2. Pegamos o valor usando 'pessoa_id', mas mantemos a chave como 'id' 
            # para o selectbox do Streamlit continuar funcionando perfeitamente
            "id": linha.get('pessoa_id'), 
            "nome": nome_paciente
        })
        
    return lista_formatada


# 3. FUNÇÃO DEFINITIVA DE INSERÇÃO (INSERT)
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
    """
    Salva um novo agendamento na tabela 'agendamentos' do Supabase.
    """
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