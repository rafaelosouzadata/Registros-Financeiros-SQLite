import os
import sys
import streamlit.web.cli as stcli

if __name__ == "__main__":
    # Garante que o Streamlit encontre o arquivo da sua página
    script_path = os.path.join(os.path.dirname(__file__), "pagina_streamlit.py")
    
    # Simula a chamada de linha de comando: streamlit run pagina_streamlit.py
    sys.argv = ["streamlit", "run", script_path, "--global.developmentMode=false"]
    sys.exit(stcli.main())
