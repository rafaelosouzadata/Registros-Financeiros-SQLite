from pathlib import Path
import os
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Date, Float, update, select, Engine
import pandas as pd
import streamlit as st

class ConexaoBanco:
    _instancia = None

    def __new__(cls, *args, **kwargs):
        if cls._instancia is None:
            cls._instancia = super().__new__(cls)
            cls._instancia._inicializar()

        return cls._instancia

    def _inicializar(self, tipo = True) -> None:
        if tipo:
            self.engine: Engine = self._pegar_engine()
        else:
            self.engine: Engine = create_engine("sqlite:///:memory:")

        self.metadata: MetaData = self._pegar_metadata()
    def _pegar_engine(self) -> Engine:
        caminho = Path(__file__).resolve().parent.parent / "Database.db"
        caminho = caminho.as_posix()
        engine = create_engine("sqlite:///" + str(caminho))
        return engine

    def _pegar_metadata(self) -> MetaData:
        metadata = MetaData()
        metadata.reflect(bind=self.engine)
        return metadata

def pegar_metadata(engine):
    metadata = MetaData()
    metadata.reflect(bind=engine)
    return metadata

# @st.cache_resource
# def conexao_banco():
#     caminho = Path(__file__).resolve().parent.parent / "Database.db"
#     caminho = caminho.as_posix()
#     engine = create_engine("sqlite:///" + str(caminho))
#     return engine

def salvar_bd(df, tabela, engine):

    df.to_sql(
        name=tabela,
        con=engine,
        if_exists='append',
        index=False
    )

# Criação de Tabelas ao Inicializar

@st.cache_data
def criar_tabelas():
    conexao = ConexaoBanco()

    conexao.metadata = definir_tabelas(conexao.metadata)
    conexao.metadata.create_all(conexao.engine)

def definir_tabelas(metadata):

    membros_tbl = Table(
        "membros",
        metadata,
        Column("id", Integer, primary_key=True, autoincrement=True),
        Column("nome", String(100), nullable=False),
        Column("sexo", String(10), nullable=False),
        Column("data_nascimento", Date, nullable=False),
        Column("cargo", String(20), nullable=True),
        extend_existing=True
    )

    dizimo_tbl = Table(
        "dizimos",
        metadata,
        Column("id", Integer, primary_key=True, autoincrement=True),
        Column("valor", Float, nullable=False),
        Column("id_membro", Integer, nullable=False),
        Column("data", Date, nullable=False),
        extend_existing=True
    )

    return metadata
