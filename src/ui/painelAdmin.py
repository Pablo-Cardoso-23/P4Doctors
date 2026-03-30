import streamlit as st
import pandas as pd

if st.session_state.get('tipo_perfil') != "Administrativo":
    st.error("Acesso negado. Esta página é restrita aos administradores do sistema.")
    st.stop()

st.title("Painel Administrativo")
st.markdown("Gestão de acessos, aprovação de cadastros e controle de profissionais.")
st.markdown("---")

with st.sidebar:
    if st.button("Sair da Conta", use_container_width=True):
                st.session_state['logged_in'] = False
                st.session_state['usuario_autenticado'] = ""

                st.rerun()
                st.switch_page(pagina_login)

col_kpi1, col_kpi2, col_kpi3 = st.columns(3)

with col_kpi1:
    st.metric("Usuários Ativos", "12")
with col_kpi2:
    st.metric("Solicitações Pendentes", "2")
with col_kpi3:
    st.metric("Licenças Disponíveis", "Ilimitado")

st.markdown("---")

aba_pendenciais, aba_usuarios_ativos, aba_novo_usuario = st.tabs([
    "Solicitações Pendentes",
    "Usuários Ativos",
    "Cadastrar Novo Usuário"
])

with aba_pendenciais:
    st.subheader("Aguardando Aprovação")
    st.markdown("Revise as solicitações de acesso realizadas pela página inicial.")

    pendencia_1 = {"nome": "Dr. Fernando Costa", "crm": "98765-SP", "espec": "Cardiologia", "data": "30/03/2026"}
    pendencia_2 = {"nome": "Dra. Juliana Silva", "crm": "54321-RJ", "espec": "Pediatria", "data": "29/03/2026"}

    def layout_linha_pendencia(dados):
        container = st.container(border=True)
        col1, col2, col3, col4 = container.columns([3, 2, 2, 3])
        col1.write(f"**{dados['nome']}**")
        col2.write(f"CRM: {dados['crm']}")
        col3.write(f"{dados['espec']}")

        col4_a, col4_b = col4.columns(2)
        if col4_a.button("Aprovar", key=f"apr_{dados['crm']}", type="primary"):
            st.success(f"Acesso liberado para {dados['nome']}. E-mail de credencial enviado.")
        if col4_b.button("Recusar", key=f"rec_{dados['crm']}"):
            st.warning(f"Solicitação de {dados['nome']} recusa e removida da fila.")
        
    layout_linha_pendencia(pendencia_1)
    layout_linha_pendencia(pendencia_2)
with aba_usuarios_ativos:
    st.subheader("Profissionais e Equipe no Sistema")

    df_ativos = pd.DataFrame({
        "Nome Completo": ["Pablo James", "Carlos Souza", "Ana Oliveira"],
        "Perfil": ["Administrativo", "Médico", "Recepcionista"],
        "CRM": ["-", "12345-DF", "-"],
        "Status": ["Ativo", "Ativo", "Bloqueado"],
        "Último Acesso": ["30/03/2026", "29/03/2026", "15/02/2026"]
    })

    st.dataframe(df_ativos, use_container_width=True, hide_index=True)
with aba_novo_usuario:
    st.subheader("Adicionar Usuário ao Sistema")
    st.markdown("Cadastre manualmente um profissional. Ele receberá um e-mail para definir a própria senha.")

    with st.form("form_cadastro_admin"):
        col1, col2 = st.columns(2)
        with col1:
            novo_nome = st.text_input("Nome Completo")
            novo_email = st.text_input("E-mail de Acesso")
        with col2:
            novo_perfil = st.selectbox("Perfil de Acesso", ["Médico", "Administrativo", "Secretária"])
            novo_crm = st.text_input("CRM (Deixe em branco se não for médico)")
        
        botao_cadastrar = st.form_submit_button("Criar Conta e Enviar Convite", type="primary", use_container_width=True)

        if botao_cadastrar:
            if novo_nome and novo_email:
                st.success(f"Conta para {novo_nome} criada com sucesso! O convite foi enviado para {novo_email}.")
            else:
                st.warning("Por favor, preencha o Nome e o E-mail obrigatórios.")
