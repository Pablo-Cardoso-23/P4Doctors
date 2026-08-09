import streamlit as st
import plotly.express as px
import pandas as pd
import datetime
from src.database.crud import buscar_dados_dashboard
from src.utils.security import verificar_acesso
from src.database.crud import buscar_medicos_vinculados

st.set_page_config(page_title="Dashboard", layout="wide")

if not st.session_state.get('usuario_autenticado') or not st.session_state.get('usuario_id'):
    st.switch_page("src/ui/forms.py")

verificar_acesso(perfis_permitidos=["Médico", "Administrativo"])

usuario_logado_id = st.session_state.get('usuario_id')
tipo_perfil = st.session_state.get('tipo_perfil')

medico_alvo_id = None

if tipo_perfil in ['Secretária', 'Administrativo']:
    st.info("Modo Equipe: Selecione a agenda do profissional vinculado.")
    
    lista_medicos = buscar_medicos_vinculados(usuario_logado_id)
    
    if not lista_medicos:
        st.error("Você ainda não possui vínculo com nenhum médico. Contate o administrador.")
        st.stop() 

    medico_selecionado = st.selectbox(
        "Profissional", 
        options=lista_medicos, 
        format_func=lambda m: m["nome"]
    )

    medico_alvo_id = medico_selecionado["id"]
else:
    medico_alvo_id = usuario_logado_id

def criar_card(titulo, valor, coluna):
    with coluna:
        container = st.container(border=True)
        container.markdown(f"<p style='text-align: center; font-size: 14px; color: #a5a5a5; margin-bottom: 0px;'>{titulo}</p>", unsafe_allow_html=True)
        container.markdown(f"<h3 style='text-align: center; margin-top: 0px;'>{valor}</h3>", unsafe_allow_html=True)

st.title("Dashboard de Faturamento e Produtividade")
st.markdown("Acompanhe suas métricas financeiras e volume de atendimentos.")
st.markdown("---")

df = buscar_dados_dashboard(medico_alvo_id)

if df.empty:
    st.info("Nenhum atendimento registrado ainda para exibir no dashboard.")
    st.stop()

df['data'] = pd.to_datetime(df['data']).dt.date
col_f_ano, col_f_mes, col_f_local, col_f_tipo = st.columns(4)
anos_disponiveis = sorted(list(set(d.year for d in df['data'])), reverse=True)
ano_atual = datetime.date.today().year
index_ano = anos_disponiveis.index(ano_atual) if ano_atual in anos_disponiveis else 0

with col_f_ano:
    ano_selecionado = st.selectbox("Ano", anos_disponiveis, index=index_ano)

dicionario_meses = {
    "Todos": 0, "Janeiro": 1, "Fevereiro": 2, "Março": 3, "Abril": 4, 
    "Maio": 5, "Junho": 6, "Julho": 7, "Agosto": 8, "Setembro": 9, 
    "Outubro": 10, "Novembro": 11, "Dezembro": 12
}

with col_f_mes:
    mes_atual_nome = list(dicionario_meses.keys())[datetime.date.today().month]
    index_mes = list(dicionario_meses.keys()).index(mes_atual_nome) if ano_selecionado == ano_atual else 0
    
    mes_selecionado_nome = st.selectbox("Mês", list(dicionario_meses.keys()), index=index_mes)
    num_mes_selecionado = dicionario_meses[mes_selecionado_nome]

with col_f_local:
    filtro_local = st.multiselect("Local", df['local'].unique(), default=df['local'].unique())

with col_f_tipo:
    filtro_tipo_atendimento = st.multiselect("Tipo de Atendimento", df['tipo'].unique(), default=df['tipo'].unique())

mask = (
    (pd.to_datetime(df['data']).dt.year == ano_selecionado) &
    (df['local'].isin(filtro_local)) &
    (df['tipo'].isin(filtro_tipo_atendimento))
)

if num_mes_selecionado != 0:
    mask = mask & (pd.to_datetime(df['data']).dt.month == num_mes_selecionado)

df_filtrado = df[mask]

st.markdown("---")

if df_filtrado.empty:
    st.warning("Nenhum dado encontrado para os filtros selecionados.")
    st.stop()

faturamento_total = df_filtrado['valor'].sum()
volume_atendimentos = len(df_filtrado)
ticket_medio = faturamento_total / volume_atendimentos if volume_atendimentos > 0 else 0

col_kpi1, col_kpi2, col_kpi3 = st.columns(3)

valor_faturamento = f"R$ {faturamento_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
valor_ticket_medio = f"R$ {ticket_medio:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

criar_card("FATURAMENTO TOTAL", valor_faturamento, col_kpi1)
criar_card("VOLUME DE ATENDIMENTOS", str(volume_atendimentos), col_kpi2)
criar_card("TICKET MÉDIO", valor_ticket_medio, col_kpi3)

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

df_tempo = df_filtrado.groupby('data')['valor'].sum().reset_index()
df_tempo = df_tempo.sort_values('data')
df_tempo['data_formatada'] = pd.to_datetime(df_tempo['data']).dt.strftime('%d/%m/%Y')

fig_tempo = px.line(
    df_tempo, 
    x='data_formatada', 
    y='valor', 
    color_discrete_sequence=['#FF4B4B'], 
    markers=True
)
fig_tempo.update_layout(
    xaxis_title='Data', 
    yaxis_title="Faturamento (R$)", 
    margin=dict(l=0, r=0, t=30, b=0)
)
st.plotly_chart(fig_tempo, use_container_width=True)