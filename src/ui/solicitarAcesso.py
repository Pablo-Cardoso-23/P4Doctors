import streamlit as st
import time
from src.database.crud import registrar_solicitacao_medico

st.title("Solicitação de Acesso")
st.markdown("""
Preencha os dados abaixo para solicitar sua conta no **P4 Doctors**. 
Nossa equipe validará seu registro profissional e, em até 24h, você receberá um e-mail com suas credenciais temporárias de acesso.
""")

st.markdown("---")

st.subheader("Dados Pessoais e Profissionais")

col_nome, col_cpf = st.columns(2)
with col_nome:
    nome = st.text_input("Nome Completo", placeholder="Ex Dr. Pablo James")
with col_cpf:
    cpf = st.text_input("CPF", placeholder="000.000.000-00")

email = st.text_input("E-mail Profissional", placeholder="seuemail@email.com.br")

col1, col2 = st.columns(2)

with col1: 
    crm = st.text_input("Número do CRM", placeholder="Ex: 123456")
with col2:
    uf_crm = st.selectbox("UF do CRM", ["AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"])

lista_especialidades = [
    "Alergia e Imunologia", "Anestesiologia", "Angiologia", "Cardiologia", 
    "Cirurgia Geral", "Cirurgia Plástica", "Clínica Médica", "Dermatologia", 
    "Endocrinologia", "Gastroenterologia", "Geriatria", "Ginecologia e Obstetrícia", 
    "Infectologia", "Medicina de Família e Comunidade", "Medicina do Trabalho", 
    "Medicina Intensiva", "Neurologia", "Oftalmologia", "Ortopedia e Traumatologia", 
    "Otorrinolaringologia", "Pediatria", "Pneumologia", "Psiquiatria", 
    "Radiologia", "Reumatologia", "Urologia", "Outra (Especificar)"
]

especialidade_selecionada = st.selectbox("Especialidade Principal", lista_especialidades)

if especialidade_selecionada == "Outra (Especificar)":
    especialidade_digitada = st.text_input("Especifique sua Especialidade", placeholder="Digite sua especialidade")
    if especialidade_digitada:
        tratar_entrada = especialidade_digitada.strip().lower()
        lista_limpa = [esp.lower() for esp in lista_especialidades[:-1]]
        if tratar_entrada in lista_limpa:
            indice = lista_limpa.index(tratar_entrada)
            especialidade = lista_especialidades[indice]
            st.info(f"Notamos que a especialidade digitada já existe em nossa base. Ela foi padronizada automaticamente para: {especialidade}.")
        else:
            especialidade = especialidade_digitada.strip().title()
    else:
        especialidade = ""
else:
    especialidade = especialidade_selecionada

st.markdown("---")

botao_enviar = st.button("Enviar Solicitação", type="primary", use_container_width=True)

if botao_enviar:
    if nome and cpf and email and crm and especialidade:
        try:
            registrar_solicitacao_medico(nome, cpf, email, crm, uf_crm, especialidade)
            
            st.success("Solicitação enviada com sucesso! Fique de olho na sua caixa de entrada e na pasta de spam. Obrigado por se juntar à P4!")
            time.sleep(3)
            st.switch_page("src/ui/sobre.py")
        except Exception as e:
            st.error(f"Erro ao processar solicitação. Verifique se o CPF ou E-mail já estão cadastrados no sistema. Detalhes: {e}")
    else:
        st.warning("Por favor, preencha todos os campos obrigatórios para prosseguir.")

if st.button("Voltar para a página inicial"):
    st.switch_page("src/ui/sobre.py")