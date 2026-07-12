import sys
from pathlib import Path

caminho_modulos = Path(__file__).resolve().parent / "python_pasta"
sys.path.append(str(caminho_modulos))

import datetime
import streamlit as st
import pandas as pd
import modulo_database as mod_db
import modulo_base as mod_base
import formularios as mod_form
import modulo_dbt as mod_dbt
import graficos as mod_graph
import plotly.express as px
from streamlit_option_menu import option_menu
from sqlalchemy import *


st.set_page_config(
    page_title="Financeiro Igreja",       
    page_icon="📊",                        
    layout="wide",                        
    initial_sidebar_state="expanded"
)
mod_db.criar_tabelas()
engine = mod_db.conexao_banco()

with st.sidebar:
    pags = ["Menu","Cadastro", "Visualização"]
    # pagina = st.radio("Navegação", pags)

    pagina = option_menu(
        menu_title=None,                            
        options=pags,  
        default_index=0,
        orientation="vertical",
        )

if st.button("Atualizar Dados"):
    with st.spinner("Atualizando Dados..."):
        mod_dbt.dbt_seed(engine)
        df = mod_dbt.dbt_run(engine)
        st.success("Dados Atualizados!")
        st.rerun()

if pagina == "Menu":
    st.title("Em Desenvolvimento")
    st.header("Abra a lateral esquerda para mais opções")
if pagina == "Cadastro":
    aba = option_menu(
        menu_title=None,                            
        options=["Membros", "Dízimos"],  
        default_index=0,                 
        orientation="horizontal",        
        )
    if aba == "Membros":
        st.title(f"Cadastro de Membros")
        mod_form.registro_membros()

    if aba == "Dízimos":
        st.title(f"Cadastro de Dízimos")
        mod_form.registro_dizimo()

if pagina == "Visualização":

        aba = option_menu(
        menu_title=None,                 
        options=["Membros", "Dízimos"],  
        default_index=0,                               
        orientation="horizontal",                      
        )

        if aba == "Membros":

            coluna1, coluna2 = st.columns(2)

            with coluna1:
                pie_sexo = mod_graph.grafico_pie_sexo(engine)
                st.plotly_chart(pie_sexo)

            with coluna2:

                pie_cargos = mod_graph.grafico_pie_cargos(engine)   
                st.plotly_chart(pie_cargos)
                
            df = pd.DataFrame(mod_graph.grafico_tabela_comum("membros"))
            st.dataframe(df)
        
        if aba == "Dízimos":
            with engine.begin() as conn:
                cte = mod_graph.cte_gold_dizimos(conn)
                stmt = select(distinct(cte.c.ano_mes).label("ano_mes")).order_by(cte.c.ano_mes.desc())
                res = conn.execute(stmt).mappings().all()
                df = pd.DataFrame(res)

            obreiros_membros_ano_mes = st.selectbox("Escolha o Mês", df)
            coluna1, coluna2 = st.columns(2)
            dizimo_membros, dizimo_obreiros = mod_graph.tabela_dizimo_membros_obreiros(engine, obreiros_membros_ano_mes)

            with coluna1:
                st.subheader("Dízimo dos Membros")
                st.dataframe(dizimo_membros)
                
                try:
                    total_membros = dizimo_membros["valor"].sum()
                except:
                    total_membros = 0
                st.write(f"Valor Total: {total_membros}")

            with coluna2:
                st.subheader("Dízimo dos Obreiros")
                st.dataframe(dizimo_obreiros)

                try:
                    total_obreiros = dizimo_obreiros["valor"].sum()
                except:
                    total_obreiros = 0 
                st.write(f"Valor Total: {total_obreiros}")

            fig2 = mod_graph.grafico_saldo_mes(engine)
            st.plotly_chart(fig2)

            fig = mod_graph.grafico_saldo_por_mesano(engine)
            st.plotly_chart(fig)