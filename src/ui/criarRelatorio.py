import streamlit as st
import datetime

st.title("Registrar um Novo Relatório")
st.markdown("""
Preencha os dados abaixo para registrar um atendimento realizado. 
O sistema registrará o relatório após o preenchimento e validação de todos os dados, verifique e preencha atentamente todos os campos, caso tenha errado alguma informação a plataforma permite que você altere ou exclua um relatório.
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
st.markdown("###### Atenção: nesse campo você deve informar o nome do paciente ou caso tenha sido um plantão, apenas coloque como no exemplo a seguir: 'Plantão 12h'")

col1, col2 = st.columns(2)
    
with col1:
    # Teste de lista de busca: Implementar depois quando o bd for criado
    pacientes_cadastrados = ["Anthony Silva", "Leonardo Souza", "Vitor Ramalho", "Maria Oliveira"]
    opcoes_paciente = ["Selecione um paciente", "+ Cadastrar Novo Paciente", "Não se aplica (Plantão)"] + pacientes_cadastrados
    paciente_selecionado = st.selectbox("Buscar Paciente", opcoes_paciente)

    novo_nome_paciente = ""
    novo_cpf_paciente = ""

    if paciente_selecionado == "+ Cadastrar Novo Paciente":
        st.markdown("###### Preencha o dados do novo paciente:")
        novo_nome_paciente = st.text_input("Nome Completo do Paciente")
        novo_cpf_paciente = st.text_input("CPF (Opcional)", placeholder="000.000.000-00")
        paciente_final = novo_nome_paciente # Na hora do banco, a ideia é colocar um id novo gerado
    elif paciente_selecionado == "Não se aplica (Plantão)":
        st.info("Atemdimento em formato de plantão. Nenhum paciente será vinculado a este registro.")
        paciente_final = None # Na hora do banco, a chave estrangeira (paciente_id) ficará vazia
    else:
        paciente_final = paciente_selecionado
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
    valor_atendimento = st.number_input("Valor do Atendimento")

st.markdown("---")

botao_enviar = st.button("Enviar Relatório", type="primary", use_container_width=True)

if botao_enviar:
    if paciente_selecionado == "Selecione um paciente":
        st.warning("Por favor, selecione um paciente, cadastre um novo ou marque como plantão.")
    elif paciente_selecionado == "+ Cadastrar Novo Paciente" and novo_nome_paciente.strip() == "":
        st.warning("Por favor, preencha o nome do novo paciente para realizar o cadastro.")
    else:
        st.success("Relatório validado com sucesso! ")
