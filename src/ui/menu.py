import streamlit as st
import datetime

if "usuario_autenticado" not in st.session_state or not st.session_state['usuario_autenticado']:
    st.warning("Por favor, faça o login para acessar o sistema.")
    st.stop()

st.title("P4 Doctors - Central de Profissional")
st.markdown(f"#### Bem-vindo(a), Dr(a). {st.session_state['usuario_autenticado']}")
st.markdown("Utilize os atalhos abaixo para navegar pelo sistema sistema ou utilize o menu lateral.")

st.markdown("---")

st.markdown("Acesso Rápido")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("#### Agenda")
    st.markdown("Gerencie seus horários e plantões.")
    if st.button("Abrir Agenda", use_container_width=True):
        st.switch_page("src/ui/agenda.py")
with col2:
    st.markdown("#### Novo Relatório")
    st.markdown("Registre consultas e faturamentos.")
    if st.button("Criar Registro", type="primary", use_container_width=True):
        st.switch_page("src/ui/criarRelatorio.py")
with col3:
    st.markdown("#### Dashboards")
    st.markdown("Analise seus ganhos e volume.")
    if st.button("Ver Métricas", use_container_width=True):
        st.switch_page("src/ui/dashboard.py")

st.markdown("---")

st.markdown("#### Resumo de Hoje")
hoje = datetime.datetime.now().strftime("%d/%m/%Y")

st.info(f"Data: {hoje}. Você possui N consultas agendadas e N platão pendente de registro no sistema.")
