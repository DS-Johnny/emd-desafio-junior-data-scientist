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
chamado = st.session_state.chamado_data
bairro = st.session_state.bairro_data

bairro['id_bairro'] = bairro['id_bairro'].apply(lambda x: str(x))
chamado = pd.merge(chamado, bairro, how='left', on='id_bairro')
    
# ------------------------------------------------------------------------- BODY

st.title("Análise de temperatura e clima por bairro")
st.write('Escolha uma data para visualizar o mapa de calor.')

data_exemplo = datetime.strptime('2024-08-04', '%Y-%m-%d').date()
d = st.date_input("Selecione o dia", value=data_exemplo)
if d:
    st.write('Aguarde, os dados para esta data estão sendo processados. Isso pode demorar alguns instantes.')

    try:
        # Função que vai ser aplicada em cada linha do dataframe
        def get_temperatura_media(row, d):
            wrio = Weather(row['centroid_lat'], row['centroid_lon'])  # Instancia a classe Weather com as coordenadas do bairro
            return wrio.forecast(d, d)['temperatura media']

        def get_clima(row, d):
            wrio = Weather(row['centroid_lat'], row['centroid_lon'])  # Instancia a classe Weather com as coordenadas do bairro
            return wrio.forecast(d, d)['clima']

        # Aplicando a função no dataframe de bairros
        bairro['temperatura media'] = bairro.apply(lambda x: get_temperatura_media(x, d), axis=1)
        bairro['temperatura media'] = bairro['temperatura media'].apply(lambda x: round(x,2))
        bairro['clima'] = bairro.apply(lambda x: get_clima(x, d), axis=1)
        
        st.write("Dados coletados da API Open-Meteo Historical Weather. Seu mapa está sendo gerado.")

        # Definindo um centroide para os bairros
        gdf = gpd.GeoDataFrame(bairro)
        gdf['geometry'] = gdf['geometry_wkt'].apply(wkt.loads)
        gdf['geometry_wkt'] = gdf['geometry_wkt'].apply(wkt.loads)
        gdf = gdf.set_geometry('geometry_wkt')
        gdf['geometry'] = gdf.geometry.centroid
        gdf['centroid_lat'] = gdf['geometry'].y
        gdf['centroid_lon'] = gdf['geometry'].x

        popup_content = ['nome', 'subprefeitura', 'temperatura media','clima']
        tooltip_content = ['nome','temperatura media', 'clima']
        map = folium.Map(location=[-22.8831165538581, -43.42882206268638], tiles="OpenStreetMap", zoom_start=11)
        
        st.write('Média de temperatura do dia escolhido para cada bairro da Cidade do Rio de Janeiro.')
        gdf.explore(tiles="CartoDB positron", popup=popup_content, tooltip=tooltip_content, column='temperatura media', legend=False, figsize=(5,5),
                    edgecolor='k', m=map, cmap='OrRd').save('map_temperatura.html')

        # Lendo e exibindo o mapa no Streamlit
        with open('map_temperatura.html', 'r', encoding='utf-8') as file:
            html_data = file.read()

        components.html(html_data, height=600, width=800)

        b_max = bairro[bairro['temperatura media'] == bairro['temperatura media'].max()]['nome'].iloc[0]
        t_max = bairro[bairro['temperatura media'] == bairro['temperatura media'].max()]['temperatura media'].iloc[0]
        b_min = bairro[bairro['temperatura media'] == bairro['temperatura media'].min()]['nome'].iloc[0]
        t_min = bairro[bairro['temperatura media'] == bairro['temperatura media'].min()]['temperatura media'].iloc[0]
        col1, col2 = st.columns(2)
        with col1:
            st.subheader('Bairro mais quente do dia')
            st.write(b_max)

            st.subheader('Temperatura média')
            st.write(f'{t_max}°C')
            
        with col2:
            st.subheader('Bairro mais frio do dia')
            st.write(b_min)

            st.subheader('Temperatura média')
            st.write(f'{t_min}°C')
        
        st.markdown("---")
        subp_media = bairro.groupby('subprefeitura').agg({'temperatura media':'mean'}).sort_values('temperatura media', ascending=False)
        st.subheader('Média de temperatuda por subprefeitura')
        st.table(subp_media)


    except:
        st.warning('Por favor tente uma data mais antiga. Não foi possível encontrar os dados.')

