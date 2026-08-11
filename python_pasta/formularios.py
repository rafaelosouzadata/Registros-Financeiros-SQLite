from ast import UnaryOp
from ctypes import alignment
from pydoc import text
from pandas._libs import pandas

import pandas as pd

import streamlit as st
from datetime import datetime, date, time
import modulo_database as mod_db
from dataclasses import dataclass, field
from sqlalchemy import select

def registro_membros():
    data_atual = datetime.now().date()
    data_minima = date(1900, 1, 1)

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

                conexao = ConexaoBanco()
                engine = conexao.engine
                salvar_bd(df, "membros", engine)

            st.success(f"""Cadastro Concluído:
                           \nnome: {nome}
                           \ndata: {data_nascimento.strftime("%Y-%m-%d")}
                           \nsexo: {sexo}
                           \ncargo: {cargo}""")

# id, valor, id_membro, data
def registro_dizimo():
    # Orgnaização das Tabelas Dimensão

    conexao = mod_db.ConexaoBanco()
    engine = conexao.engine
    metadata = conexao.metadata

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
            data_atual = datetime.now().date()
            data_minima = date(1900, 1, 1)
            data = st.date_input("Data do pagamento",
                                    value=data_atual,
                                    min_value=data_minima,
                                    max_value=data_atual
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


@dataclass
class Cargo:
    nome: str

    def __post_init__(self):
        self.nome = self.nome.strip().upper()

@dataclass
class Membro:
    nome: str
    sexo: str
    data_nascimento: date
    id_cargo: int


    def __post_init__(self):

        self.nome = self.nome.strip().upper()
        self.sexo = self.sexo.strip().upper()

@dataclass
class Dizimo:
    valor: float
    data: date
    id_membro: int

def limpeza_dados(tabela, **kwargs):

    def _empacotar_membros(nome, id_cargo, sexo, data_nascimento):
        registro = Membro(
            nome=nome,
            id_cargo=id_cargo,
            sexo=sexo,
            data_nascimento=data_nascimento
        )

        return registro

    def _empacotar_cargos(nome):
        registro = Cargo(
            nome=nome,
        )

        return registro

    def _empacotar_dizimos(valor, data, id_membro):
        registro = Dizimo(
            valor = valor,
            data = data,
            id_membro = id_membro,
        )

        return registro

    if tabela == "membros":
        return _empacotar_membros(**kwargs)

    elif tabela == "cargos":
        return _empacotar_cargos(**kwargs)

    elif tabela == "dizimos":
        return _empacotar_dizimos(**kwargs)

    else:
        raise ValueError(f"Tabela '{tabela}' é inválida ou não suportada.")


class SalvarDados:

    def __init__(self, conexao):
        self.engine = conexao.engine
        self.metadata = conexao.metadata

class ConexaoBanco:

    def __init__(self):
        self.engine = self._pegar_engine
        self.metadata = self._pegar_metadata

    def _pegar_engine(self):
        caminho = Path(__file__).resolve().parent.parent / "Database.db"
        caminho = caminho.as_posix()
        engine = create_engine("sqlite:///" + str(caminho))
        return engine

    def _pegar_metadata(self):
        metadata = MetaData(); metadata.reflect(bind=self.engine)
        return metadata

# ============== FLET ==============
import flet as ft

def container_padrao(conteudo):
    container = ft.Container(
        expand= True,
        content=conteudo,
        padding= 20,
        bgcolor = ft.Colors.BLUE_GREY_900,
        border_radius = 12
    )

    return container

def textbox_padrao(rotulo):
    textbox = ft.TextField(
        label=rotulo,
        hint_text="Digite Aqui",
        expand=True,
    )
    return textbox

class DataPicker:
    def __init__(self, page) -> None:
        self.page = page

        self.datapicker = ft.DatePicker(
            first_date = date(2020, 1, 1),
            last_date = datetime.now().date(),
            confirm_text = "Confirmar",
            cancel_text = "Cancelar",
            help_text="Escolha a Data Desejada",
            open= False,
            on_change = self._selecionar_data,
        )

        self.botao = ft.Button(
            content = "Data",
            icon = ft.Icons.DATE_RANGE,
            on_click = self._abrir_datapicker,
        )

        page.overlay.append(self.datapicker)

        self.data_selecionada = None

    def _abrir_datapicker(self, e):
        self.datapicker.open = True

    def _selecionar_data(self, e):
        self.data_selecionada = self.datapicker.value.date()

        self.botao.content = f"{datetime.strftime(self.data_selecionada, "%d/%m/%Y")}"

        self.page.update()


class Notificacao:

    def __init__(self, page: ft.Page, mensagem) -> None:
        self.page = page
        self.mensagem = mensagem

    def ativar_notf(self):

        self.notf = ft.SnackBar(
            ft.Text(self.mensagem),
            open = True,
            duration= 3000,
        )

        self.page.overlay.append(self.notf)

        self.page.update()




# =============== Formularios ===============
def CadastroMembro(page):
    data_nascimento = DataPicker(page)

    coluna_data = ft.Column([data_nascimento.botao],
        horizontal_alignment= ft.CrossAxisAlignment.CENTER)

    nome = textbox_padrao("Digite seu Nome")


    cargos = [
        [0, "Membro"],
        [1, "Pastor"],
        [2, "Diácono"]
    ]
    cargo = ft.Dropdown(
        label="Cargo",
        options=[ft.dropdown.Option(key=key, text=value) for key, value in cargos],
        # editable= True,
    )

    generos = [
        [0, "Homem"],
        [1, "Mulher"]
    ]
    sexo = ft.Dropdown(
        label="Sexo",
        options=[ft.dropdown.Option(key=key, text=value) for key, value in generos]
    )

    def salvar_dados(e, page, tabela, **kwargs):
        registro = limpeza_dados(tabela, **kwargs)


        notf = Notificacao(page, f"Dados {registro}!")

        notf.ativar_notf()

    salvar = ft.Button(
        content= "Salvar Dados",
        icon= ft.Icons.SAVE,
        on_click= lambda e: salvar_dados(e, page, "membros",
            nome = nome.value,
            data_nascimento = data_nascimento.data_selecionada,
            sexo = sexo.value,
            id_cargo = cargo.value,
        ),
    )

    linha_dados = ft.Row([coluna_data, sexo, cargo],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

    coluna_pessoa = ft.Column([nome, linha_dados, salvar],
        horizontal_alignment = ft.CrossAxisAlignment.CENTER)

    container = container_padrao(coluna_pessoa)

    return container
