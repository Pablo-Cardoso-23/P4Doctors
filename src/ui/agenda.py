import streamlit as st
import datetime
import time
from datetime import timezone, timedelta
from streamlit_calendar import calendar
from src.utils.security import verificar_acesso
from src.database.crud import (
    buscar_agendamentos, 
    inserir_agendamento, 
    buscar_pacientes_para_select, 
    buscar_medicos_vinculados, 
    buscar_agendamentos_pendentes, 
    aprovar_agendamento_web, 
    recusar_agendamento_web,
    cadastrar_paciente_rapido,
    atualizar_status_agendamento
)

st.set_page_config(page_title="Agenda Medica", layout="wide")

if not st.session_state.get('usuario_autenticado') or not st.session_state.get('usuario_id'):
    st.switch_page("src/ui/forms.py")

verificar_acesso(perfis_permitidos=["Médico", "Secretária", "Administrativo"])

usuario_logado_id = st.session_state.get('usuario_id')
tipo_perfil = st.session_state.get('tipo_perfil')

medico_alvo_id = None

if tipo_perfil in ['Secretária', 'Administrativo']:
    st.info("Modo Equipe: Selecione a agenda do profissional vinculado.")
    
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

else:
    medico_alvo_id = usuario_logado_id

st.title("Agenda Medica")
st.markdown("Gerencie seus horarios, consultas e bloqueios de plantao.")
st.markdown("---")

eventos_bd = buscar_agendamentos(medico_alvo_id)

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
    "height": 650,
    "slotDuration": "00:15:00", 
    "slotLabelFormat": {        
        "hour": "2-digit",
        "minute": "2-digit",
        "omitZeroMinute": False,
    },
    "displayEventEnd": False,   
    "timeZone": "UTC" 
}

col_form, col_cal = st.columns([1, 3])

with col_form:
    st.subheader("Novo Agendamento")

    modo_paciente = st.radio("Registro do Paciente", ["Existente", "Novo"], horizontal=True)
    
    paciente_id_final = None
    nome_novo = ""
    email_novo = ""
    telefone_novo = ""

    if modo_paciente == "Existente":
        lista_pacientes = buscar_pacientes_para_select()
        paciente_selecionado = st.selectbox(
            "Paciente / Evento", 
            options=lista_pacientes, 
            format_func=lambda p: p["nome"]
        )
        if paciente_selecionado:
            paciente_id_final = paciente_selecionado["id"]
    else:
        nome_novo = st.text_input("Nome Completo")
        email_novo = st.text_input("E-mail")
        telefone_novo = st.text_input("Telefone")
        st.caption("O paciente sera cadastrado no banco automaticamente.")

    data_evento = st.date_input("Data do Evento", datetime.date.today())

    col_hora1, col_hora2 = st.columns(2)
    with col_hora1:
        hora_inicio = st.time_input("Inicio", datetime.time(8, 0))
    with col_hora2:
        hora_fim = st.time_input("Fim", datetime.time(9, 0))

    tipo_evento = st.selectbox("Tipo de Evento", ["Primeira Consulta", "Retorno", "Cirurgia", "Bloqueio Pessoal"])
    status_evento = st.selectbox("Status", ["Agendado", "Confirmado", "Cancelado"])
    observacoes = st.text_area("Observacoes (Opcional)", max_chars=500)

    st.markdown("---")
    botao_agendar = st.button("Salvar Agendamento", type="primary", use_container_width=True)

    if botao_agendar:
        if hora_fim <= hora_inicio:
            st.error("A hora de termino deve ser posterior a hora de inicio.")
        elif modo_paciente == "Novo" and (not nome_novo or not email_novo):
            st.error("Para novos pacientes, o Nome e o E-mail sao obrigatorios.")
        else:
            try:
                if modo_paciente == "Novo":
                    paciente_id_final = cadastrar_paciente_rapido(nome_novo, email_novo, telefone_novo)

                fuso_br = timezone(timedelta(hours=-3))
                
                dt_inicio_completa = datetime.datetime.combine(data_evento, hora_inicio, tzinfo=fuso_br)
                dt_fim_completa = datetime.datetime.combine(data_evento, hora_fim, tzinfo=fuso_br)
                
                inserir_agendamento(
                    medico_id=medico_alvo_id,
                    paciente_id=paciente_id_final,
                    data_hora_inicio=dt_inicio_completa,
                    data_hora_fim=dt_fim_completa,
                    tipo_evento=tipo_evento,
                    status=status_evento,
                    observacoes=observacoes,
                    criado_por_id=usuario_logado_id 
                )
                
                st.success("Agendamento salvo com sucesso!")
                time.sleep(1) 
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao processar o agendamento: {e}")

with col_cal:
    aba_calendario, aba_lista, aba_solicitacoes = st.tabs(["Calendario", "Lista de Agendamentos", "Solicitacoes da Web"])

    with aba_calendario:
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

    with aba_lista:
        st.subheader("Todos os Agendamentos")
        
        if len(eventos_bd) > 0:
            dados_tabela = []
            opcoes_para_edicao = {}
            
            for evento in eventos_bd:
                inicio_dt = datetime.datetime.fromisoformat(evento["start"])
                fim_dt = datetime.datetime.fromisoformat(evento["end"])
                status_atual = evento.get("status", "-")
                
                dados_tabela.append({
                    "Paciente / Evento": evento["title"],
                    "Contato": evento.get("contato", "-"),
                    "Data": inicio_dt.strftime("%d/%m/%Y"),
                    "Inicio": inicio_dt.strftime("%H:%M"),
                    "Fim": fim_dt.strftime("%H:%M"),
                    "Status": status_atual,
                    "Observacoes": evento.get("observacoes", "-")
                })
                
                if status_atual not in ["Concluído", "Cancelado"]:
                    rotulo = f"{inicio_dt.strftime('%d/%m')} às {inicio_dt.strftime('%H:%M')} - {evento['title']}"
                    opcoes_para_edicao[rotulo] = evento["id"]

            st.dataframe(dados_tabela, use_container_width=True, hide_index=True)
            
            st.markdown("---")
            st.subheader("Alterar Status")
            st.caption("Atualize o status dos agendamentos pendentes apos o contato com o paciente ou fim da consulta.")
            
            if opcoes_para_edicao:
                col_ed1, col_ed2, col_ed3 = st.columns([2, 1, 1])
                
                with col_ed1:
                    agendamento_selecionado = st.selectbox("Selecione a Consulta", options=[""] + list(opcoes_para_edicao.keys()))
                with col_ed2:
                    novo_status_selecionado = st.selectbox("Novo Status", ["Agendado", "Confirmado", "Concluído", "Cancelado"])
                with col_ed3:
                    st.write("")
                    if st.button("Salvar Status", type="primary", use_container_width=True):
                        if agendamento_selecionado:
                            id_do_agendamento = opcoes_para_edicao[agendamento_selecionado]
                            atualizar_status_agendamento(id_do_agendamento, novo_status_selecionado)
                            st.success("Status atualizado com sucesso!")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("Selecione uma consulta.")
            else:
                st.info("Nenhum agendamento pendente de atualizacao no momento.")
                
        else:
            st.info("Nenhum agendamento encontrado para este medico.")

    with aba_solicitacoes:
        st.subheader("Caixa de Entrada - Agendamentos Online")
        st.markdown("Revise as solicitacoes de pacientes feitas pelo site. Ao aprovar, o paciente sera cadastrado automaticamente (se for novo) e o horario sera confirmado na agenda.")
        st.markdown("---")
        
        pendentes = buscar_agendamentos_pendentes(medico_alvo_id)
        
        if not pendentes:
            st.success("Tudo limpo! Nao ha novas solicitacoes de agendamento pela web no momento.")
        else:
            for req in pendentes:
                with st.container(border=True):
                    col1, col2, col3 = st.columns([3, 2, 2])
            
                    dt_str = req['data_hora_inicio'].replace("Z", "+00:00")
                    dt_obj = datetime.datetime.fromisoformat(dt_str)
                    data_formatada = dt_obj.strftime("%d/%m/%Y as %H:%M")
                    
                    with col1:
                        st.write(f"**Paciente:** {req.get('nome_solicitante', '-')}")
                        st.write(f"**Contato:** {req.get('telefone_solicitante', '-')} | {req.get('email_solicitante', '-')}")
                    
                    with col2:
                        st.write(f"**Data Solicitada:**")
                        st.write(f"{data_formatada}")
                        st.write(f"**Obs:** {req.get('observacoes', '-')}")
                    
                    with col3:
                        st.write("")
                        col3_a, col3_b = st.columns(2)
                        
                        if col3_a.button("Aprovar", key=f"apr_{req['id']}", type="primary", use_container_width=True):
                            aprovar_agendamento_web(
                                agendamento_id=req['id'], 
                                nome_paciente=req.get('nome_solicitante', ''), 
                                email_paciente=req.get('email_solicitante', ''), 
                                telefone_paciente=req.get('telefone_solicitante', '')
                            )
                            st.success("Aprovado! Registrado na agenda. Lembre-se de entrar em contato com o paciente.")
                            time.sleep(2)
                            st.rerun()
                            
                        if col3_b.button("Recusar", key=f"rec_{req['id']}", use_container_width=True):
                            recusar_agendamento_web(req['id'])
                            st.warning("Solicitacao recusada. O horario continua livre.")
                            time.sleep(1)
                            st.rerun()