import streamlit as st
import time
import bcrypt
from datetime import datetime, timedelta
from supabase import create_client, Client
from src.database.crud import atualizar_senha_usuario

@st.cache_resource
def get_supabase() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = get_supabase()

@st.cache_resource
def obter_controle_global():
    return {
        "tentativas": {},
        "bloqueios": {}
    }

controle_acesso = obter_controle_global()

# Hash Bcrypt pré-calculado para a Operação Fantasma (Dummy)
DUMMY_HASH = b"$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj2DAN480uPe"

def autenticar_usuario_db(email_fornecido, senha_fornecida):
    """
    Verifica as credenciais no PostgreSQL via Supabase.
    Retorna (perfil, nome_completo, usuario_id, data_ultima_troca_senha) ou (None, None, None, None)
    """
    email_normalizado = email_fornecido.strip().lower()
    senha_bytes = senha_fornecida.encode('utf-8')
    res_medico = supabase.table('medicos').select('pessoa_id, senha_hash, data_ultima_troca_senha, pessoas!pessoa_id(nome_completo, status)').eq('email', email_normalizado).execute()
    
    if res_medico.data:
        dados = res_medico.data[0]
        if dados.get('pessoas', {}).get('status') == 'Inativo':
            return None, None, None, None
        if bcrypt.checkpw(senha_bytes, dados['senha_hash'].encode('utf-8')):
            return 'Médico', dados['pessoas']['nome_completo'], dados['pessoa_id'], dados.get('data_ultima_troca_senha')
        return None, None, None, None

    res_equipe = supabase.table('equipe_apoio').select('pessoa_id, papel, senha_hash, data_ultima_troca_senha, pessoas!pessoa_id(nome_completo, status)').eq('email', email_normalizado).execute()
    
    if res_equipe.data:
        dados = res_equipe.data[0]
        if dados.get('pessoas', {}).get('status') == 'Inativo':
            return None, None, None, None
        if bcrypt.checkpw(senha_bytes, dados['senha_hash'].encode('utf-8')):
            papel = dados.get('papel', 'Equipe de Apoio')
            perfil = 'Administrativo' if papel == 'Administrativo' else papel
            return perfil, dados['pessoas']['nome_completo'], dados['pessoa_id'], dados.get('data_ultima_troca_senha')
        return None, None, None, None

    bcrypt.checkpw(senha_bytes, DUMMY_HASH)
    return None, None, None, None

if st.session_state.get('forcing_password_change'):
    st.warning(st.session_state.get('motivo_troca', 'É necessário redefinir sua senha.'))
    st.subheader("Redefinição de Senha Obrigatória")
    
    with st.form("form_troca_obrigatoria"):
        nova_senha = st.text_input("Nova Senha", type="password")
        confirma_senha = st.text_input("Confirme a Nova Senha", type="password")
        botao_trocar = st.form_submit_button("Alterar Senha e Acessar", type="primary", use_container_width=True)
        
        if botao_trocar:
            if len(nova_senha) < 6:
                st.error("A senha deve ter pelo menos 6 caracteres.")
            elif nova_senha != confirma_senha:
                st.error("As senhas não coincidem. Tente novamente.")
            else:
                try:
                    atualizar_senha_usuario(
                        pessoa_id=st.session_state['temp_id'], 
                        perfil=st.session_state['temp_perfil'], 
                        senha_texto_claro=nova_senha
                    )
                    st.success("Senha alterada com sucesso! Inicializando ambiente seguro...")
                    st.session_state['usuario_autenticado'] = st.session_state['temp_nome']
                    st.session_state['tipo_perfil'] = st.session_state['temp_perfil']
                    st.session_state['usuario_id'] = st.session_state['temp_id']
                    st.session_state['ultimo_acesso'] = datetime.now() 
                    
                    del st.session_state['forcing_password_change']
                    del st.session_state['temp_id']
                    del st.session_state['temp_perfil']
                    del st.session_state['temp_nome']
                    del st.session_state['motivo_troca']
                    
                    time.sleep(1)
                    st.rerun() 
                except Exception as e:
                    st.error(f"Erro ao atualizar a senha: {e}")
                    
    st.stop()

st.title("Acesso ao Sistema")
st.markdown("Insira suas credenciais corporativas para acessar o painel.")
st.markdown("---")

with st.form("form_login"):
    usuario_email = st.text_input("E-mail Profissional").strip()
    senha = st.text_input("Senha", type="password")
    botao_entrar = st.form_submit_button("Entrar", type="primary", use_container_width=True)

    if botao_entrar:
        time.sleep(1.5) 

        if not usuario_email or not senha:
            st.warning("Preencha todos os campos obrigatórios.")
            st.stop()

        bloqueado_ate = controle_acesso["bloqueios"].get(usuario_email)
        
        if bloqueado_ate:
            if datetime.now() < bloqueado_ate:
                tempo_restante = (bloqueado_ate - datetime.now()).seconds
                st.error(f"Conta temporariamente bloqueada por segurança. Tente novamente em {tempo_restante} segundos.")
                st.stop()
            else:
                controle_acesso["bloqueios"].pop(usuario_email, None)
                controle_acesso["tentativas"][usuario_email] = 0

        perfil, nome_completo, usuario_id, data_troca_banco = autenticar_usuario_db(usuario_email, senha)

        if perfil:
            controle_acesso["tentativas"][usuario_email] = 0
            precisa_mudar = False
            motivo_troca = ""
            
            if data_troca_banco is None:
                precisa_mudar = True
                motivo_troca = "Este é o seu primeiro acesso. Por segurança, você precisa definir uma senha própria."
            else:
                try:
                    data_troca_obj = datetime.fromisoformat(data_troca_banco.replace("Z", ""))
                    dias_passados = (datetime.now() - data_troca_obj).days
                    
                    if dias_passados >= 90:
                        precisa_mudar = True
                        motivo_troca = f"Sua senha expirou (última troca há {dias_passados} dias). A política de segurança exige a troca a cada 90 dias."
                except Exception:
                    precisa_mudar = True
                    motivo_troca = "A política de segurança exige a atualização da sua senha atual."
                    
            if precisa_mudar:
                st.session_state['forcing_password_change'] = True
                st.session_state['temp_nome'] = nome_completo
                st.session_state['temp_perfil'] = perfil
                st.session_state['temp_id'] = usuario_id
                st.session_state['motivo_troca'] = motivo_troca
                st.rerun()
            else:
                st.session_state['usuario_autenticado'] = nome_completo
                st.session_state['tipo_perfil'] = perfil
                st.session_state['usuario_id'] = usuario_id
                st.session_state['ultimo_acesso'] = datetime.now() 
                
                st.success("Autenticação bem-sucedida. Inicializando ambiente seguro...")
                time.sleep(1)
                st.rerun()
        else:
            tentativas_atuais = controle_acesso["tentativas"].get(usuario_email, 0) + 1
            controle_acesso["tentativas"][usuario_email] = tentativas_atuais
            
            if tentativas_atuais >= 3:
                controle_acesso["bloqueios"][usuario_email] = datetime.now() + timedelta(minutes=3)
                st.error("Múltiplas tentativas falhas. Acesso bloqueado globalmente por 3 minutos.")
            else:
                st.error("Credenciais inválidas. Verifique seu e-mail e senha.")

st.markdown("<br><hr><p style='text-align: center; color: var(--text-color); opacity: 0.5; font-size: 0.9rem;'>&copy; 2026 P4 Health. Todos os direitos reservados.</p>", unsafe_allow_html=True)