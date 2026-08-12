import sys
from pathlib import Path

caminho_modulos = Path(__file__).resolve().parent / "python_pasta"
sys.path.append(str(caminho_modulos))

import flet as ft
import formularios as mod_form

def main(page: ft.Page):

    page.title = "Financeiro Igreja"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20
    page.window.height = 600
    page.window.width = 600
    page.scroll = "auto"

    page.vertical_alignment = "center"
    page.horizontal_alignment = "center"

    main_container = ft.Container(
                                expand = True,
                                # height = 200,
                                width = 600,
                                padding=20,
                                bgcolor= "BLUE"
    )

    Formulario_Membros = mod_form.CadastroMembro(page)
    Formulario_Cargo = mod_form.CadastroCargo(page)
    Formulario_Dizimo = mod_form.CadastroDizimo(page)

    pagina_cadastro = ft.Column(
        [Formulario_Cargo, Formulario_Membros, Formulario_Dizimo]
    )
    main_container.content = pagina_cadastro

    page.add(main_container)

ft.run(main)
