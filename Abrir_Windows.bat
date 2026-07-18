@echo off
title Inicializando Streamlit

:: 1. Caminho para o script de ativação do seu Miniconda
call "C:\Users\%USERNAME%\miniconda3\Scripts\activate.bat"

:: 2. Ativar o seu ambiente do conda
call conda activate ambiente_python

:: 3. Navegar até a pasta do projeto
cd /d "%~dp0"

:: 4. Executar o Streamlit
streamlit run pagina_streamlit.py

pause