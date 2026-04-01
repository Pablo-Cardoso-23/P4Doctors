import streamlit as st

if "usuario_autenticado" not in st.session_state:
    st.session_state['usuario_autenticado'] = None
if 'tipo_perfil' not in st.session_state:
    st.session_state['tipo_perfil'] = None

pagina_sobre = st.Page("src/ui/sobre.py", title="P4 Doctors - Sobre")
pagina_solicitar_acesso = st.Page("src/ui/solicitarAcesso.py", title="Solicitar Acesso")
pagina_login = st.Page("src/ui/forms.py", title="P4 Doctors - Login")
pagina_inicial = st.Page("src/ui/menu.py", title="Menu")
pagina_dashboard = st.Page("src/ui/dashboard.py", title="Dashboards")
pagina_agendamentos = st.Page("src/ui/agenda.py", title="Agendamentos")
pagina_criar_relatorio = st.Page("src/ui/criarRelatorio.py", title="Novo Relatorio")
pagina_admin = st.Page("src/ui/painelAdmin.py", title="Painel Administrativo")

if st.session_state['usuario_autenticado']:
    if st.session_state['tipo_perfil'] == 'Administrativo':
        pg = st.navigation({
            "Gestão de Sistema": [pagina_admin]
        })
    else:
        with st.sidebar:
            if st.session_state['tipo_perfil'] == 'Médico':
                st.markdown(f"**Dr(a). {st.session_state['usuario_autenticado']}**")
            else:
                st.markdown(f"**{st.session_state['usuario_autenticado']}**")
                
            st.markdown(f"**Tipo de Usuário: {st.session_state['tipo_perfil']}**")
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
                "Agendamentos": [pagina_agendamentos],
                "Registrar Relatório": [pagina_criar_relatorio],
            }
        )
else:
    pg = st.navigation([pagina_sobre, pagina_login, pagina_solicitar_acesso])

pg.run()
