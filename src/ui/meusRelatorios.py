import streamlit as st
import pandas as pd
import datetime
from supabase import create_client, Client

# ==========================================
# 1. PROTEÇÃO DE SESSÃO E CONEXÃO
# ==========================================
if not st.session_state.get('usuario_autenticado') or not st.session_state.get('usuario_id'):
    st.warning("Acesso restrito. Por favor, realize o login para acessar esta página.")
    st.stop()

@st.cache_resource
def get_supabase() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = get_supabase()

# ==========================================
# 2. CARREGAMENTO DE DADOS REAIS DO SUPABASE
# ==========================================
def carregar_historico_db(medico_id):
    try:
        res = supabase.table('atendimentos')\
            .select('data_atendimento, local_atendimento, tipo_consulta, valor, relatorio_clinico, paciente_id, pacientes!paciente_id(pessoas(nome_completo))')\
            .eq('medico_id', medico_id)\
            .order('data_atendimento', desc=True)\
            .execute()
        
        if not res.data:
            return pd.DataFrame(columns=["Data", "Paciente/Serviço", "Tipo", "Local", "Valor (R$)", "Status"])
        
        registros_processados = []
        for item in res.data:
            # Tratamento Flexível de Data
            data_bruta = item['data_atendimento']
            
            # Normaliza o formato caso o banco devolva com "T" (ex: 2026-07-28T15:30:00)
            data_bruta = data_bruta.replace("T", " ")
            
            # Verifica se tem horário embutido ou apenas a data
            if len(data_bruta) > 10:
                dt_obj = datetime.datetime.strptime(data_bruta[:19], "%Y-%m-%d %H:%M:%S")
            else:
                dt_obj = datetime.datetime.strptime(data_bruta[:10], "%Y-%m-%d")
                
            data_formatada = dt_obj.strftime("%d/%m/%Y")
            
            if item.get('pacientes') and item['pacientes'].get('pessoas'):
                paciente_servico = item['pacientes']['pessoas']['nome_completo']
            else:
                paciente_servico = item['tipo_consulta'] if item['tipo_consulta'] == "Plantão" else "Serviço Geral"

            registros_processados.append({
                "Data": data_formatada,
                "Paciente/Serviço": paciente_servico,
                "Tipo": item['tipo_consulta'],
                "Local": item['local_atendimento'],
                "Valor (R$)": float(item['valor']),
                "Status": "Registrado",
                "Data_ISO": dt_obj.date()
            })
            
        return pd.DataFrame(registros_processados)
    except Exception as e:
        st.error(f"Erro ao consultar histórico no banco de dados: {e}")
        return pd.DataFrame(columns=["Data", "Paciente/Serviço", "Tipo", "Local", "Valor (R$)", "Status"])
    
# Carrega o DataFrame vindo direto do PostgreSQL filtrado pelo médico logado
df_historico = carregar_historico_db(st.session_state['usuario_id'])

# ==========================================
# 3. INTERFACE E FILTROS DO USUÁRIO
# ==========================================
st.title("Histórico de Atendimentos")
st.markdown("Consulte, filtre e revise todos os relatórios, consultas e plantões registrados no sistema.")
st.markdown("---")

st.subheader("Filtros de Busca")
col_filtro1, col_filtro2, col_filtro3 = st.columns(3)

with col_filtro1:
    filtro_data = st.date_input("Período", value=(datetime.date.today() - datetime.timedelta(days=7), datetime.date.today()))
with col_filtro2:
    filtro_tipo = st.selectbox("Tipo de Registro", ["Todos", "Primeira Consulta", "Retorno", "Procedimento", "Plantão"])
with col_filtro3:
    filtro_busca = st.text_input("Buscar por Paciente", placeholder="Digite o nome...")

st.markdown("---")

st.subheader("Relatórios Registrados")

# Cópia para aplicação dos filtros em memória, mantendo a responsividade do Pandas
df_filtrado = df_historico.copy()

if filtro_tipo != "Todos":
    df_filtrado = df_filtrado[df_filtrado["Tipo"] == filtro_tipo]

if filtro_busca and not df_filtrado.empty:
    df_filtrado = df_filtrado[df_filtrado["Paciente/Serviço"].str.contains(filtro_busca, case=False, na=False)]

if isinstance(filtro_data, tuple) and len(filtro_data) == 2 and not df_filtrado.empty:
    data_inicio, data_fim = filtro_data
    df_filtrado = df_filtrado[(df_filtrado['Data_ISO'] >= data_inicio) & (df_filtrado['Data_ISO'] <= data_fim)]

# Remove a coluna auxiliar para não exibi-la na tabela da interface
if 'Data_ISO' in df_filtrado.columns:
    df_filtrado = df_filtrado.drop(columns=['Data_ISO'])

# Renderização da Tabela reativa
st.dataframe(
    df_filtrado,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Valor (R$)": st.column_config.NumberColumn(format="R$ %.2f")
    }
)

st.markdown("---")

# ==========================================
# 4. AÇÕES E EXPORTAÇÃO
# ==========================================
@st.cache_data
def converter_para_csv(df):
    return df.to_csv(index=False).encode('utf-8')

csv_dados = converter_para_csv(df_filtrado)

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