import streamlit as st
import datetime
from src.database.crud import buscar_medicos_publico, criar_agendamento_publico

st.set_page_config(page_title="Agendar Consulta - P4 Health", layout="centered")

st.title("Agendar Consulta")
st.markdown("Bem-vindo(a) à central de agendamentos da **P4 Health**.")
st.markdown("Preencha o formulário abaixo para solicitar um horário. Nossa equipe avaliará a disponibilidade e confirmará sua consulta.")
st.markdown("---")

lista_medicos = buscar_medicos_publico()

if not lista_medicos:
    st.warning("No momento não temos profissionais disponíveis para agendamento online.")
    st.stop()

with st.form("form_agendamento_publico"):
    st.subheader("1. Escolha o Profissional e a Data")
    
    medico_selecionado = st.selectbox(
        "Profissional", 
        options=lista_medicos, 
        format_func=lambda m: f"{m['nome']} ({m['especialidade']})"
    )
    
    col_data, col_hora = st.columns(2)
    with col_data:
        data_escolhida = st.date_input("Data Desejada", min_value=datetime.date.today())
    with col_hora:
        hora_escolhida = st.time_input("Horário de Preferência", step=1800)
        
    st.markdown("---")
    st.subheader("2. Seus Dados de Contato")
    
    nome_paciente = st.text_input("Seu Nome Completo")
    
    col_contato1, col_contato2 = st.columns(2)
    with col_contato1:
        email_paciente = st.text_input("Seu E-mail principal")
    with col_contato2:
        telefone_paciente = st.text_input("Seu WhatsApp / Telefone")
        
    observacoes = st.text_area("Motivo da Consulta ou Observações (Opcional)")
    
    st.markdown("---")
    botao_solicitar = st.form_submit_button("Solicitar Agendamento", type="primary", use_container_width=True)
    
    if botao_solicitar:
        if not nome_paciente or not email_paciente or not telefone_paciente:
            st.error("Por favor, preencha seu Nome, E-mail e Telefone para que possamos retornar o contato.")
        else:
            try:
                data_hora_combinada = datetime.datetime.combine(data_escolhida, hora_escolhida).isoformat()
                
                criar_agendamento_publico(
                    medico_id=medico_selecionado['id'],
                    data_hora_inicio=data_hora_combinada,
                    nome=nome_paciente,
                    email=email_paciente,
                    telefone=telefone_paciente,
                    observacoes=observacoes
                )
                
                st.success(f"Obrigado, {nome_paciente}! Sua solicitação foi enviada para a clínica.")
                st.info("Aguarde nosso contato via E-mail ou WhatsApp para a confirmação definitiva do horário.")
                
            except Exception as e:
                st.error(f"Ocorreu um erro ao enviar sua solicitação. Tente novamente mais tarde. Erro: {e}")

st.markdown("<br><br><center><small>P4 Health © 2026</small></center>", unsafe_allow_html=True)