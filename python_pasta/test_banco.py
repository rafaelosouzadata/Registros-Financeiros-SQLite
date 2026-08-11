import pytest
import modulo_database as mod_db
from sqlalchemy import String, Engine, MetaData, create_engine, Table

def test_conexao_tipos():
    conexao = mod_db.ConexaoBanco(False)

    assert isinstance(conexao, mod_db.ConexaoBanco)
    assert isinstance(conexao.engine, Engine)
    assert isinstance(conexao.metadata, MetaData)

def test_conexao_singleton():
    conexao1 = mod_db.ConexaoBanco()
    conexao2 = mod_db.ConexaoBanco()

    assert conexao1 is conexao2

def test_definir_tabelas_registra_tabelas_corretamente():
    # Executa a função passando o metadata limpo
    metadata = MetaData()
    meta =  mod_db.definir_tabelas(metadata)

    # 1. Verifica se as tabelas existem no dicionário .tables do MetaData
    assert "membros" in meta.tables
    assert "dizimos" in meta.tables

    # 2. Obtém os objetos Table para inspecionar as colunas
    membros = meta.tables["membros"]
    dizimos = meta.tables["dizimos"]

    assert isinstance(membros, Table)
    assert isinstance(dizimos, Table)


def test_estrutura_colunas_tabela_membros():

    metadata = MetaData()
    meta =  mod_db.definir_tabelas(metadata)
    membros = meta.tables["membros"]

    # Verifica os nomes das colunas presentes
    colunas_esperadas = {"id", "nome", "sexo", "data_nascimento", , "cargo"}
    assert set(membros.columns.keys()) == colunas_esperadas

def test_criacao_das_tabelas_no_banco_sqlite_em_memoria():
    metadata = MetaData()
    meta =  mod_db.definir_tabelas(metadata)

    # Cria uma engine temporária de SQLite em memória exclusivamente para este teste
    engine = create_engine("sqlite:///:memory:")

    # Tenta criar fisicamente as tabelas no banco de dados temporário
    # Se houver erro de sintaxe ou incompatibilidade no DDL, esta linha lançará uma exceção
    meta.create_all(bind=engine)

    # Inspeciona o banco para confirmar a criação física das tabelas
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tabelas_criadas = inspector.get_table_names()

    assert "membros" in tabelas_criadas
    assert "dizimos" in tabelas_criadas
