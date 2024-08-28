import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# Agora você pode importar o módulo utils
from utils.utils import Weather
import streamlit as st
import pandas as pd
import geopandas as gpd
from shapely import wkt
import folium
import streamlit.components.v1 as components
st.write('Hello World!')

#chamado = pd.read_parquet('../../datasets/chamado_treated.parquet')
#bairro = pd.read_csv('../../datasets/bairro_treated.csv')
# Caminho para a pasta raiz do projeto
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

# Caminhos para os arquivos
parquet_path = os.path.join(base_dir, 'datasets/chamado_treated.parquet')
csv_path = os.path.join(base_dir, 'datasets/bairro_treated.csv')

# Carregando os arquivos
chamado = pd.read_parquet(parquet_path)
bairro = pd.read_csv(csv_path)


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
for _, row in gdf.iterrows():
    folium.Marker(
        location=[row['centroid_lat'], row['centroid_lon']],
        popup=row['nome'],
        icon=folium.Icon(color="blue")  # Pode personalizar o ícone
    ).add_to(map)
gdf.explore(tiles="CartoDB positron", popup=popup_content, tooltip=popup_content, column='subprefeitura', legend=False, figsize=(5,5),
            edgecolor='k', m=map).save('map.html')

# Lendo e exibindo o mapa no Streamlit
with open('map.html', 'r', encoding='utf-8') as file:
    html_data = file.read()

components.html(html_data, height=600, width=800)

st.write(chamado.head())

