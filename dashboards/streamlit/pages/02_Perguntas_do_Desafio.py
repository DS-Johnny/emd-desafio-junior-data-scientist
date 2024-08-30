# ---------------------------------------------------------------------------- IMPORTS
import sys
import os
import streamlit as st
import pandas as pd
import geopandas as gpd
from shapely import wkt
import folium
from folium.plugins import FastMarkerCluster
import streamlit.components.v1 as components
import plotly.express as px
from utils.utils import Weather

# para conseguir importar a classe Weather de utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..', '..', '..')))


# ---------------------------------------------------------------------------- DADOS

# Caminho para a pasta raiz do projeto para conseguir importar os datasets
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),'..', '..', '..'))

# Caminhos para os arquivos
parquet_path = os.path.join(base_dir, 'datasets/chamado_treated.parquet')
bairro_path = os.path.join(base_dir, 'datasets/bairro_treated.csv')
ocup_path = os.path.join(base_dir, 'datasets/ocup_treated.csv')

# Carregando os arquivos
chamado = pd.read_parquet(parquet_path)
bairro = pd.read_csv(bairro_path)

bairro['id_bairro'] = bairro['id_bairro'].apply(lambda x: str(x))
chamado = pd.merge(chamado, bairro, how='left', on='id_bairro')


# ---------------------------------------------------------------------------- SIDEBAR



# ---------------------------------------------------------------------------- BODY

perguntas_datario, perguntas_api = st.tabs(['Perguntas Datario', 'Perguntas API'])

with perguntas_datario:
    perguntas_d, respostas_d = st.tabs(['Perguntas', 'Respostas'])
    with perguntas_d:
        st.markdown("""
        ## Localização de chamados do 1746
        #### Utilize a tabela de Chamados do 1746 e a tabela de Bairros do Rio de Janeiro para as perguntas de 1-5.

        1. Quantos chamados foram abertos no dia 01/04/2023?
        2. Qual o tipo de chamado que teve mais teve chamados abertos no dia 01/04/2023?
        3. Quais os nomes dos 3 bairros que mais tiveram chamados abertos nesse dia?
        4. Qual o nome da subprefeitura com mais chamados abertos nesse dia?
        5. Existe algum chamado aberto nesse dia que não foi associado a um bairro ou subprefeitura na tabela de bairros? Se sim, por que isso acontece?


        ## Chamados do 1746 em grandes eventos
        #### Utilize a tabela de Chamados do 1746 e a tabela de Ocupação Hoteleira em Grandes Eventos no Rio para as perguntas de 6-10. Para todas as perguntas considere o subtipo de chamado "Perturbação do sossego".

        6. Quantos chamados com o subtipo "Perturbação do sossego" foram abertos desde 01/01/2022 até 31/12/2023 (incluindo extremidades)?
        7. Selecione os chamados com esse subtipo que foram abertos durante os eventos contidos na tabela de eventos (Reveillon, Carnaval e Rock in Rio).
        8. Quantos chamados desse subtipo foram abertos em cada evento?
        9. Qual evento teve a maior média diária de chamados abertos desse subtipo?
        10. Compare as médias diárias de chamados abertos desse subtipo durante os eventos específicos (Reveillon, Carnaval e Rock in Rio) e a média diária de chamados abertos desse subtipo considerando todo o período de 01/01/2022 até 31/12/2023.

        ##### Importante: a tabela de Chamados do 1746 possui mais de 10M de linhas. Evite fazer consultas exploratórias na tabela sem um filtro ou limite de linhas para economizar sua cota no BigQuery!
        """)

with perguntas_api:
    perguntas_a, respostas_a = st.tabs(['Perguntas', 'Respostas'])

    with perguntas_a:
        st.markdown("""
        ## Integração com APIs: Feriados e Tempo

        ### Utilize as APIs públicas abaixo para responder às questões 1-8:
        - [Public Holiday API](https://date.nager.at/Api)
        - [Open-Meteo Historical Weather API](https://open-meteo.com/)

        1. **Quantos feriados há no Brasil em todo o ano de 2024?**

        2. **Qual mês de 2024 tem o maior número de feriados?**

        3. **Quantos feriados em 2024 caem em dias de semana (segunda a sexta-feira)?**

        4. **Qual foi a temperatura média em cada mês?**  
        Utilize a Open-Meteo Historical Weather API para obter as temperaturas médias diárias no Rio de Janeiro de 01/01/2024 a 01/08/2024.  
        
        5. **Qual foi o tempo predominante em cada mês nesse período?**  
        Utilize como referência para o código de tempo (_weather_code_) o seguinte link: [WMO Code](https://gist.github.com/stellasphere/9490c195ed2b53c707087c8c2db4ec0c).

        6. **Qual foi o tempo e a temperatura média em cada feriado de 01/01/2024 a 01/08/2024?**

        7. **Considere as seguintes suposições:**
        - O cidadão carioca considera "frio" um dia cuja temperatura média é menor que 20ºC;
        - Um feriado bem aproveitado no Rio de Janeiro é aquele em que se pode ir à praia;
        - O cidadão carioca só vai à praia quando não está com frio;
        - O cidadão carioca também só vai à praia em dias com sol, evitando dias **totalmente** nublados ou chuvosos (considere _weather_code_ para determinar as condições climáticas).

        Houve algum feriado "não aproveitável" em 2024? Se sim, qual(is)?

        8. **Qual foi o feriado "mais aproveitável" de 2024?**  
        Considere o melhor par tempo e temperatura.
        """)    