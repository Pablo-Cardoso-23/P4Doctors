import streamlit as st
import base64

def get_base64_image(caminho_imagem):
    try:
        with open(caminho_imagem, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except FileNotFoundError:
        return ""

st.set_page_config(page_title="P4 Doctors - Conheça a Plataforma", layout="wide", initial_sidebar_state="collapsed")

img_hero_b64 = get_base64_image("img/homeimg.jpg")
tag_imagem = f'<img src="data:image/png;base64,{img_hero_b64}" alt="P4 Doctors Platform">' if img_hero_b64 else '<div style="color: white; border: 1px dashed rgba(255,255,255,0.3); padding: 100px; text-align: center; border-radius: 16px;">[Insira sua imagem aqui: img/hero_medico.png]</div>'

st.markdown(f"""
<style>
/* Importando uma tipografia premium do Google Fonts */
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;700;800&display=swap');

.block-container {{
    padding-top: 1rem;
    padding-bottom: 4rem;
    max-width: 1200px;
}}

.hero-wrapper {{
    position: relative;
    overflow: hidden; 
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: #0a0a0a; /* Fundo base escuro */
    border-radius: 24px;
    padding: 60px 50px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
    margin-top: 80px; 
    margin-bottom: 70px;
    gap: 50px;
}}

.hero-wrapper::before, .hero-wrapper::after {{
    content: "";
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    /* Utilizando estritamente o RGB (211, 47, 47) que corresponde à cor dos títulos */
    background: radial-gradient(circle at 50% 50%, rgba(211, 47, 47, 0.25), transparent 60%),
                radial-gradient(circle at 80% 20%, rgba(211, 47, 47, 0.20), transparent 50%);
    animation: cosmicFlow 25s infinite linear;
    z-index: 0;
    pointer-events: none;
    opacity: 0.5;
    transition: opacity 0.5s ease, animation-duration 0.5s ease;
}}
.hero-wrapper::after {{
    background: radial-gradient(circle at 20% 80%, rgba(211, 47, 47, 0.20), transparent 50%);
    animation: cosmicFlow 20s infinite linear reverse;
}}

.hero-wrapper:hover::before, .hero-wrapper:hover::after {{
    opacity: 0.9;
    animation-duration: 8s;
}}

@keyframes cosmicFlow {{
    0% {{ transform: rotate(0deg) scale(1); }}
    50% {{ transform: rotate(180deg) scale(1.2); }}
    100% {{ transform: rotate(360deg) scale(1); }}
}}

.hero-text {{
    flex: 1.2;
    text-align: left;
    z-index: 1; /* Fica acima da animação */
    position: relative;
}}
.hero-text h1 {{
    font-family: 'Montserrat', sans-serif;
    font-size: 3.5rem;
    font-weight: 800;
    margin-bottom: 20px;
    color: #ffffff;
    line-height: 1.1;
    letter-spacing: -1px;
}}
.hero-text p {{
    font-family: 'Montserrat', sans-serif;
    font-size: 1.15rem;
    font-weight: 300;
    color: #e0e0e0;
    line-height: 1.6;
}}
.hero-image {{
    flex: 1;
    display: flex;
    justify-content: flex-end;
    z-index: 1;
    position: relative;
}}
.hero-image img {{
    max-width: 100%;
    height: auto;
    border-radius: 16px;
    box-shadow: 0 15px 35px rgba(0, 0, 0, 0.4);
    object-fit: cover;
}}

@media (max-width: 900px) {{
    .hero-wrapper {{
        flex-direction: column;
        text-align: center;
        padding: 40px 30px;
        margin-top: 40px;
    }}
    .hero-text {{
        text-align: center;
        margin-bottom: 30px;
    }}
    .hero-image {{
        justify-content: center;
    }}
}}

.section-title {{
    text-align: center;
    color: var(--text-color);
    font-family: 'Montserrat', sans-serif;
    font-size: 2rem;
    font-weight: 700;
    margin-top: 20px;
    margin-bottom: 15px;
}}
.section-subtitle {{
    text-align: center;
    color: var(--text-color);
    font-family: 'Montserrat', sans-serif;
    opacity: 0.8;
    font-size: 1.1rem;
    margin-bottom: 60px;
    max-width: 800px;
    margin-left: auto;
    margin-right: auto;
}}

.feature-card {{
    background-color: var(--secondary-background-color);
    border: 1px solid rgba(211, 47, 47, 0.2);
    border-radius: 16px;
    padding: 35px 30px;
    height: 100%;
    box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    transition: transform 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease;
    margin-bottom: 30px;
}}
.feature-card:hover {{
    transform: translateY(-8px);
    box-shadow: 0 12px 25px rgba(211, 47, 47, 0.15);
    border-color: #D32F2F;
}}
.card-header {{
    color: #D32F2F; /* O vermelho base da marca (rgb 211, 47, 47) */
    font-family: 'Montserrat', sans-serif;
    font-size: 1.2rem;
    font-weight: 700;
    margin-bottom: 15px;
    text-transform: uppercase;
    letter-spacing: 1px;
}}
.card-text {{
    color: var(--text-color);
    opacity: 0.9;
    font-size: 1rem;
    line-height: 1.6;
}}

.cta-container {{
    background-color: var(--secondary-background-color);
    border: 1px solid rgba(211, 47, 47, 0.3);
    border-radius: 16px;
    padding: 60px 40px;
    text-align: center;
    margin-top: 100px;
    margin-bottom: 40px;
}}
.cta-title {{
    color: var(--text-color);
    font-family: 'Montserrat', sans-serif;
    font-size: 1.8rem;
    font-weight: 700;
    margin-bottom: 15px;
}}
</style>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="hero-wrapper">
    <div class="hero-text">
        <h1>P4 Doctors</h1>
        <p>A plataforma de gestão individual que atua como sua retaguarda. Centralize seu consultório, seus prontuários e seus ganhos em um ambiente seguro e desenhado exclusivamente para a rotina médica.</p>
    </div>
    <div class="hero-image">
        {tag_imagem}
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<div class='section-title'>A Realidade da Rotina Médica</div>", unsafe_allow_html=True)
st.markdown("""
<div class='section-subtitle'>
Sabemos que a rotina de um profissional de saúde é extremamente dinâmica. Entre plantões em diferentes hospitais, 
atendimentos em clínicas particulares e a pressão inerente à profissão, a gestão financeira e o controle de 
histórico acabam ficando em segundo plano.<br><br>
O <b>P4 Doctors</b> nasceu para devolver esse controle a você. Nós transformamos os dados brutos dos seus atendimentos 
em inteligência clínica e financeira, para que você possa focar apenas na excelência do tratamento aos seus pacientes.
</div>
""", unsafe_allow_html=True)

st.markdown("<div class='section-title'>Por que escolher nossa tecnologia?</div>", unsafe_allow_html=True)
st.markdown("<div class='section-subtitle'>Substituímos planilhas manuais e anotações dispersas por uma arquitetura inteligente.</div>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="feature-card">
        <div class="card-header">Dashboards Automáticos</div>
        <div class="card-text">Acompanhe seu faturamento e volume de consultas em tempo real. Os dados são processados e entregues em gráficos focados em resultados, separando convênios, consultas particulares e plantões.</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="feature-card">
        <div class="card-header">Privacidade Absoluta</div>
        <div class="card-text">Acesso rigorosamente restrito através de controle por papéis (RBAC) e criptografia de ponta a ponta. Os dados são exclusivamente seus e da sua equipe de apoio delegada.</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-card">
        <div class="card-header">Fluxo Ágil</div>
        <div class="card-text">Registre novos pacientes, atualize horários e salve faturamentos com apenas alguns cliques. Nossa interface foi desenvolvida visando o menor atrito possível durante os atendimentos.</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="feature-card">
        <div class="card-header">Operação 100% em Nuvem</div>
        <div class="card-text">Arquitetura altamente responsiva. Tenha o controle gerencial total na tela grande do seu consultório ou acesse rapidamente no celular durante um intervalo de plantão.</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
<div class="cta-container">
    <div class="cta-title">Pronto para transformar sua gestão médica?</div>
    <p style="color: var(--text-color); opacity: 0.8; margin-bottom: 30px;">Acesse sua conta ou solicite a validação do seu registro profissional.</p>
</div>
""", unsafe_allow_html=True)

col_espaco1, col_btn1, col_btn2, col_espaco2 = st.columns([2, 3, 3, 2])

with col_btn1:
    if st.button("Fazer Login e Acessar", type="secondary", use_container_width=True):
        st.switch_page("src/ui/forms.py")

with col_btn2:
    if st.button("Solicitar Acesso à Plataforma", type="primary", use_container_width=True):
        st.switch_page("src/ui/solicitarAcesso.py")

st.markdown("<br><hr><p style='text-align: center; color: var(--text-color); opacity: 0.5; font-size: 0.9rem; font-family: Montserrat, sans-serif;'>&copy; 2026 P4 Health Solutions. Todos os direitos reservados.</p>", unsafe_allow_html=True)