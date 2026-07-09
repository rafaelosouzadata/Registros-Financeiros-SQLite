import pandas as pd
import plotly.express as px
from sqlalchemy import *
from python_pasta.modulo_database import *
import streamlit as st

def grafico_tabela_comum(tabela, engine=None):

    if engine is None:
        engine = conexao_banco()

    metadata = pegar_metadata(engine)
    tabela = metadata.tables[tabela]

    stmt = select(tabela)

    with engine.begin() as conn:
        res = conn.execute(stmt).mappings().all()
        return pd.DataFrame([dict(linha) for linha in res])

def grafico_tabela_dizimos(engine=None):

    if engine is None:
        engine = conexao_banco()

    metadata = pegar_metadata(engine)
    dizimos = metadata.tables["dizimos"]
    membros = metadata.tables["membros"]

    stmt = (select(membros.c.nome,
                   dizimos.c.valor,
                   dizimos.c.data
                   )
            .join(membros, membros.c.id == dizimos.c.id_membro)
            .order_by(dizimos.c.data.desc())
            )

    with engine.begin() as conn:
        res = conn.execute(stmt).mappings().all()
        df = pd.DataFrame(res)

    return df

# Gráficos Relacionado a Membros

def grafico_pie_sexo(engine=None):

    if engine is None:
        engine = conexao_banco()

    metadata = pegar_metadata(engine)
    membros = metadata.tables["membros"]

    stmt = (select(membros.c.sexo,
                   func.count(membros.c.id).label("quantidade")
                   )
            .group_by(membros.c.sexo)
            )

    with engine.begin() as conn:
        res = conn.execute(stmt).mappings().all()
        df = pd.DataFrame(res)

    cores_customizadas = {
    "HOMEM": "#1f77b4",  
    "MULHER": "#e377c2"   
    }

    pie_sexo = px.pie(df,
                      names="sexo",
                      values="quantidade",
                      color="sexo",
                      color_discrete_map=cores_customizadas)
    return pie_sexo

def grafico_pie_cargos(engine=None):
    
    if engine is None:
        engine = conexao_banco()

    metadata = pegar_metadata(engine)
    membros = metadata.tables["membros"]

    stmt = (select(membros.c.cargo,
                   func.count(membros.c.id).label("quantidade")
                   )
            .group_by(membros.c.cargo)
            )

    with engine.begin() as conn:
        res = conn.execute(stmt).mappings().all()
        df= pd.DataFrame(res)

    pie_cargos = px.pie(df,
                        names="cargo",
                        values="quantidade",
                        color="cargo")

    return pie_cargos

# Gráficos Relacionados a Dízimo

def cte_gold_dizimos(engine):

    if engine is None:
        engine = conexao_banco()

    metadata = pegar_metadata(engine)
    fct_dizimos = metadata.tables["fct_dizimos"]
    membros = metadata.tables["membros"]
    dim_meses =  metadata.tables["dim_meses"]

    stmt_gold_dizimos = (select(
                fct_dizimos.c.data,
                fct_dizimos.c.ano_mes,
                fct_dizimos.c.ano,
                fct_dizimos.c.mes,
                dim_meses.c.nome.label("nome_mes"),
                dim_meses.c.nome_reduzido.label("nome_mes_reduzido"),
                fct_dizimos.c.dia,
                fct_dizimos.c.valor,
                fct_dizimos.c.id_membro,
                membros.c.nome.label("nome_membro"),
                membros.c.cargo
                )
            .join(membros, membros.c.id == fct_dizimos.c.id_membro)
            .join(dim_meses, fct_dizimos.c.mes == dim_meses.c.id)
            .order_by(fct_dizimos.c.data).cte("gold_dizimos")
            )

    return stmt_gold_dizimos

def tabela_dizimo_membros_obreiros(engine):

    if engine is None:
        engine = conexao_banco()

    metadata = pegar_metadata(engine)

    stmt_gold_dizimos = cte_gold_dizimos(engine)

    stmt_dizimo_membros = (select(stmt_gold_dizimos.c.data,
                                  stmt_gold_dizimos.c.nome_membro.label("nome"),
                                  stmt_gold_dizimos.c.valor,
                                  func.sum(stmt_gold_dizimos.c.valor)
                                        .over(partition_by=stmt_gold_dizimos.c.ano_mes,
                                              order_by=stmt_gold_dizimos.c.data).label("soma_total"))
                           .where(stmt_gold_dizimos.c.cargo == "MEMBRO")
                           .order_by(stmt_gold_dizimos.c.data, stmt_gold_dizimos.c.nome_membro)
                            )

    stmt_dizimo_obreiros = (select(stmt_gold_dizimos.c.data,
                                   stmt_gold_dizimos.c.cargo,
                                   stmt_gold_dizimos.c.nome_membro.label("nome"),
                                   stmt_gold_dizimos.c.valor,
                                   func.sum(stmt_gold_dizimos.c.valor)
                                        .over(partition_by=stmt_gold_dizimos.c.ano_mes,
                                              order_by=stmt_gold_dizimos.c.data).label("soma_total"))
                           .where(not_(stmt_gold_dizimos.c.cargo == "MEMBRO"))
                           .order_by(stmt_gold_dizimos.c.data, stmt_gold_dizimos.c.nome_membro)
                            )

    with engine.begin() as conn:
        dizimo_membros = pd.DataFrame(conn.execute(stmt_dizimo_membros).mappings().all())
        dizimo_obreiros = pd.DataFrame(conn.execute(stmt_dizimo_obreiros).mappings().all())

    return dizimo_membros, dizimo_obreiros

def gold_dizimos(engine=None):

    if engine is None:
        engine = conexao_banco()

    metadata = pegar_metadata(engine)
    fct_dizimos = metadata.tables["fct_dizimos"]
    dim_membros = metadata.tables["membros"]
    dim_meses =  metadata.tables["dim_meses"]

    stmt = (select(
                fct_dizimos.c.data,
                fct_dizimos.c.ano_mes,
                fct_dizimos.c.ano,
                fct_dizimos.c.mes,
                dim_meses.c.nome.label("nome_mes"),
                dim_meses.c.nome_reduzido.label("nome_mes_reduzido"),
                fct_dizimos.c.dia,
                fct_dizimos.c.valor,
                fct_dizimos.c.soma_mensal,
                fct_dizimos.c.soma_anual,
                fct_dizimos.c.id_membro,
                dim_membros.c.nome.label("nome_membro"),
                dim_membros.c.cargo
                )
            .join(dim_membros, dim_membros.c.id == fct_dizimos.c.id_membro)
            .join(dim_meses, fct_dizimos.c.mes == dim_meses.c.id)
            .order_by(fct_dizimos.c.data)
            )
    with engine.begin() as conn:
        res = conn.execute(stmt).mappings().all()
        df = pd.DataFrame(res)
    return df

@st.fragment
def grafico_saldo_por_mesano(engine=None):

    if engine is None:
        engine = conexao_banco()

    metadata = pegar_metadata(engine)
    fct_dizimos = metadata.tables["fct_dizimos"]
    dim_membros = metadata.tables["membros"]
    dim_meses =  metadata.tables["dim_meses"]

    stmt = (select(
                fct_dizimos.c.data,
                fct_dizimos.c.ano,
                fct_dizimos.c.mes,
                fct_dizimos.c.ano_mes,
                dim_meses.c.nome.label("nome_mes"),
                dim_meses.c.nome_reduzido.label("nome_mes_reduzido"),
                fct_dizimos.c.dia,
                fct_dizimos.c.valor,
                fct_dizimos.c.soma_mensal,
                fct_dizimos.c.soma_anual
                )
            .join(dim_meses, fct_dizimos.c.mes == dim_meses.c.id)
        )   .order_by(fct_dizimos.c.data)

    

    with engine.begin() as conn:
        res = conn.execute(stmt).mappings().all()
        df = pd.DataFrame(res)

    fig = px.bar(df, y="valor", x="data", color="nome_mes")
    return fig

def grafico_saldo_mes(engine=None):
    if engine is None:
        engine = conexao_banco()

    metadata = pegar_metadata(engine)
    fct_dizimos = metadata.tables["fct_dizimos"]
    dim_membros = metadata.tables["membros"]
    dim_meses =  metadata.tables["dim_meses"]

    
    stmt2 = (select(
                fct_dizimos.c.ano_mes,
                fct_dizimos.c.mes,
                dim_meses.c.nome.label("nome_mes"),
                dim_meses.c.nome_reduzido.label("nome_mes_reduzido"),
                func.max(fct_dizimos.c.soma_mensal).label("valor")
                )
            .join(dim_meses, fct_dizimos.c.mes == dim_meses.c.id)
            .group_by(fct_dizimos.c.ano_mes,
                      fct_dizimos.c.mes,
                      dim_meses.c.nome,
                      dim_meses.c.nome_reduzido)
            .order_by(fct_dizimos.c.ano_mes)
            )

    with engine.begin() as conn:    
        res2 = conn.execute(stmt2).mappings().all()
        df2 = pd.DataFrame(res2)

    fig2 = px.bar(df2, y = "valor", x = "ano_mes", color="nome_mes", title="Valor Mensal")

    return fig2

