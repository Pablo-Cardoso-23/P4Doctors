import streamlit as st
import pandas as pd
import datetime

st.set_page_config(page_title="P4 Doctors - Meus Relatórios", layout="wide")

st.title("Histórico de Atendimentos")
st.markdown("Consulte, filtre e revise todos os relatórios, consultas e plantões registrados no sistema.")
st.markdown("---")

st.subheader("Filtros de Busca")
col_filtro1, col_filtro2, col_filtro3 = st.columns(3)

with col_filtro1:
    filtro_data = st.date_input("Período", value=(datetime.date.today() - datetime.timedelta(days=7), datetime.date.today()))
with col_filtro2:
    filtro_tipo = st.selectbox("Tipo de Registro", ["Todos", "Primeira Consulta", "Retorno", "Plantão", "Ecocardiograma"])
with col_filtro3:
    filtro_busca = st.text_input("Buscar por Paciente", placeholder="Digite o nome...")

st.markdown("---")

st.subheader("Relatórios Registrados")

# Dados fictícios para simular a interface
dados_simulados = {
    "Data": ["07/05/2026", "06/05/2026", "05/05/2026", "04/05/2026"],
    "Paciente/Serviço": ["Anthony Silva", "Plantão 12h", "Maria Oliveira", "Leonardo Souza"],
    "Tipo": ["Primeira Consulta", "Plantão", "Ecocardiograma", "Retorno"],
    "Local": ["Hospital de Base", "Hospital Anchieta", "Clínica P4", "Hospital das Clínicas"],
    "Valor (R$)": [350.00, 1200.00, 450.00, 200.00],
    "Status": ["Registrado", "Registrado", "Registrado", "Pendente Edição"]
}

df_historico = pd.DataFrame(dados_simulados)

st.dataframe(
    df_historico,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Valor (R$)": st.column_config.NumberColumn(format="R$ %.2f")
    }
)

st.markdown("---")

@st.cache_data
def converter_para_csv(df):
    return df.to_csv(index=False).encode('utf-8')

csv_dados = converter_para_csv(df_historico)

col_acao1, col_acao2, col_acao3 = st.columns([2, 1, 1])
with col_acao1:
    st.info("Para ver o relatório clínico completo ou editar um registro, selecione a opção ao lado.")
with col_acao2:
    st.download_button(
        label="Exportar para CSV",
        data=csv_dados,
        file_name=f"historico_atendimentos_{datetime.date.today()}.csv",
        mime="text/csv",
        use_container_width=True
    )
with col_acao3:
    st.button("Visualizar Detalhes", type="primary", use_container_width=True)
