# ---------------------------------------------------------------------------- IMPORTS
import sys
import os
import streamlit as st
import pandas as pd
import geopandas as gpd
from shapely import wkt
import folium
import streamlit.components.v1 as components
from datetime import datetime

# para conseguir importar a classe Weather de utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..', '..', '..')))
from utils.utils import Weather

# ---------------------------------------------------------------------------- DADOS

# Caminho para a pasta raiz do projeto para conseguir importar os datasets
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),'..', '..', '..'))

# Caminhos para os arquivos
parquet_path = os.path.join(base_dir, 'datasets/chamado_treated.parquet')
csv_path = os.path.join(base_dir, 'datasets/bairro_treated.csv')

# Carregando os arquivos
chamado = pd.read_parquet(parquet_path)
bairro = pd.read_csv(csv_path)

# ------------------------------------------------------------------------- BODY

data_exemplo = datetime.strptime('2024-08-04', '%Y-%m-%d').date()
d = st.date_input("Selecione o dia", value=data_exemplo)
if d:
    st.write('Aguarde, os dados para esta data estão sendo analisados. Isso pode demorar alguns instantes.')

    try:
        # Função que vai ser aplicada em cada linha do dataframe
        def get_temperatura_media(row, d):
            wrio = Weather(row['centroid_lat'], row['centroid_lon'])  # Instancia a classe Weather com as coordenadas do bairro
            return wrio.forecast(d, d)['temperatura media']

        # Aplicando a função no dataframe de bairros
        bairro['temperatura media'] = bairro.apply(lambda x: get_temperatura_media(x, d), axis=1)
        bairro['temperatura media'] = bairro['temperatura media'].apply(lambda x: round(x,2))

        # Definindo um centroide para os bairros
        gdf = gpd.GeoDataFrame(bairro)
        gdf['geometry'] = gdf['geometry_wkt'].apply(wkt.loads)
        gdf['geometry_wkt'] = gdf['geometry_wkt'].apply(wkt.loads)
        gdf = gdf.set_geometry('geometry_wkt')
        gdf['geometry'] = gdf.geometry.centroid
        gdf['centroid_lat'] = gdf['geometry'].y
        gdf['centroid_lon'] = gdf['geometry'].x

        popup_content = ['nome', 'subprefeitura', 'temperatura media']
        map = folium.Map(location=[-22.8831165538581, -43.42882206268638], tiles="OpenStreetMap", zoom_start=11)



        gdf.explore(tiles="CartoDB positron", popup=popup_content, tooltip=popup_content, column='temperatura media', legend=False, figsize=(5,5),
                    edgecolor='k', m=map, cmap='OrRd').save('map.html')

        # Lendo e exibindo o mapa no Streamlit
        with open('map.html', 'r', encoding='utf-8') as file:
            html_data = file.read()

        components.html(html_data, height=600, width=800)
    except:
        st.warning('Por favor tente uma data mais antiga. Não foi possível encontrar os dados.')