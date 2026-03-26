import streamlit as st
import datetime

st.title("Registrar um Novo Relatório")
st.markdown("""
Preencha os dados abaixo para registrar um atendimento realizado. 
O sistema registrará o relatório após o preenchimento e validação de todos os dados, verifique e preecnha atentamente todos os campos, caso tenha errado alguma informação a plataforma permite que você altere ou exclua um relatório.
""")

with st.form("novo_relatorio"):
    st.subheader("Dados Gerais do Trabalho")

    event_time = st.datetime_input(
        "Data e Horário do Atendimento",
        datetime.datetime(2025, 11, 19, 16, 45),
    )
    st.selectbox("Local de Atendimento", ["Hospital das Clínicas", "Hospital de Base", "Hospital Anchieta"])

    st.markdown("---")

    st.subheader("Informações do Paciente / Serviço")
    st.markdown("###### Atenção: nesse campo você deve informar o nome do paciente ou caso tenha sido um plantão, apenas coloque como no exemplo a seguir: 'Plantão 12h'")

    col1, col2 = st.columns(2)
    
    with col1:
        st.text_input("Nome do Paciente / Serviço", placeholder="Ex: Pablo James ou Platão 12h")
    with col2:
        st.selectbox("Tipo de Consulta", ["Primeira Consulta", "Retorno", "Procedimento", "Plantão"])

    st.markdown("---")

    st.subheader("Detalhes e Valores")

    col3, col4 = st.columns(2)

    with col3:
        st.text_area("Relatório Clínico / Evolução (Campo Opcional)")
    with col4:
        st.number_input("Valor do Atendimento")

    st.markdown("---")

    botao_enviar = st.form_submit_button("Enviar Relatório", type="primary", use_container_width=True)
