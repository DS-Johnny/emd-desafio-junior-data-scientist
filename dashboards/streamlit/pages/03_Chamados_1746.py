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

# para conseguir importar a classe Weather de utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..', '..', '..')))


# ---------------------------------------------------------------------------- DADOS
@st.cache_data
def get_data():
    # Caminho para a pasta raiz do projeto para conseguir importar os datasets
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),'..', '..', '..'))

    # Caminhos para os arquivos
    parquet_path = os.path.join(base_dir, 'datasets/chamado_treated.parquet')
    csv_path = os.path.join(base_dir, 'datasets/bairro_treated.csv')

    # Carregando os arquivos
    chamado = pd.read_parquet(parquet_path)
    bairro = pd.read_csv(csv_path)
    bairro['id_bairro'] = bairro['id_bairro'].apply(lambda x: str(x))
    chamado = pd.merge(chamado, bairro, how='left', on='id_bairro')
    return bairro, chamado

bairro, chamado = get_data()
# ------------------------------------------------------------------------- Sidebar
# --------------------------------FILTRO DE OUTLIERS 
outliers = st.sidebar.radio(
    'Outliers',
    ["Com outliers", "Sem outliers", "Somente Outliers"],
    captions=[
        "Todos os dados",
        "Apenas chamados de dentro da região",
        "Chamados fora da região e sem local"
    ],
)

if outliers == "Com outliers":
    chamado = chamado
elif outliers == "Sem outliers":
    chamado = chamado[(chamado['longitude'] > -43.79547479049324) & (chamado['longitude'] < -43.09690430442521) & (chamado['latitude'] > -23.08290563772194) & (chamado['latitude'] < -22.746032827955112)]
else:
    chamado = chamado[~((chamado['longitude'] > -43.79547479049324) & (chamado['longitude'] < -43.09690430442521) & (chamado['latitude'] > -23.08290563772194) & (chamado['latitude'] < -22.746032827955112))]

# --------------------------------------------------------- Filtro de tempo
datas_chamado = chamado['data_inicio'].sort_values(ascending=True)
data_inicio, data_fim = st.sidebar.select_slider('Selecione o período:', datas_chamado, [datas_chamado.max(), datas_chamado.min()])

chamado = chamado[(chamado['data_inicio'] >= data_inicio) & (chamado['data_inicio'] <= data_fim)]

# ------------------------------------------------------------------------- BODY
st.title('Análise de chamados do 1746')


# -------------------------------------------- Filtros de Tipo e Subtipo
tipo_true = st.radio(
    'Selecione:',
    ["Visualizar todos", "Filtrar por tipo", "Filtrar por subtipo"]
)

if tipo_true == 'Visualizar todos':
    chamado = chamado
elif tipo_true == 'Filtrar por tipo':
    tipos = chamado['tipo'].unique().tolist()
    tipos.sort()
    tipo = st.selectbox('Tipo', tipos)
    chamado = chamado[chamado['tipo'] == tipo]
else:
    subtipos = chamado['subtipo'].unique().tolist()
    subtipos.sort()
    subtipo = st.selectbox('Subtipo', subtipos)
    chamado = chamado[chamado['subtipo'] == subtipo]

#--------------------------------------------------------------------

st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.subheader('Total')
    qt_chamados = len(chamado)
    st.metric('Quantidade de chamados', qt_chamados)
with col2:
    st.subheader('Sem local')
    qt_chamados_sem_local = len(chamado[chamado['latitude'].isnull()])
    st.metric('Quantidade de chamados', qt_chamados_sem_local)

with col3:
    qt_chamados_fora = len(chamado[~((chamado['longitude'] > -43.79547479049324) & (chamado['longitude'] < -43.09690430442521) & (chamado['latitude'] > -23.08290563772194) & (chamado['latitude'] < -22.746032827955112))]) - qt_chamados_sem_local
    st.subheader('Fora da região')
    st.metric('Quantidade de chamados', qt_chamados_fora)

st.write('Chamados que não possuem informação do local não serão plotados no mapa')
dist_map, analise = st.tabs(['Distribuição geográfica dos chamados', 'Análises'])



with dist_map:
    # Dashboard para plot do mapa
    chamado_sem_ausentes = chamado[~chamado['latitude'].isnull()]



    #---------------------------- Group by CONTAGEM de CHAMADOS e Reclamações
    chamByBairro = chamado_sem_ausentes.groupby('id_bairro').agg({'id_chamado':'count'})
    chamByBairro = chamByBairro.reset_index()
    reclByBairro = chamado_sem_ausentes.groupby('id_bairro').agg({'reclamacoes':'sum'})
    reclByBairro = reclByBairro.reset_index()
    bairro['QT_chamados'] = chamByBairro['id_chamado']
    bairro['QT_reclamacoes'] = reclByBairro['reclamacoes']

    # Definindo um centroide para os bairros
    gdf = gpd.GeoDataFrame(bairro)
    gdf['geometry'] = gdf['geometry_wkt'].apply(wkt.loads)
    gdf['geometry_wkt'] = gdf['geometry_wkt'].apply(wkt.loads)
    gdf = gdf.set_geometry('geometry_wkt')
    gdf['geometry'] = gdf.geometry.centroid
    gdf['centroid_lat'] = gdf['geometry'].y
    gdf['centroid_lon'] = gdf['geometry'].x

    popup_content = ['nome', 'subprefeitura', 'QT_chamados']

    map = folium.Map(location=[-22.8831165538581, -43.42882206268638], tiles="OpenStreetMap", zoom_start=11)
    map.add_child(FastMarkerCluster(chamado_sem_ausentes[['latitude', 'longitude']].values.tolist()))#,icon=folium.Icon(color='red', icon='info-sign'))) # Tentar mudar o ícone futuramente



    gdf.explore(tiles="CartoDB positron", popup=popup_content, tooltip=popup_content, column='QT_chamados', legend=False, figsize=(5,5),
                edgecolor='k', m=map, cmap='OrRd').save('map.html')

    # Lendo e exibindo o mapa no Streamlit
    with open('map.html', 'r', encoding='utf-8') as file:
        html_data = file.read()

    components.html(html_data, height=600, width=800)

with analise:
    subprefeituras = chamado['subprefeitura'].unique().tolist()
    #subprefeituras.sort()
    subprefeitura = st.multiselect('Subprefeituras', subprefeituras, default=subprefeituras)

    
    chamado = chamado[chamado['subprefeitura'].isin(subprefeitura)]

    col1, col2, col3 = st.columns(3)
    with col1:
        encerrados = sum(chamado['situacao'] == 'Encerrado')
        st.metric('Encerrados', encerrados)
        pct_encerrados = encerrados / len(chamado)
        text_encerrados = '{:.2f}%'.format(pct_encerrados*100)
        st.progress(pct_encerrados, text=text_encerrados)

    with col2:
        n_encerrados = sum(chamado['situacao'] == 'Não Encerrado')
        st.metric('Não Encerrado', n_encerrados)
        pct_n_encerrados = n_encerrados / len(chamado)
        text_n_encerrados = '{:.2f}%'.format(pct_n_encerrados*100)
        st.progress(pct_n_encerrados, text=text_n_encerrados)
    
    with col3:
        reclamacoes = chamado['reclamacoes'].sum()
        st.metric('Reclamações', reclamacoes)
        pct_reclamacoes = reclamacoes / len(chamado)
        text_reclamacoes = '{:.2f}%'.format(pct_reclamacoes*100)
        st.progress(pct_reclamacoes, text=text_reclamacoes)
    
with st.container():
    graph, table = st.tabs(['Gráfico', 'Tabela'])
    chamados_por_subp = chamado.groupby('subprefeitura').agg({'id_chamado':'count'}).sort_values('id_chamado', ascending=False).reset_index()
    chamados_por_subt = chamado.groupby('subtipo').agg({'id_chamado':'count'}).sort_values('id_chamado', ascending=False).head(10).reset_index()
    with graph:    
        
        fig = px.histogram(chamados_por_subp, x='subprefeitura', y='id_chamado', title='Volume de chamados por Subprefeitura', color='subprefeitura')
        fig.update_layout(
            xaxis_title='Subprefeituras',
            yaxis_title='Volume de chamados'
        )
        st.plotly_chart(fig, use_container_width=True)


        fig = px.histogram(chamados_por_subt, x='subtipo', y='id_chamado', title='Volume de chamados por Subtipo', color='subtipo')
        fig.update_layout(
            xaxis_title='Subtipos',
            yaxis_title='Volume de chamados'
        )
        st.plotly_chart(fig, use_container_width=True)

    with table:
        st.table(chamados_por_subp)

    

    