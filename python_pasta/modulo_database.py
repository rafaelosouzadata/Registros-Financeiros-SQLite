from pathlib import Path
import os
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Date, Float, update, select
import pandas as pd
import streamlit as st

# engine -> metadata
def pegar_metadata(engine):
	metadata = MetaData(); metadata.reflect(bind=engine)
	return metadata

# -> engine
@st.cache_resource
def conexao_banco():
	caminho = Path(__file__).resolve().parent / "Database.db"
	engine = create_engine("sqlite:////" + str(caminho))
	return engine

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
	engine = conexao_banco()
	metadata = pegar_metadata(engine)

	metadata = definir_tabelas(metadata)
	metadata.create_all(engine)

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

	