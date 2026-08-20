import streamlit as st
import pandas as pd
import datetime
from supabase import create_client, Client

from src.database.crud import buscar_medicos_vinculados
from src.utils.security import verificar_acesso
from src.utils.pdf_generator import gerar_pdf_prontuario

st.set_page_config(page_title="Histórico de Atendimentos", layout="wide")

if not st.session_state.get('usuario_autenticado') or not st.session_state.get('usuario_id'):
    st.warning("Acesso restrito. Por favor, realize o login para acessar esta pagina.")
    st.stop()

verificar_acesso(perfis_permitidos=["Médico", "Secretária", "Administrativo"])

@st.cache_resource
def get_supabase() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = get_supabase()

usuario_logado_id = st.session_state.get('usuario_id')
tipo_perfil = st.session_state.get('tipo_perfil')

medico_alvo_id = None
nome_medico_pdf = ""

if tipo_perfil in ['Secretária', 'Administrativo']:
    st.info("Modo Equipe: Selecione o profissional para visualizar o historico de atendimentos.")
    
    lista_medicos = buscar_medicos_vinculados(usuario_logado_id)
    
    if not lista_medicos:
        st.error("Você ainda nao possui vinculo com nenhum medico. Contate o administrador.")
        st.stop()

    medico_selecionado = st.selectbox(
        "Profissional", 
        options=lista_medicos, 
        format_func=lambda m: m["nome"]
    )
    medico_alvo_id = medico_selecionado["id"]
    nome_medico_pdf = medico_selecionado["nome"]
else:
    medico_alvo_id = usuario_logado_id
    nome_medico_pdf = f"Dr(a). {st.session_state.get('usuario_autenticado')}"

def carregar_historico_db(medico_id):
    try:
        res = supabase.table('atendimentos')\
            .select('data_atendimento, local_atendimento, tipo_consulta, valor, relatorio_clinico, paciente_id, pacientes!paciente_id(pessoas(nome_completo))')\
            .eq('medico_id', medico_id)\
            .order('data_atendimento', desc=True)\
            .execute()
        
        if not res.data:
            return pd.DataFrame(columns=["Data", "Paciente/Servico", "Tipo", "Local", "Valor (R$)", "Status"])
        
        registros_processados = []
        for item in res.data:
            data_bruta = item['data_atendimento']
            data_bruta = data_bruta.replace("T", " ")
            
            if len(data_bruta) > 10:
                dt_obj = datetime.datetime.strptime(data_bruta[:19], "%Y-%m-%d %H:%M:%S")
            else:
                dt_obj = datetime.datetime.strptime(data_bruta[:10], "%Y-%m-%d")
                
            data_formatada = dt_obj.strftime("%d/%m/%Y")
            
            if item.get('pacientes') and item['pacientes'].get('pessoas'):
                paciente_servico = item['pacientes']['pessoas']['nome_completo']
            else:
                paciente_servico = item['tipo_consulta'] if item['tipo_consulta'] == "Plantao" else "Servico Geral"

            registros_processados.append({
                "Data": data_formatada,
                "Paciente/Servico": paciente_servico,
                "Tipo": item['tipo_consulta'],
                "Local": item['local_atendimento'],
                "Valor (R$)": float(item['valor']),
                "Status": "Registrado",
                "Data_ISO": dt_obj.date(),
                "Data_Bruta": data_bruta,
                "Relatorio": item.get('relatorio_clinico', '')
            })
            
        return pd.DataFrame(registros_processados)
    except Exception as e:
        st.error(f"Erro ao consultar historico no banco de dados: {e}")
        return pd.DataFrame(columns=["Data", "Paciente/Servico", "Tipo", "Local", "Valor (R$)", "Status"])

df_historico = carregar_historico_db(medico_alvo_id)

st.title("Histórico de Atendimentos")
st.markdown("Consulte, filtre e revise todos os relatorios, consultas e plantoes registrados no sistema.")
st.markdown("---")

st.subheader("Filtros de Busca")
col_filtro1, col_filtro2, col_filtro3 = st.columns(3)

with col_filtro1:
    filtro_data = st.date_input("Periodo", value=(datetime.date.today() - datetime.timedelta(days=7), datetime.date.today()))
with col_filtro2:
    filtro_tipo = st.selectbox("Tipo de Registro", ["Todos", "Primeira Consulta", "Retorno", "Procedimento", "Plantao"])
with col_filtro3:
    filtro_busca = st.text_input("Buscar por Paciente", placeholder="Digite o nome...")

st.markdown("---")

st.subheader("Relatorios Registrados")

df_filtrado = df_historico.copy()

if not df_filtrado.empty:
    if filtro_tipo != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Tipo"] == filtro_tipo]

    if filtro_busca:
        df_filtrado = df_filtrado[df_filtrado["Paciente/Servico"].str.contains(filtro_busca, case=False, na=False)]

    if isinstance(filtro_data, tuple) and len(filtro_data) == 2:
        data_inicio, data_fim = filtro_data
        df_filtrado = df_filtrado[(df_filtrado['Data_ISO'] >= data_inicio) & (df_filtrado['Data_ISO'] <= data_fim)]

st.dataframe(
    df_filtrado,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Valor (R$)": st.column_config.NumberColumn(format="R$ %.2f"),
        "Data_ISO": None,
        "Data_Bruta": None,
        "Relatorio": None
    }
)

st.markdown("---")

st.subheader("Exportacao de Dados")

if df_filtrado.empty:
    st.info("Nenhum dado disponivel para exportacao com os filtros atuais.")
else:
    col_csv, col_pdf = st.columns(2)
    
    with col_csv:
        st.markdown("**1. Exportar Planilha de Controle**")
        st.caption("Baixe a visao atual da tabela em formato CSV.")
        
        @st.cache_data
        def converter_para_csv(df):
            df_limpo = df.drop(columns=['Data_ISO', 'Data_Bruta', 'Relatorio'], errors='ignore')
            return df_limpo.to_csv(index=False).encode('utf-8')

        csv_dados = converter_para_csv(df_filtrado)
        
        st.download_button(
            label="Baixar Relatorio Financeiro (CSV)",
            data=csv_dados,
            file_name=f"historico_atendimentos_{datetime.date.today()}.csv",
            mime="text/csv",
            use_container_width=True
        )

    with col_pdf:
        st.markdown("**2. Emitir 2a Via de Prontuario**")
        st.caption("Selecione um atendimento para gerar o documento oficial.")
    
        opcoes_exportacao = df_filtrado.apply(
            lambda x: f"{x['Data']} - {x['Paciente/Servico']} ({x['Tipo']})", axis=1
        ).tolist()
        
        registro_selecionado = st.selectbox("Selecione o registro:", options=[""] + opcoes_exportacao)
        
        if registro_selecionado:
            index_selecionado = opcoes_exportacao.index(registro_selecionado)
            linha_selecionada = df_filtrado.iloc[index_selecionado]
            
            pdf_bytes = gerar_pdf_prontuario(
                nome_medico=nome_medico_pdf,
                nome_paciente=linha_selecionada["Paciente/Servico"],
                data_atend=linha_selecionada["Data_Bruta"],
                local=linha_selecionada["Local"],
                tipo=linha_selecionada["Tipo"],
                relatorio=linha_selecionada["Relatorio"]
            )
            
            nome_arquivo = f"2a_Via_Prontuario_{linha_selecionada['Paciente/Servico'].replace(' ', '_')}.pdf"
            
            st.download_button(
                label="Baixar Prontuario (PDF)",
                data=pdf_bytes,
                file_name=nome_arquivo,
                mime="application/pdf",
                type="primary",
                use_container_width=True
            )