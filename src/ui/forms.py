import streamlit as st
import time

# st.set_page_config(page_title="Faça o Login Para Acessar o P4 Doctors", layout="centered")

if "usuario_autenticado" not in st.session_state:
    st.session_state['usuario_autenticado'] = None
if 'tipo_perfil' not in st.session_state:
    st.session_state['tipo_perfil'] = None

def tela_login():
    st.title("P4 Doctors")
    st.markdown("Olá, seja bem-vindo! Faça login para acessar o sistema e aproveitar nossas funcionalidades!")

    with st.form("form_login"):
        usuario = st.text_input("Usuário", placeholder="Digite seu e-mail")
        senha = st.text_input("Senha", type="password", placeholder="Digite sua senha")
        botao_login = st.form_submit_button("Entrar", width="stretch")

        if botao_login:
            if usuario == "admin" and senha == "12345":
                st.success("Login efetuado")
                time.sleep(2)
                st.session_state['tipo_perfil'] = "Administrativo"
                st.session_state['usuario_autenticado'] = usuario
                st.rerun()
            elif usuario == "Bron" and senha == "6789":
                st.success("Login efetuado")
                time.sleep(2)
                st.session_state['tipo_perfil'] = "Médico"
                st.session_state['usuario_autenticado'] = usuario
                st.rerun()
            else:
                st.error("Usuário ou senha incorretos")

tela_login()
