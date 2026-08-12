import streamlit as st
import datetime
from supabase import create_client, Client
from src.database.crud import buscar_medicos_vinculados
from src.utils.security import verificar_acesso
from src.utils.pdf_generator import gerar_pdf_prontuario

st.set_page_config(page_title="Novo Relatorio", layout="wide")

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
    st.info("Modo Equipe: Selecione o profissional para o qual deseja registrar este relatorio.")
    
    lista_medicos = buscar_medicos_vinculados(usuario_logado_id)
    
    if not lista_medicos:
        st.error("Voce ainda nao possui vinculo com nenhum medico. Contate o administrador.")
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

@st.cache_data(ttl=60)
def carregar_pacientes():
    try:
        res = supabase.table('pacientes')\
            .select('pessoa_id, pessoas!inner(nome_completo, cpf)')\
            .execute()
        
        pacientes_dict = {}
        if res.data:
            for item in res.data:
                p_id = item['pessoa_id']
                nome = item['pessoas']['nome_completo']
                pacientes_dict[f"{nome} (ID: {p_id})"] = p_id
        return pacientes_dict
    except Exception:
        return {}

mapa_pacientes = carregar_pacientes()

st.title("Registrar um Novo Relatorio")
st.markdown("""
Preencha os dados abaixo para registrar um atendimento realizado. 
O sistema registrara o relatorio apos o preenchimento e validacao de todos os dados.
""")
st.markdown("---")

st.subheader("Dados Gerais do Trabalho")

if 'hora_padrao_relatorio' not in st.session_state:
    st.session_state['hora_padrao_relatorio'] = datetime.datetime.now().time().replace(second=0, microsecond=0)

col_data, col_hora = st.columns(2)

with col_data:
    data_atend = st.date_input("Data do Atendimento", value=datetime.date.today())
with col_hora:
    hora_atend = st.time_input("Horario", value=st.session_state['hora_padrao_relatorio'])

event_time = datetime.datetime.combine(data_atend, hora_atend)

opcoes_local = ["Hospital das Clinicas", "Hospital de Base", "Hospital Anchieta", "Outro (Especificar)"]
local_selecionado = st.selectbox("Local de Atendimento", opcoes_local)

if local_selecionado == "Outro (Especificar)":
    local = st.text_input("Especifique o Local de Atendimento", placeholder="Digite o nome do local")
else:
    local = local_selecionado

st.markdown("---")

st.subheader("Informacoes do Paciente / Servico")
st.markdown("###### Atencao: informe o nome do paciente ou selecione 'Nao se aplica' para plantoes.")

col1, col2 = st.columns(2)
    
with col1:
    opcoes_paciente = ["Selecione um paciente", "+ Cadastrar Novo Paciente", "Nao se aplica (Plantao)"] + list(mapa_pacientes.keys())
    paciente_selecionado = st.selectbox("Buscar Paciente", opcoes_paciente)

    dados_novo_paciente = dict()
    nome_p = ""

    if paciente_selecionado == "+ Cadastrar Novo Paciente":
        st.markdown("###### Preencha os dados do novo paciente:")

        c1, c2 = st.columns(2)
        with c1:
            nome_p = st.text_input("Nome Completo do Paciente")
            dados_novo_paciente['nome'] = nome_p
        with c2:
            dados_novo_paciente['cpf'] = st.text_input("CPF ", placeholder="000.000.000-00")
        
        c3, c4 = st.columns(2)
        with c3:
            dados_novo_paciente['data_nascimento'] = st.date_input("Data de Nascimento",
                                                                    value=None,
                                                                    min_value=datetime.date(1900, 1, 1),
                                                                    max_value=datetime.date.today(),
                                                                    format="DD/MM/YYYY")
        with c4:
            dados_novo_paciente['email'] = st.text_input("E-mail para Contato")

        c5, c6 = st.columns([2, 2])
        with c5:
            tipos_sangue = ["Nao Informado", "A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
            dados_novo_paciente['tipo_sanguineo'] = st.selectbox("Tipo Sanguineo", tipos_sangue)
        with c6:
            dados_novo_paciente['observacoes'] = st.text_area("Observacoes Medicas Gerais", height=68)      
    elif paciente_selecionado == "Nao se aplica (Plantao)":
        st.info("Atendimento em formato de plantao. Nenhum paciente sera vinculado a este registro.")
        
with col2:
    opcoes_tipo = ["Primeira Consulta", "Retorno", "Procedimento", "Plantao", "Outro (Especificar)"]
    tipo_selecionado = st.selectbox("Tipo de Consulta", opcoes_tipo)

if tipo_selecionado == "Outro (Especificar)":
    tipo_consulta = st.text_input("Especifique o Tipo de Consulta", placeholder="Ex: Exame de Rotina")
else:
    tipo_consulta = tipo_selecionado

st.markdown("---")

st.subheader("Detalhes e Valores")

col3, col4 = st.columns(2)

with col3:
    relatorio_atendimento = st.text_area("Relatorio Clinico / Evolucao (Campo Opcional)")
with col4:
    valor_atendimento = st.number_input("Valor do Atendimento", min_value=0.0, step=50.0, format="%.2f")

st.markdown("---")

botao_enviar = st.button("Enviar Relatorio", type="primary", use_container_width=True)

if botao_enviar:
    if paciente_selecionado == "Selecione um paciente":
        st.error("Por favor, selecione um paciente ou cadastre um novo.")
    elif not local.strip():
        st.error("Por favor, especifique o local de atendimento.")
    else:
        id_paciente_final = None
        erro_processamento = False
        nome_paciente_pdf = ""

        if paciente_selecionado == "+ Cadastrar Novo Paciente":
            nome_paciente_pdf = nome_p.strip()
            cpf_p = dados_novo_paciente.get('cpf', '').strip()

            if not nome_paciente_pdf:
                st.error("O Nome Completo e obrigatorio para o cadastro de novos pacientes.")
                erro_processamento = True
            elif not cpf_p:
                st.error("O CPF e obrigatorio para o cadastro de novos pacientes.")
                erro_processamento = True
            else:
                try:
                    res_p = supabase.table('pessoas').insert({
                        "nome_completo": nome_paciente_pdf,
                        "cpf": cpf_p,
                        "status": "Ativo"
                    }).execute()

                    if res_p.data:
                        id_paciente_final = res_p.data[0]['id']
                        dt_nasc = dados_novo_paciente.get('data_nascimento')
                        dt_nasc_str = dt_nasc.strftime("%Y-%m-%d") if dt_nasc else None

                        supabase.table('pacientes').insert({
                            "pessoa_id": id_paciente_final,
                            "data_nascimento": dt_nasc_str,
                            "email": dados_novo_paciente.get('email', '').strip(),
                            "tipo_sanguineo": dados_novo_paciente.get('tipo_sanguineo'),
                            "observacoes": dados_novo_paciente.get('observacoes', '').strip()
                        }).execute()
                    else:
                        st.error("Erro ao gerar registro na tabela de pessoas.")
                        erro_processamento = True
                except Exception as e:
                    st.error(f"Erro ao cadastrar novo paciente no banco de dados: {e}")
                    erro_processamento = True

        elif paciente_selecionado == "Nao se aplica (Plantao)":
            nome_paciente_pdf = "Plantao (Nao se aplica)"
        else:
            id_paciente_final = mapa_pacientes[paciente_selecionado]
            nome_paciente_pdf = paciente_selecionado.split(" (ID:")[0]

        if not erro_processamento:
            try:
                dt_atendimento_str = event_time.strftime("%Y-%m-%d %H:%M:%S")

                payload_atendimento = {
                    "data_atendimento": dt_atendimento_str,
                    "medico_id": medico_alvo_id, 
                    "paciente_id": id_paciente_final,
                    "local_atendimento": local,
                    "tipo_consulta": tipo_consulta,
                    "relatorio_clinico": relatorio_atendimento if relatorio_atendimento.strip() else None,
                    "valor": float(valor_atendimento),
                    "criado_por_id": usuario_logado_id
                }

                supabase.table('atendimentos').insert(payload_atendimento).execute()

                st.success("Relatorio de atendimento registrado com sucesso no banco de dados!")
                st.cache_data.clear()
                
                pdf_bytes = gerar_pdf_prontuario(
                    nome_medico=nome_medico_pdf,
                    nome_paciente=nome_paciente_pdf,
                    data_atend=dt_atendimento_str,
                    local=local,
                    tipo=tipo_consulta,
                    relatorio=relatorio_atendimento
                )
                
                nome_arquivo = f"Prontuario_{nome_paciente_pdf.replace(' ', '_')}.pdf"
                
                st.download_button(
                    label="Baixar Prontuario em PDF",
                    data=pdf_bytes,
                    file_name=nome_arquivo,
                    mime="application/pdf",
                    type="secondary"
                )

            except Exception as e:
                st.error(f"Erro ao registrar atendimento no Supabase: {e}")