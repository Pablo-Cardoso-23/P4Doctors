import streamlit as st
import time
import datetime
from src.utils.security import verificar_acesso

TIMEOUT_MINUTOS = 30
agora = datetime.datetime.now()

if "usuario_autenticado" not in st.session_state or not st.session_state['usuario_autenticado']:
    st.switch_page("src/ui/forms.py")

verificar_acesso(perfis_permitidos=["Médico", "Secretária"])

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
data_atual = agora.strftime("%d/%m/%Y")

st.info(f"Data: {data_atual}. Você possui N consultas agendadas e N platão pendente de registro no sistema.")
