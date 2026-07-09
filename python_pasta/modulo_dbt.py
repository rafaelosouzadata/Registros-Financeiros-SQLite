from sqlalchemy import MetaData, Table, Column, Integer, String, Date, Float, update, select, extract, func
import modulo_database as mod_db
import pandas as pd
import streamlit as st
from pathlib import Path

def dbt_run(engine):

    metadata_engine = mod_db.pegar_metadata(engine)

    metadata_novas_tabelas = drop_create_tabelas(engine)
    stmts = definindo_stmts(metadata_engine, metadata_novas_tabelas)

    with engine.begin() as conn:
        dbt_seed(conn)
        for chave, valor in stmts.items():
            res = conn.execute(valor).mappings().all()
            df = pd.DataFrame(res)
            df.to_sql(
                name=chave,
                con=conn,
                if_exists="replace",
                index=False
                )

def dbt_seed(engine):
    pasta_seed = Path(__file__).resolve().parent / "seeds"

    for arquivo in pasta_seed.glob("*.csv"):
        df = pd.read_csv(arquivo)
        df.to_sql(
            name=arquivo.stem,
            con=engine,
            if_exists="replace",
            index=False)


def definindo_stmts(metadata_engine, metadata_novas_tabelas):

    dizimo_tbl = metadata_engine.tables["dizimos"]
    membros_tbl = metadata_engine.tables["membros"]

    dim_meses = metadata_engine.tables["dim_meses"]
    fct_dizimos_tbl = metadata_novas_tabelas.tables["fct_dizimos"]

    ano = extract('year', dizimo_tbl.c.data)
    mes = extract('month', dizimo_tbl.c.data)
    dia = extract('day', dizimo_tbl.c.data)

    ano_mes_formatado = func.cast(ano, String) + '-' + func.printf('%02d', mes)

    stmt_stg_dizimo = (
        select(
            dizimo_tbl.c.id.label('id_dizimo'),
            dizimo_tbl.c.id_membro,
            dizimo_tbl.c.valor,
            dizimo_tbl.c.data,
            ano.label('ano'),
            mes.label('mes'),
            dia.label('dia'),
            ano_mes_formatado.label('ano_mes')
        ).cte("stg_dizimo")
    )

    stmt_fct_dizimos = (
        select(
            stmt_stg_dizimo.c.id_dizimo,
            stmt_stg_dizimo.c.id_membro,
            stmt_stg_dizimo.c.valor,
            func.sum(stmt_stg_dizimo.c.valor).over(partition_by=stmt_stg_dizimo.c.ano_mes,
                                 order_by=stmt_stg_dizimo.c.data).label("soma_mensal"),
            func.sum(stmt_stg_dizimo.c.valor).over(partition_by=stmt_stg_dizimo.c.ano,
                                 order_by=stmt_stg_dizimo.c.data).label("soma_anual"),
            stmt_stg_dizimo.c.data,
            stmt_stg_dizimo.c.ano,
            stmt_stg_dizimo.c.mes,
            stmt_stg_dizimo.c.dia,
            stmt_stg_dizimo.c.ano_mes
        )
    )

    # stmt_gold_dizimos = (select(
    #             fct_dizimos_tbl.c.data,
    #             fct_dizimos_tbl.c.ano,
    #             fct_dizimos_tbl.c.mes,
    #             dim_meses.c.nome.label("nome_mes"),
    #             dim_meses.c.nome_reduzido.label("nome_mes_reduzido"),
    #             fct_dizimos_tbl.c.dia,
    #             fct_dizimos_tbl.c.valor,
    #             fct_dizimos_tbl.c.soma_mensal,
    #             fct_dizimos_tbl.c.soma_anual,
    #             fct_dizimos_tbl.c.id_membro,
    #             membros_tbl.c.nome.label("nome_membro"),
    #             membros_tbl.c.cargo
    #             )
    #         .join(membros_tbl, membros_tbl.c.id == fct_dizimos_tbl.c.id_membro)
    #         .join(dim_meses, fct_dizimos_tbl.c.mes == dim_meses.c.id)
    #         .order_by(fct_dizimos_tbl.c.data)
    #         )

    stmts = {"fct_dizimos":stmt_fct_dizimos
             # "golden_dizimos":stmt_gold_dizimos
            }

    return stmts

def drop_create_tabelas(engine):

    metadata = MetaData()

    # stg_dizimo = Table(
    #     "stg_dizimo",
    #     metadata,
    #     Column("id_dizimo", Integer, primary_key=True),
    #     Column("id_membro", Integer),
    #     Column("valor", Float),
    #     Column("data", Date),
    #     Column("ano", Integer),
    #     Column("mes", Integer),
    #     Column("dia", Integer),
    #     Column("ano-mes", String)
    #     )

    fct_dizimos = Table(
        "fct_dizimos",
        metadata,
        Column("id_dizimo", Integer, primary_key=True),
        Column("id_membro", Integer),
        Column("valor", Float),
        Column("soma_mensal", Float),
        Column("soma_anual", Float),
        Column("data", Date),
        Column("ano", Integer),
        Column("mes", Integer),
        Column("dia", Integer),
        Column("ano-mes", String)
        )

    with engine.begin() as conn:
        metadata.drop_all(conn)
        metadata.create_all(conn)

    return metadata
