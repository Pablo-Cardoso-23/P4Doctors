import streamlit as st
import datetime
import time
from streamlit_calendar import calendar
from src.utils.security import verificar_acesso

st.set_page_config(page_title="Agenda Médica", layout="wide")

if "usuario_autenticado" not in st.session_state or not st.session_state['usuario_autenticado']:
    st.switch_page("src/ui/forms.py")

TIMEOUT_MINUTOS = 30
agora = datetime.datetime.now()
verificar_acesso(perfis_permitidos=["Médico", "Secretária"])

st.title("Agenda Médica")
st.markdown("Gerencie seus horários, consultas e bloqueios de plantão.")
st.markdown("---")

opcoes_calendario = {
    "headerToolbar": {
        "left": "today prev,next",
        "center": "title",
        "right": "dayGridMonth,timeGridWeek,timeGridDay",
    },
    "initialView": "timeGridWeek", # Começa mostrando a semana
    "slotMinTime": "06:00:00",     # A agenda começa às 6h da manhã
    "slotMaxTime": "23:00:00",     # A agenda vai até as 23h
    "allDaySlot": False,
    "locale": "pt-br",             # Traduz os dias e meses para Português
}

# DADOS SÓ PARA TESTE, DEPOIS COLOCAR O BD
hoje = datetime.date.today()
eventos_teste = [
    {
        "title": "Carlos Souza (Primeira Consulta)",
        "start": f"{hoje}T09:00:00",
        "end": f"{hoje}T10:00:00",
        "color": "#1f77b4", # Azul
    },
    {
        "title": "Maria Oliveira (Retorno)",
        "start": f"{hoje}T14:00:00",
        "end": f"{hoje}T14:30:00",
        "color": "#2ca02c", # Verde
    },
    {
        "title": "Plantão 12h - Hospital de Base",
        "start": f"{hoje + datetime.timedelta(days=1)}T07:00:00",
        "end": f"{hoje + datetime.timedelta(days=1)}T19:00:00",
        "color": "#d62728", # Vermelho (Destaca bloqueios grandes)
    }
]

col_form, col_cal = st.columns([1, 3])

with col_form:
    st.subheader("Novo Agendamento")

    paciente = st.selectbox("Paciente / Evento", ["Selecione", "Bloqueio/Plantão", "Anthony Silva", "Leonardo Souza", "Vitor Ramalho", "Maria Oliveira"])
    data_evento = st.date_input("Data do Evento", hoje)

    col_hora1, col_hora2 = st.columns(2)

    with col_hora1:
        hora_inicio = st.time_input("Início", datetime.time(8, 0))
    with col_hora2:
        hora_fim = st.time_input("Fim", datetime.time(9, 0))

    tipo_evento = st.selectbox("Tipo de Evento", ["Primeira Consulta", "Retorno", "Cirurgia", "Bloqueio Pessoal"])
    status_evento = st.selectbox("Status", ["Agendado", "Confirmado"])

    st.markdown("---")
    botao_agendar = st.button("Salvar Agendamento", type="primary", use_container_width=True)

    if botao_agendar:
        if paciente == "Selecione":
            st.warning("Selecione um paciente ou informe que é um bloqueio.")
        else:
            st.success("Agendamento salvo!")
with col_cal:
    estilo_customizado = """
        .fc-event-time { font-style: normal; font-weight: bold; }
        .fc-event-title { font-weight: 500; }
        .fc-toolbar-title { font-size: 1.2rem; font-weight: bold; }
    """

    calendario = calendar(
        events=eventos_teste,
        options=opcoes_calendario,
        custom_css=estilo_customizado
    )
