import pytest
from unittest.mock import MagicMock

# Importando as funções críticas que precisam ser testadas
from src.database.crud import (
    registrar_solicitacao_medico,
    aprovar_solicitacao_com_senha,
    atualizar_status_usuario
)

@pytest.fixture(autouse=True)
def mock_supabase(mocker):
    """
    Mock global para interceptar todas as chamadas ao Supabase.
    Garante que os testes não gravem dados no banco de produção.
    """
    mock_client = mocker.patch('src.database.crud.supabase')

    # Criando a cadeia de métodos do Supabase: table().insert().execute()
    mock_table = MagicMock()
    mock_insert = MagicMock()
    mock_update = MagicMock()
    mock_eq = MagicMock()
    mock_execute = MagicMock()

    # Configurando o retorno padrão simulando o banco de dados
    mock_execute.data = [{'id': '123e4567-e89b-12d3-a456-426614174000'}]

    # Conectando a simulação
    mock_eq.execute.return_value = mock_execute
    mock_update.eq.return_value = mock_eq
    mock_insert.execute.return_value = mock_execute
    mock_table.insert.return_value = mock_insert
    mock_table.update.return_value = mock_update
    mock_client.table.return_value = mock_table

    return mock_client

def test_registrar_solicitacao_medico_sucesso(mock_supabase):
    """
    TU01: Verifica se a criação de um novo médico chama as tabelas corretas
    e aplica a trava inicial de segurança.
    """
    resultado = registrar_solicitacao_medico(
        nome="Doutor Teste",
        cpf="11122233344",
        email="teste@p4health.com",
        crm="12345",
        uf_crm="DF",
        especialidade="Cardiologia"
    )

    assert resultado is True
    # Verifica se as tabelas pessoas e medicos foram acionadas
    mock_supabase.table.assert_any_call('pessoas')
    mock_supabase.table.assert_any_call('medicos')

def test_aprovar_solicitacao_com_senha(mock_supabase):
    """
    TU02: Verifica se o sistema atualiza o status para Ativo 
    e injeta a senha definitiva corretamente.
    """
    resultado = aprovar_solicitacao_com_senha(
        pessoa_id="123e4567-e89b-12d3-a456-426614174000",
        senha_hash="hash_criptografado_seguro_123"
    )

    assert resultado is True
    # Verifica se a tabela de pessoas foi atualizada
    mock_supabase.table.assert_any_call('pessoas')
    mock_supabase.table().update.assert_any_call({'status': 'Ativo'})
    
    # Verifica se a tabela de médicos recebeu a nova senha
    mock_supabase.table.assert_any_call('medicos')
    mock_supabase.table().update.assert_any_call({'senha_hash': 'hash_criptografado_seguro_123'})

def test_inativar_usuario(mock_supabase):
    """
    TU03: Verifica o funcionamento do Soft Delete (inativação).
    """
    resultado = atualizar_status_usuario(
        usuario_id="123e4567-e89b-12d3-a456-426614174000", 
        novo_status="Inativo"
    )

    assert resultado is True
    mock_supabase.table.assert_any_call('pessoas')
    mock_supabase.table().update.assert_called_with({'status': 'Inativo'})