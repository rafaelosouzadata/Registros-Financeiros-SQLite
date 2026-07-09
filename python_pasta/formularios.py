import pandas as pd
import streamlit as st
import datetime
from python_pasta.modulo_database import *

def registro_membros():
	data_atual = datetime.date.today()
	data_minima = datetime.date(1900, 1, 1)

	with st.form("Cadastro de Membros"):
		nome = st.text_input("Escreva o nome completo")
		
		col1, col2 = st.columns(2)

		with col1:
			data_nascimento = st.date_input("Escolha a data de nascimento",
									value=data_atual,
									min_value=data_minima,
									max_value=data_atual
									)
		with col2:
			sexo = st.radio("Sexo",["Homem","Mulher"])

		cargos = ["Membro","Diácono","Presibítero","Pastor","Missionário"]
		cargo = st.selectbox("Escolha o Cargo", cargos)


		if st.form_submit_button("Enviar"):

			with st.spinner("Salvando Dados..."):
				cadastro = [x.upper() for x in [nome,sexo,cargo]]
				cadastro.append(data_nascimento)

				df = pd.DataFrame([cadastro], columns=["nome","sexo","cargo","data_nascimento"])

				engine = conexao_banco()
				salvar_bd(df, "membros", engine)

			st.success(f"""Cadastro Concluído:
						   \nnome: {nome}
						   \ndata: {data_nascimento.strftime("%Y-%m-%d")}
						   \nsexo: {sexo}
						   \ncargo: {cargo}""")

# id, valor, id_membro, data
def registro_dizimo():
	# Orgnaização das Tabelas Dimensão

	engine = conexao_banco()
	metadata = pegar_metadata(engine)
	membros = metadata.tables["membros"]

	stmt = (select(membros.c.id,
						  membros.c.nome)
			.order_by(membros.c.nome))

	with engine.begin() as conn:
		membros_df = pd.DataFrame(conn.execute(stmt).mappings().all())


	with st.form("Registro Dízimo"):
		# Formulário

		membros_dict = dict(zip(membros_df["nome"].tolist(), membros_df["id"].tolist()))
		membro = st.selectbox("Membro dizimista", membros_dict.keys())

		col1, col2 = st.columns(2)
		with col1:
			valor = st.number_input("Valor",
									min_value=0.0,
									step=0.5,
									format="%.2f")

		with col2:
			data_atual = datetime.date.today()
			data_minima = datetime.date(1900, 1, 1)
			data = st.date_input("Data do pagamento",
									value=data_atual,
									min_value=data_minima
									# max_value=data_atual
									)

		if st.form_submit_button("Enviar"):
			
			with st.spinner("Salvando Dados..."):
				membro = membros_dict[membro]
				cadastro = [membro, valor, data]
				df = pd.DataFrame([cadastro], columns=["id_membro","valor","data"])

				salvar_bd(df, "dizimos", engine)

			st.success(f"""Dados Salvos com Sucesso:
						   \nmembro: {membro}
						   \ndata: {data.strftime("%Y-%m-%d")}
						   \nvalor: {valor}""")