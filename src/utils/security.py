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
        st.rerun()
        
    if "ultimo_acesso" in st.session_state:
        diferenca = (agora - st.session_state['ultimo_acesso']).total_seconds() / 60
        if diferenca > TIMEOUT_MINUTOS:
            for chave in list(st.session_state.keys()):
                del st.session_state[chave]
            
            st.warning(f"Sessão expirada por inatividade após {TIMEOUT_MINUTOS} minutos.")
            st.info("Redirecionando para a tela de login...")
            time.sleep(2.5)
            st.rerun()
    
    st.session_state['ultimo_acesso'] = agora

    if perfis_permitidos:
        perfil_atual = st.session_state.get("tipo_perfil")
        if perfil_atual not in perfis_permitidos:
            st.error(f"Acesso negado para o perfil: {perfil_atual}.")
            
            if perfil_atual == "Administrativo":
                if st.button("Ir para o Painel Administrativo"):
                    st.switch_page("src/ui/painelAdmin.py")
            st.stop()