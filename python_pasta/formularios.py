from ast import UnaryOp
from ctypes import alignment
from pydoc import text
from pandas._libs import pandas
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
import pandas as pd

import streamlit as st
from datetime import datetime, date, time
import modulo_database as mod_db
from dataclasses import dataclass, field, asdict
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


# ===================================
#         LIMPEZA DE DADOS
# ===================================

# >>>> Dataclasses de Limpeza <<<<
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
    cargo: str


    def __post_init__(self):

        self.nome = self.nome.strip().upper()
        self.sexo = self.sexo.strip().upper()
        self.cargo = self.cargo.strip().upper()

@dataclass
class Dizimo:
    valor: float
    data: date
    id_membro: int

# >>>> Organização para Salvar Dados <<<<

def salvar_dados(e, tabela, **kwargs):

    def _empacotar_cargos(Base, nome):
        registro = Cargo(
            nome=nome,
        )

        Cargo_TBL = Base.classes.cargos
        dados = Cargo_TBL(**asdict(registro))

        return dados

    def _empacotar_membros(Base, nome, cargo, sexo, data_nascimento):
        registro = Membro(
            nome=nome,
            cargo=cargo,
            sexo=sexo,
            data_nascimento=data_nascimento
        )

        Membro_TBL = Base.classes.membros
        dados = Membro_TBL(**asdict(registro))

        return dados

    def _empacotar_dizimos(Base, valor, data, id_membro):
        registro = Dizimo(
            valor = valor,
            data = data,
            id_membro = id_membro,
        )

        Dizimo_TBL = Base.classes.dizimos
        dados = Dizimo_TBL(**asdict(registro))

        return dados

    dataclasses = {
        "membros": _empacotar_membros,
        "cargos": _empacotar_cargos,
        "dizimos": _empacotar_dizimos
    }

    empacotador = dataclasses.get(tabela)

    if not empacotador:
        raise ValueError(f"Tabela '{tabela}' é inválida ou não suportada.")

    conexao = mod_db.ConexaoBanco()

    Base = automap_base()
    Base.prepare(autoload_with=conexao.engine)

    with Session(conexao.engine) as session:
        session.add(empacotador(Base, **kwargs))
        session.commit()

    notf = ft.SnackBar(
        ft.Text("Dados Salvos com Sucesso!", color= "#114308"),
        show_close_icon= True,
        open= False,
        duration= 3000,
        bgcolor= "#afffa2",
    )

    e.page.overlay.append(notf)

    notf.open = True

    e.page.update()

# class ConexaoBanco:

#     def __init__(self):
#         self.engine = self._pegar_engine
#         self.metadata = self._pegar_metadata

#     def _pegar_engine(self):
#         caminho = Path(__file__).resolve().parent.parent / "Database.db"
#         caminho = caminho.as_posix()
#         engine = create_engine("sqlite:///" + str(caminho))
#         return engine

#     def _pegar_metadata(self):
#         metadata = MetaData(); metadata.reflect(bind=self.engine)
#         return metadata

# ============== USER INTERFACE ==============

import flet as ft

# >>>> Criação de Widgets Padrões
def container_padrao(conteudo):
    container = ft.Container(
        # expand= True,
        content=conteudo,
        padding= 20,
        bgcolor = ft.Colors.BLUE_GREY_900,
        border_radius = 12,
        width = 500,
        height = 200,
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
            first_date = date(1920, 1, 1),
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

# ==============================
#           FORMULARIOS
# ==============================

def CadastroMembro(page):

    # >>>> Entrada de Dados <<<<
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
        options=[ft.dropdown.Option(key=value, text=value) for _, value in cargos],
    )

    generos = [
        "Homem",
        "Mulher"
    ]
    sexo = ft.Dropdown(
        label="Sexo",
        options=[ft.dropdown.Option(key=key, text=key) for key in generos]
    )

    # >>>> Confirmação e Envio <<<<

    salvar = ft.Button(
        content= "Salvar Dados",
        icon= ft.Icons.SAVE,
        on_click= lambda e: salvar_dados(e, "membros",
            nome = nome.value,
            data_nascimento = data_nascimento.data_selecionada,
            sexo = sexo.value,
            cargo = cargo.value,
        ),
    )

    # >>>> Layout <<<<
    linha_dados = ft.Row([coluna_data, sexo, cargo],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

    coluna_pessoa = ft.Column([nome, linha_dados, salvar],
        horizontal_alignment = ft.CrossAxisAlignment.CENTER)

    container = container_padrao(coluna_pessoa)


    return container

def CadastroCargo(page):

    # >>>> Entrada de Dados <<<<
    nome = textbox_padrao("Digite o Nome do Cargo")

    # >>>> Confirmação e Envio <<<<

    salvar = ft.Button(
        content= "Salvar Dados",
        icon= ft.Icons.SAVE,
        on_click= lambda e: salvar_dados(e, "cargos",
            nome = nome.value,
        ),
    )

    # >>>> Layout <<<<

    coluna_pessoa = ft.Column([nome, salvar],
        horizontal_alignment = ft.CrossAxisAlignment.CENTER)

    container = container_padrao(coluna_pessoa)

    return container

def CadastroDizimo(page):
    import graficos as mod_graph

    conexao = mod_db.ConexaoBanco()

    df = mod_graph.pesquisa_tabela_comum(conexao.engine, "membros", "nome")

    try:
        lista_membros = dict(zip(df["nome"].tolist(), df["id"].tolist()))
    except:
        return ft.Container()


    label_autocomplete = ft.Text("Membro:")

    nome = ft.AutoComplete(
        expand=True,
        suggestions= [ft.AutoCompleteSuggestion(key, key) for key in lista_membros.keys()]
    )

    nome_membro = ft.Row(
        [label_autocomplete, nome],
        tight=True,
        # horizontal_alignment= ft.CrossAxisAlignment.START
    )

    valor = ft.TextField(
        label = "Valor",
        hint_text = 0.0,

        input_filter=ft.InputFilter(
            allow=True,
            regex_string= r"^\d*\.?\d*$",
            replacement_string=""
        )
    )

    data = DataPicker(page)

    # >>>> Confirmação e Envio <<<<

    salvar = ft.Button(
        content= "Salvar Dados",
        icon= ft.Icons.SAVE,
        on_click= lambda e: salvar_dados(e, "dizimos",
            id_membro = lista_membros.get(nome.value),
            valor = valor.value,
            data = data.data_selecionada,
        ),
    )

    # >>>> Layout <<<<

    linha_meio = ft.Row(
        [data.botao, valor]
    )
    coluna_pessoa = ft.Column([nome_membro, linha_meio, salvar],
        horizontal_alignment = ft.CrossAxisAlignment.CENTER)

    container = container_padrao(coluna_pessoa)

    return container
