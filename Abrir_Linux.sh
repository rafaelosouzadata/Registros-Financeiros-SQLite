#!/bin/bash

echo "iniciando Servidor..."

#!/bin/bash

# 1. Configura o terminal para o Conda (se não estiver no seu .bashrc)
source "$HOME/miniconda3/etc/profile.d/conda.sh"

# 2. Ativar o seu ambiente do conda
conda activate ambiente_python

# 3. Navegar até a pasta do projeto (onde o script .sh está salvo)
cd "$(dirname "$0")"

# 4. Executar o Streamlit
streamlit run pagina_streamlit.py # --server.headless true