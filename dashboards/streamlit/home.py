# ---------------------------------------------------------------------------- IMPORTS
import sys
import os
import streamlit as st
import pandas as pd
import geopandas as gpd
from shapely import wkt
import folium
import streamlit.components.v1 as components

# para conseguir importar a classe Weather de utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from utils.utils import Weather

# ---------------------------------------------------------------------------- DADOS

# Caminho para a pasta raiz do projeto para conseguir importar os datasets
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

# Caminhos para os arquivos
parquet_path = os.path.join(base_dir, 'datasets/chamado_treated.parquet')
csv_path = os.path.join(base_dir, 'datasets/bairro_treated.csv')

# Carregando os arquivos
chamado = pd.read_parquet(parquet_path)
bairro = pd.read_csv(csv_path)

# ------------------------------------------------------------------------- BODY

st.title('Desafio Técnico - Cientista de Dados Júnior')
st.markdown('#### Escritório de Dados - Prefeitura da Cidade do Rio de Janeiro')

tab1, tab2, tab3 = st.tabs(['Descrição do desafio', 'O que você vai encontrar nesta aplicação', 'Sobre mim'])

with tab1:
    st.write("""Este é um desafio técnico para a vaga de Cientista de dados Júnior no campo de soluções de tecnologia e de Governo Digital para a área pública do Rio de Janeiro.
             Nele serão avaliadas abilidades técnicas como manipulação de dados, análises exploratórias, integração com APIs, Consultas SQL, análise e Visualização de dados.""")
    
    

# ----------------------------------------------------------------------------- SIDEBAR
st.sidebar.write('Write Home')