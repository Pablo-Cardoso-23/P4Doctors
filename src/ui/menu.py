import streamlit as st

st.title("P4 Doctors")
st.markdown(f"#### Bem-Vindo, {st.session_state['usuario_autenticado']}")

botao_dashboard = st.button("Acessar Dashboards")
botao_criar_relatorio = st.button("Criar Relatório")
