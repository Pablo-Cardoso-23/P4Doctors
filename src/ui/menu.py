import streamlit as st
import datetime
import base64
from src.utils.security import verificar_acesso
from src.database.crud import (
    buscar_agendamentos,
    buscar_agendamentos_pendentes,
    buscar_medicos_vinculados
)

def render_logo_com_efeito(caminho_imagem):
    try:
        with open(caminho_imagem, "rb") as img_file:
            img_b64 = base64.b64encode(img_file.read()).decode()

        estilo_css = f"""
        <style>
        .logo-container {{
            display: flex;
            justify-content: center;
            padding-bottom: 20px;
        }}
        .logo-glow {{
            width: 100%;
            max-width: 350px;
            border-radius: 24px;
            padding: 15px;
            background: linear-gradient(135deg, rgba(139, 0, 0, 0.6) 0%, rgba(0, 0, 0, 0.9) 100%);
            box-shadow: 0 8px 32px rgba(255, 0, 0, 0.4), 0 0 15px rgba(255, 255, 255, 0.15);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            transition: transform 0.4s ease, box-shadow 0.4s ease;
        }}
        .logo-glow:hover {{
            transform: translateY(-5px);
            box-shadow: 0 12px 45px rgba(255, 0, 0, 0.6), 0 0 25px rgba(255, 255, 255, 0.3);
        }}
        </style>

        <div class="logo-container">
            <img class="logo-glow" src="data:image/png;base64,{img_b64}">
        </div>
        """
        st.markdown(estilo_css, unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("Imagem da logo não encontrada. Verifique o diretório 'img/'.")

if "usuario_autenticado" not in st.session_state or not st.session_state['usuario_autenticado']:
    st.switch_page("src/ui/forms.py")

verificar_acesso(perfis_permitidos=["Médico", "Secretária", "Administrativo"])

usuario_logado_id = st.session_state.get('usuario_id')
tipo_perfil = st.session_state.get('tipo_perfil')
nome_usuario = st.session_state.get('usuario_autenticado')

col_logo_1, col_logo_2, col_logo_3 = st.columns([1, 6, 1])
with col_logo_2:
    render_logo_com_efeito("img/P4.png")

if tipo_perfil == 'Médico':
    st.title(f"Bem-vindo(a), Dr(a). {nome_usuario}")
else:
    st.title(f"Bem-vindo(a), {nome_usuario}")

st.markdown("Acompanhe o resumo diário e acesse rapidamente as funcionalidades do sistema.")
st.markdown("---")

medico_alvo_id = None
if tipo_perfil in ['Secretária', 'Administrativo']:
    lista_medicos = buscar_medicos_vinculados(usuario_logado_id)
    if not lista_medicos:
        st.warning("Você ainda não possui vínculo com médicos para exibir o resumo.")
    else:
        medico_selecionado = st.selectbox(
            "Visão Geral da Agenda do Profissional:", 
            options=lista_medicos, 
            format_func=lambda m: m["nome"]
        )
        medico_alvo_id = medico_selecionado["id"]
else:
    medico_alvo_id = usuario_logado_id

hoje = datetime.date.today()
consultas_hoje = 0
pendentes_qtd = 0
proximas_consultas = []

if medico_alvo_id:
    pendentes_bd = buscar_agendamentos_pendentes(medico_alvo_id)
    pendentes_qtd = len(pendentes_bd) if pendentes_bd else 0
    eventos_bd = buscar_agendamentos(medico_alvo_id)
    if eventos_bd:
        for ev in eventos_bd:
            try:
                dt_inicio = datetime.datetime.fromisoformat(ev["start"].replace("Z", "+00:00"))
                if dt_inicio.date() == hoje and ev["status"] not in ["Cancelado", "Recusado"]:
                    consultas_hoje += 1
                    if ev["status"] in ["Agendado", "Confirmado"]:
                        proximas_consultas.append({
                            "hora": dt_inicio.strftime("%H:%M"),
                            "titulo": ev["title"],
                            "status": ev["status"]
                        })
            except Exception:
                pass
        
        proximas_consultas = sorted(proximas_consultas, key=lambda x: x["hora"])

st.subheader("Resumo do Dia")
c1, c2, c3 = st.columns(3)

with c1:
    st.metric(label="Consultas para Hoje", value=consultas_hoje)
with c2:
    st.metric(
        label="Solicitações Web", 
        value=pendentes_qtd, 
        delta=f"{pendentes_qtd} aguardando análise" if pendentes_qtd > 0 else "Tudo limpo", 
        delta_color="inverse" if pendentes_qtd > 0 else "normal"
    )
with c3:
    st.metric(label="Data Atual", value=hoje.strftime("%d/%m/%Y"))

st.write("")

st.subheader("Acesso Rápido")
col1, col2, col3, col4 = st.columns(4)

with col1:
    with st.container(border=True):
        st.markdown("#### Agenda")
        st.caption("Horários e web.")
        if st.button("Abrir", key="btn_ag", use_container_width=True):
            st.switch_page("src/ui/agenda.py")
with col2:
    with st.container(border=True):
        st.markdown("#### Pacientes")
        st.caption("Cadastros e edição.")
        if st.button("Abrir", key="btn_pac", use_container_width=True):
            st.switch_page("src/ui/gestao_pacientes.py")
with col3:
    with st.container(border=True):
        st.markdown("#### Prontuário")
        st.caption("Novo atendimento.")
        if st.button("Criar", key="btn_pront", type="primary", use_container_width=True):
            st.switch_page("src/ui/criarRelatorio.py")
with col4:
    with st.container(border=True):
        st.markdown("#### Painel")
        st.caption("Métricas financeiras.")
        if st.button("Ver", key="btn_dash", use_container_width=True):
            st.switch_page("src/ui/dashboard.py")

st.markdown("---")
st.subheader("Próximos Atendimentos")

if proximas_consultas:
    for consulta in proximas_consultas[:6]:
        if consulta['status'] == "Confirmado":
            st.success(f"**{consulta['hora']}** - {consulta['titulo']} (Confirmado)")
        else:
            st.info(f"**{consulta['hora']}** - {consulta['titulo']} (Agendado - Falta Confirmar)")
            
    if len(proximas_consultas) > 6:
        st.caption("Existem mais consultas hoje. Acesse a Agenda para ver a lista completa.")
else:
    st.info("Não há consultas pendentes de atendimento marcadas para o dia de hoje.")