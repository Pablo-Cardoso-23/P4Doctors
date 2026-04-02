import streamlit as st
import datetime
import time

def verificar_acesso(perfis_permitidos=None):
    """
    Valida a aplicação, timeout de sessão e autorização (RBAC).
    """
    TIMEOUT_MINUTOS = 30
    agora = datetime.datetime.now()

    if not st.session_state.get("usuario_autenticado"):
        st.switch_page("src/ui/forms.py")
    if "ultimo_acesso" in st.session_state:
        diferenca = (agora - st.session_state['ultimo_acesso']).total_seconds() / 60
        if diferenca > TIMEOUT_MINUTOS:
            for chave in list(st.session_state.keys()):
                del st.session_state[chave]
            st.error(f"Sessão expirada após {TIMEOUT_MINUTOS} minutos.")
            time.sleep(3)
            st.switch_page("src/ui/forms.py")
    
    st.session_state['ultimo_acesso'] = agora

    if perfis_permitidos:
        perfil_atual = st.session_state.get("tipo_perfil")
        if perfil_atual not in perfis_permitidos:
            st.error(f"Acesso negado para o perfil: {perfil_atual}.")
            if perfil_atual == "Administrativo":
                if st.button("Ir para o Painel Administrativo"):
                    st.switch_page("src/ui/painelAdmin.py")
            st.stop()
