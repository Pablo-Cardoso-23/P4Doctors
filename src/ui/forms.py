import streamlit as st
import time
import bcrypt
from datetime import datetime, timedelta

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

def verificar_credenciais(usuario_fornecido, senha_fornecida):
    """
    Verifica as credenciais usando st.secrets
    Utiliza um dummy check para mitigar Timing Attacks.
    """
    senha_bytes = senha_fornecida.encode('utf-8')

    try:
        usuarios_validos = st.secrets["usuarios"]
    except KeyError:
        usuarios_validos = {}
    
    usuario_existe = usuario_fornecido in usuarios_validos

    if usuario_existe:
        senha_alvo = usuarios_validos[usuario_fornecido]["senha_hash"].encode('utf-8')
        perfil_alvo = usuarios_validos[usuario_fornecido]["perfil"]
    else:
        senha_alvo = DUMMY_HASH
        perfil_alvo = None

    try:
        senhas_conferem = bcrypt.checkpw(senha_bytes, senha_alvo)
    except ValueError:
        senhas_conferem = False
    if usuario_existe and senhas_conferem:
        return perfil_alvo
    return None

st.title("Acesso ao Sistema")
st.markdown("Insira suas credenciais corporativas para acessar o painel.")
st.markdown("---")

try:
    usuarios_carregados = list(st.secrets["usuarios"].keys())
    st.info(f"STATUS DO COFRE: Sucesso. Usuários carregados: {usuarios_carregados}")
except Exception as e:
    st.error("STATUS DO COFRE: Falha. O arquivo .streamlit/secrets.toml não foi encontrado ou está vazio.")

with st.form("form_login"):
    usuario = st.text_input("Usuário").strip()
    senha = st.text_input("Senha", type="password")
    botao_entrar = st.form_submit_button("Entrar", type="primary", use_container_width=True)

    if botao_entrar:
        # Tarpitting Universal: Atraso intencional de rede para mitigar scanners rápidos
        time.sleep(1.5) 

        if not usuario or not senha:
            st.warning("Preencha todos os campos obrigatórios.")
            st.stop()

        # 1. Verificação do Lockout Global
        bloqueado_ate = controle_acesso["bloqueios"].get(usuario)
        
        if bloqueado_ate:
            if datetime.now() < bloqueado_ate:
                tempo_restante = (bloqueado_ate - datetime.now()).seconds
                st.error(f"Conta temporariamente bloqueada por segurança. Tente novamente em {tempo_restante} segundos.")
                st.stop()
            else:
                controle_acesso["bloqueios"].pop(usuario, None)
                controle_acesso["tentativas"][usuario] = 0

        # 2. Processamento Criptográfico Seguro
        perfil = verificar_credenciais(usuario, senha)

        if perfil:
            # Fluxo de Sucesso: Limpa o estado global deste usuário específico
            controle_acesso["tentativas"][usuario] = 0
            
            # Registra apenas os dados operacionais na sessão local do navegador legítimo
            st.session_state['usuario_autenticado'] = usuario
            st.session_state['tipo_perfil'] = perfil
            st.session_state['ultimo_acesso'] = datetime.now() 
            
            st.success("Autenticação bem-sucedida. Inicializando ambiente seguro...")
            time.sleep(1)
            st.rerun()
        else:
            # Fluxo de Falha: Registra a tentativa no dicionário da memória do servidor
            tentativas_atuais = controle_acesso["tentativas"].get(usuario, 0) + 1
            controle_acesso["tentativas"][usuario] = tentativas_atuais
            
            if tentativas_atuais >= 3:
                controle_acesso["bloqueios"][usuario] = datetime.now() + timedelta(minutes=3)
                st.error("Múltiplas tentativas falhas. Acesso bloqueado globalmente por 3 minutos.")
            else:
                st.error("Credenciais inválidas. Verifique seu usuário e senha.")