import streamlit as st
import time
import datetime
from src.utils.security import verificar_acesso
from src.database.crud import (
    buscar_todos_pacientes_completo,
    atualizar_paciente_banco,
    excluir_paciente_banco
)

st.set_page_config(page_title="Gestão de Pacientes", layout="wide")

if not st.session_state.get('usuario_autenticado') or not st.session_state.get('usuario_id'):
    st.switch_page("src/ui/forms.py")

verificar_acesso(perfis_permitidos=["Médico", "Secretária", "Administrativo"])

st.title("Gestão de Pacientes")
st.markdown("Visualize, atualize os dados cadastrais ou remova registros inseridos incorretamente.")
st.markdown("---")

pacientes_bd = buscar_todos_pacientes_completo()

if not pacientes_bd:
    st.info("Nenhum paciente cadastrado no sistema no momento.")
    st.stop()

opcoes_pacientes = {}
for p in pacientes_bd:
    dados_p = p.get('pessoas', {})
    nome = dados_p.get('nome_completo', 'Sem Nome')
    cpf = dados_p.get('cpf', 'Sem CPF')
    rotulo = f"{nome} (CPF: {cpf})"
    opcoes_pacientes[rotulo] = p

paciente_selecionado = st.selectbox(
    "Selecione um paciente para gerenciar:",
    options=[""] + list(opcoes_pacientes.keys())
)

st.markdown("---")

if paciente_selecionado:
    paciente_dados = opcoes_pacientes[paciente_selecionado]
    pessoa_id = paciente_dados['pessoa_id']
    dados_pessoas = paciente_dados.get('pessoas', {})
    
    st.subheader("Edição de Cadastro")
    
    with st.form("form_editar_paciente"):
        col1, col2 = st.columns(2)
        
        with col1:
            novo_nome = st.text_input("Nome Completo", value=dados_pessoas.get('nome_completo', ''))
            novo_cpf = st.text_input("CPF", value=dados_pessoas.get('cpf', ''))
            novo_telefone = st.text_input("Telefone", value=dados_pessoas.get('telefone', ''))
            data_nasc_atual = paciente_dados.get('data_nascimento')
            dt_nasc_val = None
            if data_nasc_atual:
                try:
                    dt_nasc_val = datetime.datetime.strptime(data_nasc_atual, "%Y-%m-%d").date()
                except ValueError:
                    dt_nasc_val = None
                    
            nova_data_nasc = st.date_input(
                "Data de Nascimento", 
                value=dt_nasc_val, 
                min_value=datetime.date(1900, 1, 1), 
                max_value=datetime.date.today(), 
                format="DD/MM/YYYY"
            )
        
        with col2:
            novo_email = st.text_input("E-mail", value=paciente_dados.get('email', ''))
            
            tipos_sangue = ["Não Informado", "A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
            tipo_atual = paciente_dados.get('tipo_sanguíneo')
            idx_sangue = tipos_sangue.index(tipo_atual) if tipo_atual in tipos_sangue else 0
            novo_tipo_sangue = st.selectbox("Tipo Sanguíneo", options=tipos_sangue, index=idx_sangue)
            
            nova_obs = st.text_area("Observacoes Médicas Iniciais", value=paciente_dados.get('observacoes', ''), height=130)
        
        st.markdown("---")
        btn_salvar = st.form_submit_button("Salvar Alterações", type="primary", use_container_width=True)
        
        if btn_salvar:
            if not novo_nome:
                st.error("O Nome Completo e obrigatório.")
            else:
                data_nasc_str = nova_data_nasc.strftime("%Y-%m-%d") if nova_data_nasc else None
                
                try:
                    atualizar_paciente_banco(
                        pessoa_id=pessoa_id,
                        nome=novo_nome,
                        cpf=novo_cpf,
                        telefone=novo_telefone,
                        email=novo_email,
                        data_nascimento=data_nasc_str,
                        tipo_sanguineo=novo_tipo_sangue,
                        observacoes=nova_obs
                    )
                    st.success("Cadastro atualizado com sucesso!")
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao atualizar cadastro: {e}")

    st.write("")
    with st.expander("Zona de Perigo - Excluir Paciente"):
        st.warning("Atenção: A exclusão e permanente. Por regras de integridade do banco de dados, se o paciente possuir consultas ou prontuarios vinculados, a exclusão sera bloqueada.")
        
        if st.button("Excluir Paciente Definitivamente", type="secondary", use_container_width=True):
            try:
                excluir_paciente_banco(pessoa_id)
                st.success("Paciente excluido com sucesso do sistema.")
                time.sleep(1.5)
                st.rerun()
            except Exception as e:
                st.error("Erro: Não foi possivel excluir o paciente. Provavelmente ele ja possui agendamentos ou historico clinico registrado.")