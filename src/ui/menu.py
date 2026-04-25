import streamlit as st
import time
import datetime
import base64
from src.utils.security import verificar_acesso

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
            /* Fundo: Gradiente do Vermelho Escuro para o Preto Sólido */
            background: linear-gradient(135deg, rgba(139, 0, 0, 0.6) 0%, rgba(0, 0, 0, 0.9) 100%);
            /* Glow: Brilho Vermelho intenso com um toque de Branco nas bordas */
            box-shadow: 0 8px 32px rgba(255, 0, 0, 0.4), 0 0 15px rgba(255, 255, 255, 0.15);
            backdrop-filter: blur(12px);
            /* Borda: Branco translúcido para efeito de vidro */
            border: 1px solid rgba(255, 255, 255, 0.2);
            transition: transform 0.4s ease, box-shadow 0.4s ease;
        }}
        .logo-glow:hover {{
            transform: translateY(-5px);
            /* No hover, o brilho vermelho expande e o branco fica mais nítido */
            box-shadow: 0 12px 45px rgba(255, 0, 0, 0.6), 0 0 25px rgba(255, 255, 255, 0.3);
        }}
        </style>

        <div class="logo-container">
            <img class="logo-glow" src="data:image/png;base64,{img_b64}">
        </div>
        """
        st.markdown(estilo_css, unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("Imagem não encontrada. Verifique o caminho.")

TIMEOUT_MINUTOS = 30
agora = datetime.datetime.now()

if "usuario_autenticado" not in st.session_state or not st.session_state['usuario_autenticado']:
    st.switch_page("src/ui/forms.py")

verificar_acesso(perfis_permitidos=["Médico", "Secretária"])

col_logo_1, col_logo_2, col_logo_3 = st.columns([1, 6, 1])
with col_logo_2:
    render_logo_com_efeito("img/P4.png")

st.title("P4 Doctors - Central de Profissional")
st.markdown(f"#### Bem-vindo(a), Dr(a). {st.session_state['usuario_autenticado']}")
st.markdown("Utilize os atalhos abaixo para navegar pelo sistema sistema ou utilize o menu lateral.")

st.markdown("---")

st.markdown("Acesso Rápido")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("#### Agenda")
    st.markdown("Gerencie seus horários e plantões.")
    if st.button("Abrir Agenda", use_container_width=True):
        st.switch_page("src/ui/agenda.py")
with col2:
    st.markdown("#### Novo Relatório")
    st.markdown("Registre consultas e faturamentos.")
    if st.button("Criar Registro", type="primary", use_container_width=True):
        st.switch_page("src/ui/criarRelatorio.py")
with col3:
    st.markdown("#### Dashboards")
    st.markdown("Analise seus ganhos e volume.")
    if st.button("Ver Métricas", use_container_width=True):
        st.switch_page("src/ui/dashboard.py")

st.markdown("---")

st.markdown("#### Resumo de Hoje")
data_atual = agora.strftime("%d/%m/%Y")

st.info(f"Data: {data_atual}. Você possui N consultas agendadas e N platão pendente de registro no sistema.")
