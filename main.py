import streamlit as st
from supabase import create_client, Client

@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

if "usuario_autenticado" not in st.session_state:
    st.session_state['usuario_autenticado'] = None
if 'tipo_perfil' not in st.session_state:
    st.session_state['tipo_perfil'] = None

supabase: Client = init_connection()

pagina_sobre = st.Page("src/ui/sobre.py", title="P4 Doctors - Sobre")
pagina_solicitar_acesso = st.Page("src/ui/solicitarAcesso.py", title="Solicitar Acesso")
pagina_login = st.Page("src/ui/forms.py", title="P4 Doctors - Login")
pagina_agendar_consulta = st.Page("src/ui/agendar_consulta.py", title="Agendar Consulta")

pagina_inicial = st.Page("src/ui/menu.py", title="Menu")
pagina_dashboard = st.Page("src/ui/dashboard.py", title="Dashboards")
pagina_agendamentos = st.Page("src/ui/agenda.py", title="Agendamentos")
pagina_criar_relatorio = st.Page("src/ui/criarRelatorio.py", title="Novo Relatorio")
pagina_meus_relatorios = st.Page("src/ui/meusRelatorios.py", title="Meus Relatórios")
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
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()

        pg = st.navigation(
            {
                "Página Inicial": [pagina_inicial],
                "Dashboards": [pagina_dashboard],
                "Agendamentos": [pagina_agendamentos],
                "Registrar Relatório": [pagina_criar_relatorio],
                "Meus Relatórios": [pagina_meus_relatorios],
            }
        )
else:
    pg = st.navigation(
        {
            "Portal do Paciente": [pagina_agendar_consulta],
            "Institucional": [pagina_sobre, pagina_login, pagina_solicitar_acesso]
        }
    )

pg.run()