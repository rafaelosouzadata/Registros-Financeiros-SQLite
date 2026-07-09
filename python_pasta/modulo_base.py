import subprocess
import streamlit as st

def exibir_menu(opcoes):

	# Definição de tipo Lista ou Dicionário
	lista = list(opcoes.keys()) if isinstance(opcoes, dict) else opcoes

	print()
	for i, item in enumerate(lista, 1):
		print(f"[{i}] - {item}")


	# Escolha de opção
	while True:
		try:
			numero = int(input("Escolha: ")) -1
			if  0 <= numero < len(lista):
				selecionado = lista[numero]
				break
			print("Digite um número válido!")
		except ValueError:
			print("Digite um número!")
			print()


	# Tratando Resultado

	valor = opcoes[selecionado] if isinstance(opcoes, dict) else selecionado

	if isinstance(valor, (list, tuple, dict)):
		espaçar()
		return exibir_menu(valor)

	elif callable(valor):
		espaçar()
		return valor()

	else:
		espaçar()
		print()
		return valor

def espaçar():
	print("\n" + ">=<"*20)

def dbt_run():

	try:
		resultado = subprocess.run(
			[	"dbt", "run",
				"--profiles-dir", "/app/dbt_pasta",
				"--project-dir", "/app/dbt_pasta"
			], 
			check=True, 
			text=True, 
			capture_output=True
			)
		return resultado.stdout

	except subprocess.CalledProcessError as e:
		print(e.stderr) 
		print(e.stdout)

		st.error("Veja o erro do DBT abaixo:")
		st.code(e.stderr if e.stderr else e.stdout) 

	return None

def dbt_seed():

	try:
		resultado = subprocess.run(
			[	"dbt", "seed",
				"--profiles-dir", "/app/dbt_pasta",
				"--project-dir", "/app/dbt_pasta"
			], 
			check=True, 
			text=True, 
			capture_output=True
			)
		return resultado.stdout

	except subprocess.CalledProcessError as e:
		print(e.stderr) 
		print(e.stdout)

		st.error("Veja o erro do DBT abaixo:")
		st.code(e.stderr if e.stderr else e.stdout) 


	return None

def dbt_dpeg():

	resultado = subprocess(
		["dbt", "dpeg"],
		check=True,
		text=True,
		capture_output=True)

	return None