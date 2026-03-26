import streamlit as st
import time

st.title("Solicitação de Acesso")
st.markdown("""
Preencha os dados abaixo para solicitar sua conta no **P4 Doctors**. 
Nossa equipe validará seu registro profissional e, em até 24h, você receberá um e-mail com suas credenciais temporárias de acesso.
""")

with st.form("form_solicitacao"):
    st.subheader("Dados Pessoais e Profissionais")

    nome = st.text_input("Nome Completo", placeholder="Ex Dr. Pablo James")
    email = st.text_input("E-mail Profissinal", placeholder="seuemail@email.com.br")

    col1, col2 = st.columns(2)

    with col1: 
        crm = st.text_input("Número do CRM", placeholder="Ex: 123456")
    with col2:
        uf_crm = st.selectbox("UF do CRM", ["AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"])

    especialidade = st.text_input("Especialidade Principal", placeholder="Ex: Cardiologia, Clínica Médica etc.")

    st.markdown("---")

    botao_enviar = st.form_submit_button("Enviar Solicitação", type="primary", use_container_width=True)

    if botao_enviar:
        if nome and email and crm and especialidade:
            st.success("Solicitação enviada com sucesso! Fique de olho na sua caixa de entrada e na pasta de spam. Obrigado por se juntar a P4!")
            time.sleep(3)
            st.switch_page("src/ui/sobre.py")
        else:
            st.warning("Por favor, preencha todos os campos obrigatórios para prosseguir.")
if st.button("Voltar para a página inicial"):
    st.switch_page("src/ui/sobre.py")
