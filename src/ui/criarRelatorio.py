import streamlit as st
import datetime
from supabase import create_client, Client
from src.database.crud import buscar_medicos_vinculados
from src.utils.security import verificar_acesso

st.set_page_config(page_title="Novo Relatório", layout="wide")

if not st.session_state.get('usuario_autenticado') or not st.session_state.get('usuario_id'):
    st.warning("Acesso restrito. Por favor, realize o login para acessar esta página.")
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

if tipo_perfil in ['Secretária', 'Administrativo']:
    st.info("Modo Equipe: Selecione o profissional para o qual deseja registrar este relatório.")
    
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

@st.cache_data(ttl=60)
def carregar_pacientes():
    """Busca a lista de pacientes ativos cadastrados no banco de dados."""
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

st.title("Registrar um Novo Relatório")
st.markdown("""
Preencha os dados abaixo para registrar um atendimento realizado. 
O sistema registrará o relatório após o preenchimento e validação de todos os dados. Verifique e preencha atentamente todos os campos; caso tenha errado alguma informação, a plataforma permite que você altere ou exclua um relatório posteriormente.
""")
st.markdown("---")

st.subheader("Dados Gerais do Trabalho")

event_time = st.datetime_input(
    "Data e Horário do Atendimento",
    value=datetime.datetime.now(),
)

opcoes_local = ["Hospital das Clínicas", "Hospital de Base", "Hospital Anchieta", "Outro (Especificar)"]
local_selecionado = st.selectbox("Local de Atendimento", opcoes_local)

if local_selecionado == "Outro (Especificar)":
    local = st.text_input("Especifique o Local de Atendimento", placeholder="Digite o nome do local")
else:
    local = local_selecionado

st.markdown("---")

st.subheader("Informações do Paciente / Serviço")
st.markdown("###### Atenção: nesse campo você deve informar o nome do paciente ou, caso tenha sido um plantão, apenas coloque como no exemplo a seguir: 'Plantão 12h'")

col1, col2 = st.columns(2)
    
with col1:
    opcoes_paciente = ["Selecione um paciente", "+ Cadastrar Novo Paciente", "Não se aplica (Plantão)"] + list(mapa_pacientes.keys())
    paciente_selecionado = st.selectbox("Buscar Paciente", opcoes_paciente)

    dados_novo_paciente = dict()

    if paciente_selecionado == "+ Cadastrar Novo Paciente":
        st.markdown("###### Preencha os dados do novo paciente:")

        c1, c2 = st.columns(2)
        with c1:
            dados_novo_paciente['nome'] = st.text_input("Nome Completo do Paciente")
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
            tipos_sangue = ["Não Informado", "A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
            dados_novo_paciente['tipo_sanguineo'] = st.selectbox("Tipo Sanguíneo", tipos_sangue)
        with c6:
            dados_novo_paciente['observacoes'] = st.text_area("Observações Médicas Gerais", height=68)      
    elif paciente_selecionado == "Não se aplica (Plantão)":
        st.info("Atendimento em formato de plantão. Nenhum paciente será vinculado a este registro.")
        
with col2:
    opcoes_tipo = ["Primeira Consulta", "Retorno", "Procedimento", "Plantão", "Outro (Especificar)"]
    tipo_selecionado = st.selectbox("Tipo de Consulta", opcoes_tipo)

if tipo_selecionado == "Outro (Especificar)":
    tipo_consulta = st.text_input("Especifique o Tipo de Consulta", placeholder="Ex: Exame de Rotina")
else:
    tipo_consulta = tipo_selecionado

st.markdown("---")

st.subheader("Detalhes e Valores")

col3, col4 = st.columns(2)

with col3:
    relatorio_atendimento = st.text_area("Relatório Clínico / Evolução (Campo Opcional)")
with col4:
    valor_atendimento = st.number_input("Valor do Atendimento", min_value=0.0, step=50.0, format="%.2f")

st.markdown("---")

botao_enviar = st.button("Enviar Relatório", type="primary", use_container_width=True)

if botao_enviar:
    if paciente_selecionado == "Selecione um paciente":
        st.error("Por favor, selecione um paciente ou cadastre um novo.")
    elif not local.strip():
        st.error("Por favor, especifique o local de atendimento.")
    else:
        id_paciente_final = None
        erro_processamento = False

        if paciente_selecionado == "+ Cadastrar Novo Paciente":
            nome_p = dados_novo_paciente.get('nome', '').strip()
            cpf_p = dados_novo_paciente.get('cpf', '').strip()

            if not nome_p:
                st.error("O Nome Completo é obrigatório para o cadastro de novos pacientes.")
                erro_processamento = True
            elif not cpf_p:
                st.error("O CPF é obrigatório para o cadastro de novos pacientes.")
                erro_processamento = True
            else:
                try:
                    res_p = supabase.table('pessoas').insert({
                        "nome_completo": nome_p,
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

        elif paciente_selecionado in mapa_pacientes:
            id_paciente_final = mapa_pacientes[paciente_selecionado]

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

                st.success("Relatório de atendimento registrado com sucesso no banco de dados!")
                st.cache_data.clear()
            except Exception as e:
                st.error(f"Erro ao registrar atendimento no Supabase: {e}")