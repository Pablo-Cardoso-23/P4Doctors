import streamlit as st

st.set_page_config(page_title="P4 Doctors - Sobre", layout="centered")

st.markdown("<h1 style='text-align: center;'>Bem-vindo ao P4 Doctors!</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: gray;'>O seu consultório, seus dados e seus ganhos centralizados em um só lugar.<h4/>", unsafe_allow_html=True)
st.markdown("---")

st.markdown("### A Realidade da Rotina Médica")
st.markdown("""
Sabemos que a rotina de um profissional de saúde é extremamente dinâmica. Entre plantões em diferentes hospitais, atendimentos em clínicas particulares e a pressão inerente à profissão, a gestão financeira e o controle de histórico acabam ficando em segundo plano. 

Muitas vezes, essas informações vitais ficam dispersas em anotações de papel, mensagens de texto ou planilhas genéricas que demandam tempo e energia para serem atualizadas.
""")

st.write("")

st.markdown("### O Nosso Propósito")
st.markdown("""
O **P4 Doctors** nasceu para devolver o controle ao profissional. Nós somos uma plataforma de gestão individual, projetada para atuar como o seu assistente de retaguarda. 

Nosso objetivo é transformar os dados brutos dos seus plantões e consultas em inteligência financeira e organização clínica. Nós cuidamos da burocracia e da consolidação das informações para que você possa focar no que realmente importa: a excelência no atendimento aos seus pacientes.
""")

st.markdown("""
### Por que usar o P4 Doctors?
Adeus planilhas confusas e anotações perdidas. Nós substituímos planilhas manuais e anotações dispersas por uma plataforma inteligente e segura, desenhada exclusivamente para a rotina ágil dos profissionais de saúde:

* **Dashboards Automáticos:** Veja seu faturamento e volume de consultas em tempo real.
* **Relatórios Ágeis:** Registre seus plantões e pacientes em poucos cliques.
* **Segurança e Privacidade:** Acesso restrito e focado no profissional.
* **Acesso em Qualquer Lugar:** Interface 100% em nuvem e responsiva. Funciona no computador do consultório ou no celular durante o plantão.
""")

st.markdown("---")

st.markdown("<h4 style='text-align: center;'>Pronto para transformar sua gestão médica?</h4>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.write("Já possui uma conta?")
    if st.button("Fazer Login e Acessar", type="secondary", use_container_width=True):
        st.switch_page("src/ui/forms.py")

with col2:
    st.write("Gostou do sistema, solicite já seu acesso!")
    if st.button("Solicitar Acesso", type="primary", use_container_width=True):
        st.switch_page("src/ui/solicitarAcesso.py")
