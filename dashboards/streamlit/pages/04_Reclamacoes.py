# ---------------------------------------------------------------------------- IMPORTS
import sys
import os
import streamlit as st
import pandas as pd
import geopandas as gpd
from shapely import wkt
import folium
import matplotlib.pyplot as plt
import streamlit.components.v1 as components


# para conseguir importar a classe Weather de utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..', '..', '..')))


# ---------------------------------------------------------------------------- DADOS
chamado = st.session_state.chamado_data
bairro = st.session_state.bairro_data

bairro['id_bairro'] = bairro['id_bairro'].apply(lambda x: str(x))
chamado = pd.merge(chamado, bairro, how='left', on='id_bairro')


# ---------------------------------------------------------------------------- SIDEBAR

# ---------------------------------------------------------------------------- BODY

with st.container():
    col1, col2, col3 = st.columns(3)
    
    tot_reclam = chamado['reclamacoes'].sum()
    recl_by_sub = chamado.groupby('subprefeitura').agg({'reclamacoes':'sum'}).reset_index().sort_values('reclamacoes', ascending=False)
    sub_max_nome = recl_by_sub.iloc[0,0]
    sub_max_tot =  recl_by_sub.iloc[0,1]
    sub_min_nome = recl_by_sub.iloc[8,0]
    sub_min_tot = recl_by_sub.iloc[8,1]

    with col1:
        st.write('Volume de Reclamações')
        st.metric('Total', tot_reclam)
    
    with col2:
        st.write('Subprefeitura mais reclamada')
        st.metric(sub_max_nome, sub_max_tot)
    
    with col3:
        st.write('Subprefeitura menos reclamada')
        st.metric(sub_min_nome, sub_min_tot)

with st.container():
    col1, col2 = st.columns(2)

    byStatus = chamado.groupby('status').agg({'reclamacoes':'sum'}).reset_index().sort_values('reclamacoes', ascending=False)
    bySubtipo = chamado.groupby('subtipo').agg({'reclamacoes':'sum'}).reset_index().sort_values('reclamacoes', ascending=False)

    with col1:
        st.write('Reclamações por Status')
        st.table(byStatus)
    with col2:
        st.write('10 Subtipos de chamados com mais reclamações')
        st.table(bySubtipo.head(10))

with st.container():
    # Dataframe para plot do mapa
    chamado_sem_ausentes = chamado[~chamado['latitude'].isnull()]

    #---------------------------- Group by CONTAGEM de CHAMADOS e Reclamações
    chamByBairro = chamado_sem_ausentes.groupby('id_bairro').agg({'id_chamado':'count'})
    chamByBairro = chamByBairro.reset_index()
    reclByBairro = chamado_sem_ausentes.groupby('id_bairro').agg({'reclamacoes':'sum'})
    reclByBairro = reclByBairro.reset_index()
    bairro['QT_chamados'] = chamByBairro['id_chamado']
    bairro['QT_reclamacoes'] = reclByBairro['reclamacoes']
    recl_by_bairro = chamado.groupby('nome').agg({'reclamacoes':'sum'}).reset_index().sort_values('reclamacoes', ascending=False)
    # Definindo um centroide para os bairros
    gdf = gpd.GeoDataFrame(bairro)
    gdf['geometry'] = gdf['geometry_wkt'].apply(wkt.loads)
    gdf['geometry_wkt'] = gdf['geometry_wkt'].apply(wkt.loads)
    gdf = gdf.set_geometry('geometry_wkt')

    

    col1, col2 = st.columns(2)

    # Filtra o GeoDataFrame para isolar os bairros com mais e menos reclamações
    bairro_destaque1 = gdf[gdf['nome'] == recl_by_bairro.iloc[0, 0]]
    bairro_destaque2 = gdf[gdf['nome'] == recl_by_bairro.iloc[-1, 0]]

    # Defina os limites dos eixos com base no GeoDataFrame completo
    xlim = gdf.total_bounds[[0, 2]]
    ylim = gdf.total_bounds[[1, 3]]

    with col1:
        st.write('Bairro com mais reclamações:')
        st.metric(recl_by_bairro.iloc[0, 0], recl_by_bairro.iloc[0, 1])
        # Plota o mapa com todos os bairros
        fig, ax = plt.subplots(figsize=(10, 10))
        gdf.plot(ax=ax, edgecolor='black', facecolor='lightblue')

        # Ajusta os limites dos eixos para garantir o alinhamento
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)

        # Destaca bairro específico
        bairro_destaque1.plot(ax=ax, edgecolor='black', facecolor='red')  # Cor de destaque em vermelho
        st.pyplot(fig)

    with col2:
        st.write('Bairro com menos reclamações:')
        st.metric(recl_by_bairro.iloc[-1, 0], recl_by_bairro.iloc[-1, 1])
        # Plota o mapa com todos os bairros
        fig2, ax2 = plt.subplots(figsize=(10, 10))
        gdf.plot(ax=ax2, edgecolor='black', facecolor='lightblue')

        # Ajusta os limites dos eixos para garantir o alinhamento
        ax2.set_xlim(xlim)
        ax2.set_ylim(ylim)

        # Destaca bairro específico
        bairro_destaque2.plot(ax=ax2, edgecolor='black', facecolor='blue')  # Cor de destaque em vermelho
        st.pyplot(fig2)
        
        


    
