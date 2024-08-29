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
chamado_sem_ausentes = chamado[~chamado['latitude'].isnull()]


# ------------------------------------------------------------------------- BODY

# Definindo um centroide para os bairros
gdf = gpd.GeoDataFrame(bairro)
gdf['geometry'] = gdf['geometry_wkt'].apply(wkt.loads)
gdf['geometry_wkt'] = gdf['geometry_wkt'].apply(wkt.loads)
gdf = gdf.set_geometry('geometry_wkt')
gdf['geometry'] = gdf.geometry.centroid
gdf['centroid_lat'] = gdf['geometry'].y
gdf['centroid_lon'] = gdf['geometry'].x

popup_content = ['nome', 'subprefeitura', 'area']

map = folium.Map(location=[-22.8831165538581, -43.42882206268638], tiles="OpenStreetMap", zoom_start=11)
map.add_child(FastMarkerCluster(chamado_sem_ausentes[['latitude', 'longitude']].values.tolist()))#,icon=folium.Icon(color='red', icon='info-sign'))) # Tentar mudar o ícone futuramente



gdf.explore(tiles="CartoDB positron", popup=popup_content, tooltip=popup_content, column='subprefeitura', legend=False, figsize=(5,5),
            edgecolor='k', m=map, cmap='coolwarm').save('map.html')

# Lendo e exibindo o mapa no Streamlit
with open('map.html', 'r', encoding='utf-8') as file:
    html_data = file.read()

components.html(html_data, height=600, width=800)