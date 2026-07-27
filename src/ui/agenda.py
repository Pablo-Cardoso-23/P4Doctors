# agenda.py
import streamlit as st
import datetime
import time
from datetime import timezone, timedelta # Importação adicionada para tratar o fuso horário
from streamlit_calendar import calendar

from src.utils.security import verificar_acesso
from src.database.crud import buscar_agendamentos, inserir_agendamento, buscar_pacientes_para_select

st.set_page_config(page_title="Agenda Médica", layout="wide")

# Verifica se o usuário está autenticado E se temos o ID dele na sessão
if not st.session_state.get('usuario_autenticado') or not st.session_state.get('usuario_id'):
    st.switch_page("src/ui/forms.py")

verificar_acesso(perfis_permitidos=["Médico", "Secretária"])

# --- CAPTURA DE DADOS REAIS DA SESSÃO ---
# Pegamos o ID real do usuário que fez login
usuario_logado_id = st.session_state.get('usuario_id')
medico_logado_id = usuario_logado_id # Assumindo que o médico logado agenda para si mesmo

st.title("Agenda Médica")
st.markdown("Gerencie seus horários, consultas e bloqueios de plantão.")
st.markdown("---")

# Busca os eventos reais do banco formatados para o calendário
eventos_bd = buscar_agendamentos(medico_logado_id)

# Configurações aprimoradas do calendário
opcoes_calendario = {
    "headerToolbar": {
        "left": "today prev,next",
        "center": "title",
        "right": "dayGridMonth,timeGridWeek,timeGridDay",
    },
    "initialView": "timeGridWeek", 
    "slotMinTime": "06:00:00",     
    "slotMaxTime": "23:00:00",     
    "allDaySlot": False,
    "locale": "pt-br", 
    
    # --- MELHORIAS VISUAIS E DE FUSO ---
    "slotDuration": "00:15:00", # Cada linha agora tem 15 min (deixa os blocos mais altos)
    "slotLabelFormat": {        # Formata o texto da hora na barra lateral
        "hour": "2-digit",
        "minute": "2-digit",
        "omitZeroMinute": False,
    },
    "displayEventEnd": False,   # Oculta a hora final dentro do bloco para poupar espaço
    "timeZone": "local"         # Garante que o calendário use o fuso do computador
}

col_form, col_cal = st.columns([1, 3])

with col_form:
    st.subheader("Novo Agendamento")

    # BUSCA OS PACIENTES REAIS DO BANCO DE DADOS
    lista_pacientes = buscar_pacientes_para_select()
    
    # O selectbox mostra o 'nome', mas retorna o objeto
    paciente_selecionado = st.selectbox(
        "Paciente / Evento", 
        options=lista_pacientes, 
        format_func=lambda p: p["nome"]
    )

    data_evento = st.date_input("Data do Evento", datetime.date.today())

    col_hora1, col_hora2 = st.columns(2)
    with col_hora1:
        hora_inicio = st.time_input("Início", datetime.time(8, 0))
    with col_hora2:
        hora_fim = st.time_input("Fim", datetime.time(9, 0))

    tipo_evento = st.selectbox("Tipo de Evento", ["Primeira Consulta", "Retorno", "Cirurgia", "Bloqueio Pessoal"])
    status_evento = st.selectbox("Status", ["Agendado", "Confirmado", "Cancelado"])
    observacoes = st.text_area("Observações (Opcional)", max_chars=500)

    st.markdown("---")
    botao_agendar = st.button("Salvar Agendamento", type="primary", use_container_width=True)

    if botao_agendar:
        if hora_fim <= hora_inicio:
            st.error("A hora de término deve ser posterior à hora de início.")
        else:
            # 1. CRIAMOS A REGRA DO FUSO DO BRASIL (UTC-3)
            fuso_br = timezone(timedelta(hours=-3))
            
            # 2. AVISAMOS O PYTHON QUAL É O NOSSO FUSO HORÁRIO AO JUNTAR DATA E HORA
            dt_inicio_completa = datetime.datetime.combine(data_evento, hora_inicio, tzinfo=fuso_br)
            dt_fim_completa = datetime.datetime.combine(data_evento, hora_fim, tzinfo=fuso_br)
            
            # 3. CHAMANDO A FUNÇÃO DO CRUD PARA SALVAR NO SUPABASE
            inserir_agendamento(
                medico_id=medico_logado_id,
                paciente_id=paciente_selecionado["id"],
                data_hora_inicio=dt_inicio_completa,
                data_hora_fim=dt_fim_completa,
                tipo_evento=tipo_evento,
                status=status_evento,
                observacoes=observacoes,
                criado_por_id=usuario_logado_id
            )
            
            st.success("Agendamento salvo com sucesso!")
            time.sleep(1) 
            st.rerun() # Recarrega a página para atualizar o calendário

with col_cal:
    estilo_customizado = """
        .fc-event-time { font-style: normal; font-weight: bold; }
        .fc-event-title { font-weight: 500; }
        .fc-toolbar-title { font-size: 1.2rem; font-weight: bold; }
    """

    calendario = calendar(
        events=eventos_bd,
        options=opcoes_calendario,
        custom_css=estilo_customizado
    )