import streamlit as st

if "logged_in" not in st.session_state:
    st.session_state['logged_in'] = False
if "usuario_autenticado" not in st.session_state:
    st.session_state['usuario_autenticado'] = ""

pagina_login = st.Page("src/ui/forms.py", title="P4 Doctors - Login")
pagina_inicial = st.Page("src/ui/menu.py", title="Menu")
pagina_dashboard = st.Page("src/ui/dashboard.py", title="Dashboards")
pagina_criar_relatorio = st.Page("src/ui/criarRelatorio.py", title="Novo Relatorio")
pagina_criar_conta = st.Page("src/ui/criarConta.py", title="Criar Conta")

if st.session_state['logged_in']:
    with st.sidebar:
        st.markdown(f"**Dr(a). {st.session_state['usuario_autenticado']}**")
        st.markdown("---")

        if st.button("Sair da Conta", use_container_width=True):
            st.session_state['logged_in'] = False
            st.session_state['usuario_autenticado'] = ""

            st.rerun()
            st.switch_page(pagina_login)

    pg = st.navigation(
        {
            "Página Inicial": [pagina_inicial],
            "Dashboards": [pagina_dashboard],
            "Registrar Relatório": [pagina_criar_relatorio],
            "Conta": [pagina_criar_conta],
        }
    )
else:
    pg = st.navigation([pagina_login])

pg.run()
