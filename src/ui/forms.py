import streamlit as st
import time
import bcrypt
from datetime import datetime, timedelta
from supabase import create_client, Client

@st.cache_resource
def get_supabase() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = get_supabase()

@st.cache_resource
def obter_controle_global():
    return {
        "tentativas": {}, # {"usuario": int}
        "bloqueios": {} #{"usuario": datetime}
    }

controle_acesso = obter_controle_global()

# Hash Bcrypt pré-calculado para a Operação Fantasma (Dummy)
# Custo 12: Garante um atraso computacional idêntico a um usuário real
DUMMY_HASH = b"$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj2DAN480uPe"

def autenticar_usuario_db(email_fornecido, senha_fornecida):
    """
    Verifica as credenciais diretamente no PostgreSQL via Supabase.
    Retorna (perfil, nome_completo, usuario_id) ou (None, None, None)
    """
    email_normalizado = email_fornecido.strip().lower()
    senha_bytes = senha_fornecida.encode('utf-8')

    # 1. Busca em Médicos
    res_medico = supabase.table('medicos').select('pessoa_id, senha_hash, pessoas!pessoa_id(nome_completo, status)').eq('email', email_normalizado).execute()
    
    if res_medico.data:
        dados = res_medico.data[0]
        if dados.get('pessoas', {}).get('status') == 'Inativo':
            return None, None, None # Usuário desativado
        if bcrypt.checkpw(senha_bytes, dados['senha_hash'].encode('utf-8')):
            return 'Médico', dados['pessoas']['nome_completo'], dados['pessoa_id']
        return None, None, None

    # 2. Busca em Equipe de Apoio (se não for médico)
    res_equipe = supabase.table('equipe_apoio').select('pessoa_id, papel, senha_hash, pessoas!pessoa_id(nome_completo, status)').eq('email', email_normalizado).execute()
    
    if res_equipe.data:
        dados = res_equipe.data[0]
        if dados.get('pessoas', {}).get('status') == 'Inativo':
            return None, None, None
        if bcrypt.checkpw(senha_bytes, dados['senha_hash'].encode('utf-8')):
            papel = dados.get('papel', 'Equipe de Apoio')
            perfil = 'Administrativo' if papel == 'Administrativo' else papel
            return perfil, dados['pessoas']['nome_completo'], dados['pessoa_id']
        return None, None, None

    # 3. Dummy Check (Se o e-mail não existir em nenhuma tabela)
    # Processa o hash fictício para manter o tempo de resposta semelhante e evitar enumeração de usuários
    bcrypt.checkpw(senha_bytes, DUMMY_HASH)
    
    return None, None, None

# --- INTERFACE DE LOGIN ---
st.title("Acesso ao Sistema")
st.markdown("Insira suas credenciais corporativas para acessar o painel.")
st.markdown("---")

with st.form("form_login"):
    usuario_email = st.text_input("E-mail Profissional").strip()
    senha = st.text_input("Senha", type="password")
    botao_entrar = st.form_submit_button("Entrar", type="primary", use_container_width=True)

    if botao_entrar:
        # Tarpitting Universal
        time.sleep(1.5) 

        if not usuario_email or not senha:
            st.warning("Preencha todos os campos obrigatórios.")
            st.stop()

        # 1. Verificação do Lockout Global
        bloqueado_ate = controle_acesso["bloqueios"].get(usuario_email)
        
        if bloqueado_ate:
            if datetime.now() < bloqueado_ate:
                tempo_restante = (bloqueado_ate - datetime.now()).seconds
                st.error(f"Conta temporariamente bloqueada por segurança. Tente novamente em {tempo_restante} segundos.")
                st.stop()
            else:
                controle_acesso["bloqueios"].pop(usuario_email, None)
                controle_acesso["tentativas"][usuario_email] = 0

        # 2. Processamento Criptográfico e Busca no Supabase
        perfil, nome_completo, usuario_id = autenticar_usuario_db(usuario_email, senha)

        if perfil:
            # Fluxo de Sucesso
            controle_acesso["tentativas"][usuario_email] = 0
            
            # Variáveis que o main.py espera para liberar a navegação
            st.session_state['usuario_autenticado'] = nome_completo
            st.session_state['tipo_perfil'] = perfil
            st.session_state['usuario_id'] = usuario_id
            st.session_state['ultimo_acesso'] = datetime.now() 
            
            st.success("Autenticação bem-sucedida. Inicializando ambiente seguro...")
            time.sleep(1)
            st.rerun()
        else:
            # Fluxo de Falha
            tentativas_atuais = controle_acesso["tentativas"].get(usuario_email, 0) + 1
            controle_acesso["tentativas"][usuario_email] = tentativas_atuais
            
            if tentativas_atuais >= 3:
                controle_acesso["bloqueios"][usuario_email] = datetime.now() + timedelta(minutes=3)
                st.error("Múltiplas tentativas falhas. Acesso bloqueado globalmente por 3 minutos.")
            else:
                st.error("Credenciais inválidas. Verifique seu e-mail e senha.")