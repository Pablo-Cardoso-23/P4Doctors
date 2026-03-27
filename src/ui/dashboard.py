import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta

st.title("Dashboard de Faturamento e Produtividade")
st.markdown("Acompanhe suas métricas financeiras e volume de atendimentos.")

st.markdown("---")

@st.cache_data
def dados_testes():
    np.random.seed(42)
    
    datas = [datetime.today() - timedelta(days=i) for i in range(30)]
    locais = ["Hospital das Clínicas", "Hospital de Base", "Hospital Anchieta", "Clínica Particular"]
    tipos = ["Primeira Consulta", "Retorno", "Procedimento", "Plantão 12h"]

    dados = []

    for _ in range(150):
        dados.append({
            "data": np.random.choice(datas),
            "local": np.random.choice(locais),
            "tipo": np.random.choice(tipos),
            "valor": np.random.uniform(150.0, 1500.0)
        })
    df = pd.DataFrame(dados)

    df.loc[df['tipo'] == 'Retorno' 'valor'] = 0.0
    df.loc[df['tipo'] == 'Plantão 12h' 'valor'] = 1200.0
    
    return df

df = dados_testes()

col_f1, col_f2, col_f3 = st.columns(3)

with col_f1:
    mes_selecionado = st.selectbox("Período (Mês)", ["Mês Atual", "Mês Anterior"])
with col_f2:
    filtro_local = st.multiselect("Filtrar por Local", df['local'].unique(), default=df['local'].unique())
with col_f3:
    filtro_tipo_atendimento = st.multiselect("Filtrar por Tipo de Atendimento", df['tipo'].unique(), default=df['tipo'].unique())

df_filtrado = df[(df['local'].isin(filtro_local)) & (df['tipo'].isin(filtro_tipo_atendimento))]

st.markdown("---")

faturamento_total = df_filtrado['valor'].sum()
volume_atendimentos = len(df_filtrado)
ticker_medio = faturamento_total / volume_atendimentos if volume_atendimentos > 0 else 0

col_kpi1, col_kpi2, col_kpi3 = st.columns(3)

with col_kpi1:
    st.metric("Faturamento Total (R$)", f"R$ {faturamento_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
with col_kpi2:
    st.metric("Volume de Atendimentos", f"{volume_atendimentos}")
with col_kpi3:
    st.metric("Ticket Médio (R$)", f"R$ {ticker_medio:.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

st.markdown("---")

col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    st.markdown("#### Faturamento por Local")
    df_local = df_filtrado.groupby('local')['valor'].sum().reset_index()
    fig_local = px.bar(df_local, x='local', y='valor', color_discrete_sequence=['#FF4B4B'])
    fig_local.update_layout(xaxis_title="", yaxis_title="Valor (R$)", margin=dict(l=0, r=0, t=30, b=0))
    st.plotly_chart(fig_local, use_container_width=True)
with col_graf2:
    st.markdown("#### Volume por Tipo de Atendimento")
    df_tipo = df_filtrado.groupby('tipo').size().reset_index(name='contagem')
    fig_tipo = px.bar(df_tipo, x='tipo', y='contagem', color_discrete_sequence=['#FF4B4B'])
    fig_tipo.update_layout(xaxis_title="", yaxis_title="Quantidade", margin=dict(l=0, r=0, t=30, b=0))
    st.plotly_chart(fig_tipo, use_container_width=True)

st.write("")

st.markdown("#### Evolução do Faturamento Diário")
df_tempo = df_filtrado.groupby(df_filtrado['data'].dt.date)['valor'].sum().reset_index()
df_tempo = df_tempo.sort_values('data')

fig_tempo = px.line(df_tempo, x='data', y='valor', color_discrete_sequence=['#FF4B4B'], markers=True)
fig_tempo.update_layout(xaxis_title='Data', yaxis_title="Faturamento (R$)", margin=dict(l=0, r=0, t=30, b=0))
st.plotly_chart(fig_tempo, use_container_width=True)
