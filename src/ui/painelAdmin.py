import streamlit as st
import pandas as pd
import bcrypt
import string
import secrets
import time

from src.database.crud import (
    listar_todos_usuarios, 
    atualizar_status_usuario, 
    criar_usuario_completo,
    aprovar_solicitacao_com_senha
)

st.set_page_config(page_title="Painel Administrativo", layout="wide")

if not st.session_state.get('usuario_autenticado') or st.session_state.get('tipo_perfil') != "Administrativo":
    st.error("Acesso negado. Esta página é restrita aos administradores do sistema.")
    st.stop()

st.title("Painel Administrativo")
st.markdown("Gestão de acessos, aprovação de cadastros e controle de profissionais.")
st.markdown("---")

with st.sidebar:
    if st.button("Sair da Conta", use_container_width=True):
        st.session_state.clear()
        st.rerun()

todos_usuarios = listar_todos_usuarios()

usuarios_processados = []
for u in todos_usuarios:
    medicos_data = u.get('medicos')
    equipe_data = u.get('equipe_apoio')
    is_medico = bool(medicos_data)
    is_equipe = bool(equipe_data)
    
    if is_medico:
        dados_especificos = medicos_data[0] if isinstance(medicos_data, list) else medicos_data
        perfil = "Médico"
        email = dados_especificos.get('email', '')
        crm = dados_especificos.get('crm', '-')
    elif is_equipe:
        dados_especificos = equipe_data[0] if isinstance(equipe_data, list) else equipe_data
        perfil = dados_especificos.get('papel', 'Equipe')
        email = dados_especificos.get('email', '')
        crm = "-"
    else:
        continue

    usuarios_processados.append({
        "ID": u['id'],
        "Nome": u['nome_completo'],
        "CPF": u.get('cpf', '-'),
        "Perfil": perfil,
        "Email": email,
        "CRM": crm,
        "Status": u['status']
    })

lista_pendentes = [u for u in usuarios_processados if u['Status'] == 'Pendente']
lista_ativos_inativos = [u for u in usuarios_processados if u['Status'] in ['Ativo', 'Inativo']]

col_kpi1, col_kpi2, col_kpi3 = st.columns(3)

with col_kpi1:
    qtd_ativos = len([u for u in usuarios_processados if u['Status'] == 'Ativo'])
    st.metric("Usuários Ativos", str(qtd_ativos))
with col_kpi2:
    st.metric("Solicitações Pendentes", str(len(lista_pendentes)))
with col_kpi3:
    st.metric("Licenças Disponíveis", "Ilimitado")

st.markdown("---")

aba_pendencias, aba_usuarios, aba_novo_usuario = st.tabs([
    "Solicitações Pendentes",
    "Gestão de Usuários (Ativos/Inativos)",
    "Cadastrar Novo Usuário"
])

with aba_pendencias:
    st.subheader("Aguardando Aprovação")
    st.markdown("Revise as solicitações de acesso (cadastros realizados pela tela de login).")

    if 'senha_recem_gerada' in st.session_state:
        st.success(st.session_state['msg_sucesso'])
        st.info(f"A senha de acesso provisória gerada é: **{st.session_state['senha_recem_gerada']}**")
        st.warning("Copie a senha acima e envie ao profissional agora! Ela não será exibida novamente.")
        
        if st.button("OK, já copiei a senha", type="secondary", use_container_width=True):
            del st.session_state['senha_recem_gerada']
            del st.session_state['msg_sucesso']
            st.rerun()
        st.markdown("---")

    if not lista_pendentes:
        st.info("Não há nenhuma solicitação de acesso pendente no momento.")
    else:
        for pendencia in lista_pendentes:
            container = st.container(border=True)
            col1, col2, col3, col4 = container.columns([3, 2, 2, 3])
            col1.write(f"**{pendencia['Nome']}**")
            col2.write(f"{pendencia['Perfil']} | CPF: {pendencia['CPF']}")
            col3.write(f"CRM: {pendencia['CRM']}")

            col4_a, col4_b = col4.columns(2)
            if col4_a.button("Aprovar", key=f"apr_{pendencia['ID']}", type="primary"):
                caracteres = string.ascii_letters + string.digits + "!@#$%"
                senha_aleatoria = ''.join(secrets.choice(caracteres) for _ in range(10))
                senha_criptografada = bcrypt.hashpw(senha_aleatoria.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                
                aprovar_solicitacao_com_senha(pendencia['ID'], senha_criptografada)
                
                st.session_state['senha_recem_gerada'] = senha_aleatoria
                st.session_state['msg_sucesso'] = f"Acesso liberado para {pendencia['Nome']} com sucesso!"
                st.rerun()
                
            if col4_b.button("Recusar", key=f"rec_{pendencia['ID']}"):
                atualizar_status_usuario(pendencia['ID'], 'Recusado')
                st.warning(f"Solicitação de {pendencia['Nome']} recusada.")
                time.sleep(1)
                st.rerun()

with aba_usuarios:
    st.subheader("Profissionais e Equipe no Sistema")
    
    if lista_ativos_inativos:
        df_ativos = pd.DataFrame(lista_ativos_inativos).drop(columns=['ID'])
        st.dataframe(df_ativos, use_container_width=True, hide_index=True)
        
        st.markdown("#### Alterar Status de Acesso")
        col_acao1, col_acao2 = st.columns([3, 1])
        with col_acao1:
            usuario_selecionado = st.selectbox(
                "Selecione o profissional para inativar ou reativar", 
                options=lista_ativos_inativos, 
                format_func=lambda x: f"{x['Nome']} ({x['Status']})"
            )
        with col_acao2:
            st.write("")
            st.write("")
            if usuario_selecionado:
                if usuario_selecionado['Status'] == 'Ativo':
                    if st.button("Inativar", use_container_width=True):
                        atualizar_status_usuario(usuario_selecionado['ID'], 'Inativo')
                        st.success("Usuário inativado com sucesso!")
                        time.sleep(1)
                        st.rerun()
                else:
                    if st.button("Reativar Acesso", type="primary", use_container_width=True):
                        atualizar_status_usuario(usuario_selecionado['ID'], 'Ativo')
                        st.success("Usuário reativado com sucesso!")
                        time.sleep(1)
                        st.rerun()
    else:
        st.info("Nenhum usuário ativo ou inativo encontrado.")

with aba_novo_usuario:
    st.subheader("Adicionar Usuário ao Sistema")
    st.markdown("Cadastre manualmente um profissional.")

    with st.form("form_cadastro_admin"):
        col1, col2 = st.columns(2)
        with col1:
            novo_nome = st.text_input("Nome Completo")
            novo_cpf = st.text_input("CPF")
            novo_email = st.text_input("E-mail de Acesso")
        with col2:
            novo_perfil = st.selectbox("Perfil de Acesso", ["Médico", "Administrativo", "Secretária"])
            novo_crm = st.text_input("CRM (Deixe em branco se não for médico)")
            nova_especialidade = st.text_input("Especialidade (Apenas para médicos)")
        
        botao_cadastrar = st.form_submit_button("Criar Conta e Salvar", type="primary", use_container_width=True)

        if botao_cadastrar:
            if novo_nome and novo_email and novo_cpf:
                try:
                    caracteres = string.ascii_letters + string.digits + "!@#$%"
                    senha_aleatoria = ''.join(secrets.choice(caracteres) for _ in range(10))
                    senha_bytes = senha_aleatoria.encode('utf-8')
                    senha_criptografada = bcrypt.hashpw(senha_bytes, bcrypt.gensalt()).decode('utf-8')
                    
                    criar_usuario_completo(
                        nome=novo_nome,
                        cpf=novo_cpf,
                        email=novo_email,
                        perfil=novo_perfil,
                        crm=novo_crm if novo_perfil == 'Médico' else None,
                        especialidade=nova_especialidade if novo_perfil == 'Médico' else None,
                        senha_hash=senha_criptografada
                    )
                    
                    st.success(f"Conta para {novo_nome} criada com sucesso no banco de dados!")
                    st.info(f"A senha provisória gerada para este usuário é: **{senha_aleatoria}**")
                    st.warning("Copie esta senha e envie ao profissional agora. Por motivos de segurança, ela não será exibida novamente e não temos como recuperá-la depois!")
                    
                except Exception as e:
                    st.error(f"Erro ao cadastrar usuário no banco de dados. Verifique se o CPF ou E-mail já existem. Detalhes: {e}")
            else:
                st.warning("Por favor, preencha o Nome, CPF e o E-mail obrigatórios.")