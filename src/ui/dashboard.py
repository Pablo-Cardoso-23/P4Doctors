import streamlit as st
import plotly.express as px
import pandas as pd
import datetime
from src.database.crud import buscar_dados_dashboard, buscar_dados_conversao_dashboard, buscar_medicos_vinculados
from src.utils.security import verificar_acesso

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

st.title("Painel Gerencial e Produtividade")
st.markdown("Acompanhe mátricas financeiras e análise a captação de pacientes.")
st.markdown("---")

df_faturamento = buscar_dados_dashboard(medico_alvo_id)
df_conversao = buscar_dados_conversao_dashboard(medico_alvo_id)

if df_faturamento.empty and df_conversao.empty:
    st.info("Nenhum dado registrado ainda para exibir no dashboard.")
    st.stop()

anos_fat = set(pd.to_datetime(df_faturamento['data']).dt.year) if not df_faturamento.empty else set()
anos_conv = set(pd.to_datetime(df_conversao['data']).dt.year) if not df_conversao.empty else set()
anos_disponiveis = sorted(list(anos_fat | anos_conv), reverse=True)

if not anos_disponiveis:
    anos_disponiveis = [datetime.date.today().year]

ano_atual = datetime.date.today().year
index_ano = anos_disponiveis.index(ano_atual) if ano_atual in anos_disponiveis else 0

col_f_ano, col_f_mes, col_f_local, col_f_tipo = st.columns(4)

with col_f_ano:
    ano_selecionado = st.selectbox("Ano", anos_disponiveis, index=index_ano)

dicionario_meses = {
    "Todos": 0, "Janeiro": 1, "Fevereiro": 2, "Marco": 3, "Abril": 4, 
    "Maio": 5, "Junho": 6, "Julho": 7, "Agosto": 8, "Setembro": 9, 
    "Outubro": 10, "Novembro": 11, "Dezembro": 12
}

with col_f_mes:
    mes_atual_nome = list(dicionario_meses.keys())[datetime.date.today().month]
    index_mes = list(dicionario_meses.keys()).index(mes_atual_nome) if ano_selecionado == ano_atual else 0
    mes_selecionado_nome = st.selectbox("Mes", list(dicionario_meses.keys()), index=index_mes)
    num_mes_selecionado = dicionario_meses[mes_selecionado_nome]

with col_f_local:
    locais_unicos = df_faturamento['local'].unique() if not df_faturamento.empty else []
    filtro_local = st.multiselect("Local (Apenas Faturamento)", locais_unicos, default=locais_unicos)

with col_f_tipo:
    tipos_unicos = df_faturamento['tipo'].unique() if not df_faturamento.empty else []
    filtro_tipo = st.multiselect("Tipo (Apenas Faturamento)", tipos_unicos, default=tipos_unicos)

st.markdown("---")

df_fat_filtrado = pd.DataFrame()
if not df_faturamento.empty:
    mask_fat = (
        (pd.to_datetime(df_faturamento['data']).dt.year == ano_selecionado) &
        (df_faturamento['local'].isin(filtro_local)) &
        (df_faturamento['tipo'].isin(filtro_tipo))
    )
    if num_mes_selecionado != 0:
        mask_fat = mask_fat & (pd.to_datetime(df_faturamento['data']).dt.month == num_mes_selecionado)
    df_fat_filtrado = df_faturamento[mask_fat]

df_conv_filtrado = pd.DataFrame()
if not df_conversao.empty:
    mask_conv = (pd.to_datetime(df_conversao['data']).dt.year == ano_selecionado)
    if num_mes_selecionado != 0:
        mask_conv = mask_conv & (pd.to_datetime(df_conversao['data']).dt.month == num_mes_selecionado)
    df_conv_filtrado = df_conversao[mask_conv]

aba_captacao, aba_financeiro = st.tabs(["Análise de Captação (Leads)", "Faturamento e Produtividade"])

with aba_captacao:
    if df_conv_filtrado.empty:
        st.warning("Nenhum dado de agendamento encontrado para o periodo selecionado.")
    else:
        total_web = len(df_conv_filtrado[df_conv_filtrado['origem'] == 'Site/Web'])
        aprovados_web = len(df_conv_filtrado[(df_conv_filtrado['origem'] == 'Site/Web') & (df_conv_filtrado['status'] == 'Confirmado')])
        total_interno = len(df_conv_filtrado[df_conv_filtrado['origem'] == 'Recepcao/Interno'])
        
        taxa_conversao = (aprovados_web / total_web * 100) if total_web > 0 else 0
        
        col_kpi_c1, col_kpi_c2, col_kpi_c3, col_kpi_c4 = st.columns(4)
        criar_card("LEADS GERADOS (WEB)", str(total_web), col_kpi_c1)
        criar_card("LEADS CONVERTIDOS", str(aprovados_web), col_kpi_c2)
        criar_card("TAXA DE CONVERSÃO", f"{taxa_conversao:.1f}%", col_kpi_c3)
        criar_card("AGENDAMENTOS INTERNOS", str(total_interno), col_kpi_c4)
        
        st.write("")
        col_graf_c1, col_graf_c2 = st.columns(2)
        
        with col_graf_c1:
            st.markdown("#### Origem dos Agendamentos")
            df_origem = df_conv_filtrado.groupby('origem').size().reset_index(name='contagem')
            fig_origem = px.pie(
                df_origem, 
                names='origem', 
                values='contagem', 
                hole=0.4, 
                color_discrete_sequence=['#FF4B4B', '#2ca02c']
            )
            st.plotly_chart(fig_origem, use_container_width=True)
            
        with col_graf_c2:
            st.markdown("#### Status das Solicitações Web")
            df_web = df_conv_filtrado[df_conv_filtrado['origem'] == 'Site/Web']
            if not df_web.empty:
                df_status = df_web.groupby('status').size().reset_index(name='contagem')
                fig_status = px.bar(
                    df_status, 
                    x='status', 
                    y='contagem', 
                    color='status',
                    color_discrete_map={'Pendente': '#ff7f0e', 'Confirmado': '#2ca02c', 'Recusado': '#d62728', 'Cancelado': '#7f7f7f'}
                )
                fig_status.update_layout(xaxis_title="", yaxis_title="Quantidade", showlegend=False, margin=dict(l=0, r=0, t=10, b=0))
                st.plotly_chart(fig_status, use_container_width=True)
            else:
                st.info("Nenhuma solicitação web neste periodo.")

with aba_financeiro:
    if df_fat_filtrado.empty:
        st.warning("Nenhum dado financeiro encontrado para os filtros selecionados.")
    else:
        faturamento_total = df_fat_filtrado['valor'].sum()
        volume_atendimentos = len(df_fat_filtrado)
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
            df_local = df_fat_filtrado.groupby('local')['valor'].sum().reset_index()
            fig_local = px.bar(df_local, x='local', y='valor', color_discrete_sequence=['#FF4B4B'])
            fig_local.update_layout(xaxis_title="", yaxis_title="Valor (R$)", margin=dict(l=0, r=0, t=30, b=0))
            st.plotly_chart(fig_local, use_container_width=True)
            
        with col_graf2:
            st.markdown("#### Volume por Tipo de Atendimento")
            df_tipo = df_fat_filtrado.groupby('tipo').size().reset_index(name='contagem')
            fig_tipo = px.bar(df_tipo, x='tipo', y='contagem', color_discrete_sequence=['#FF4B4B'])
            fig_tipo.update_layout(xaxis_title="", yaxis_title="Quantidade", margin=dict(l=0, r=0, t=30, b=0))
            st.plotly_chart(fig_tipo, use_container_width=True)

        st.write("")
        st.markdown("#### Evolucão do Faturamento Diário")

        df_tempo = df_fat_filtrado.groupby('data')['valor'].sum().reset_index()
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