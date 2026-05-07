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

    dados_novo_paciente = dict()

    if paciente_selecionado == "+ Cadastrar Novo Paciente":
        st.markdown("###### Preencha o dados do novo paciente:")

        c1, c2 = st.columns(2)
        with c1:
            dados_novo_paciente['nome'] = st.text_input("Nome Completo do Paciente")
        with c2:
            dados_novo_paciente['cpf'] = st.text_input("CPF ", placeholder="000.000.000-00")
        
        c3, c4 = st.columns(2)
        with c3:
            dados_novo_paciente['data_nascimento'] = st.date_input("Data de Nascimento", value=None)
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
    valor_atendimento = st.number_input("Valor do Atendimento")

st.markdown("---")

botao_enviar = st.button("Enviar Relatório", type="primary", use_container_width=True)

if botao_enviar:
    if paciente_selecionado == "Selecione um paciente":
        st.error("Por favor, selecione um paciente ou cadastre um novo.")
    elif paciente_selecionado == "+ Cadastrar Novo Paciente":
        if not dados_novo_paciente.get('nome', '').strip():
            st.error("O Nome Completo é obrigatório para o cadastro de novos pacientes.")
        elif not dados_novo_paciente.get('cpf', '').strip():
            st.error("O CPF é obrigatório para o cadastro de novos pacientes.")
        else:
            st.success(f"Relatório de {dados_novo_paciente['nome']} validado com sucesso!")
    else:
        st.success(f"Relatório de {paciente_selecionado} validado com sucesso!")
