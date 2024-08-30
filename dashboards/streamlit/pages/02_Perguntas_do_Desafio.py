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
ocup_path = os.path.join(base_dir, 'datasets/ocupacao_treated.csv')

# Carregando os arquivos
chamado = pd.read_parquet(parquet_path)
bairro = pd.read_csv(bairro_path)
ocup = pd.read_csv(ocup_path)

bairro['id_bairro'] = bairro['id_bairro'].apply(lambda x: str(x))
chamado = pd.merge(chamado, bairro, how='left', on='id_bairro')

# Merge chamado + ocup


# Faz o join do dataframe cham_bair com o df_explodido
merged = pd.merge(chamado, ocup, how='left', on='data_inicio') 


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

    with respostas_d:
        st.subheader("Análise do dia 01/04/2023")
        col1, col2 = st.columns(2)
        abril_01 = chamado[chamado['data_inicio'] == '2023-04-01']
        with col1:
            st.write('Total')
            st.metric('Volume de chamados', len(abril_01))

            st.write('Top 3 Bairros')
            top3_bairros = abril_01.groupby('nome').agg({'id_chamado':'count'}).sort_values('id_chamado', ascending=False).reset_index().head(3)
            fig = px.histogram(top3_bairros, x='nome', y='id_chamado')
            fig.update_layout(
                xaxis_title='Bairros',
                yaxis_title='Volume de chamados'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.write('Tipo de chamado com maior volume')
            top_tipo = abril_01.groupby('tipo').agg({'id_chamado':'count'}).sort_values('id_chamado', ascending=False).reset_index().head(1)
            top_tipo.columns = ['Tipo', 'Volume']
            st.table(top_tipo)

            st.write('Top 3 Subprefeituras')
            top3_bairros = abril_01.groupby('subprefeitura').agg({'id_chamado':'count'}).sort_values('id_chamado', ascending=False).reset_index().head(3)
            fig = px.histogram(top3_bairros, x='subprefeitura', y='id_chamado')
            fig.update_layout(
                xaxis_title='Subprefeituras',
                yaxis_title='Volume de chamados'
            )
            st.plotly_chart(fig, use_container_width=True)

        st.write(f'Existem {len(abril_01[abril_01['nome'].isnull()])} chamados abertos nesse dia que não foram associados a bairro nem subprefeituras no dia 01/04/2023')
        st.write("""Isso acontece porque não há informações sobre o local no registro do chamado. 
                 Não há ID do bairro, nem coordenadas ou qualquer informação que possibilite identificar de onde vem o chamado. 
                 Levando em consideração que 1º de abril é popularmente conhecido como "Dia da Mentira", esses registros podem ter ocorrido por conta de trotes, 
                 e os indivíduos que efetuaram a ligação não quiseram fornecer nenhuma informação sobre o local referente ao chamado. 
                 Outra possibilidade seria erro de tabulação do atendente no momento de registrar o chamado ou algum outro erro sistêmico.""")
        st.markdown("---")
        st.subheader('Perturbação do Sossego nos anos de 2022 e 2023')
        
        col1, col2 = st.columns(2)
        eventos = merged[merged['evento'].isin(['Reveillon', 'Carnaval','Rock in Rio'])]
        eventos = eventos[eventos['subtipo'] == 'Perturbação do sossego']
        byEvent = eventos[eventos['subtipo'] == 'Perturbação do sossego'].groupby('evento').agg({'id_chamado':'count'}).sort_values('id_chamado', ascending=False).reset_index()
        byEvent.columns = ['Evento', 'Volume']
        eventos_media = eventos[eventos['subtipo'] == 'Perturbação do sossego'].groupby(['evento','data_inicio']).agg({'id_chamado':'count'})
        eventos_media = eventos_media.groupby('evento').agg({'id_chamado':'mean'}).sort_values('id_chamado', ascending=False).reset_index()
        eventos_media.columns = ['Evento', 'Média']
        
        with col1:
            volume_total = sum(merged['subtipo'] == 'Perturbação do sossego')
            st.write('Chamados do tipo Perturbação do Sossego')
            st.metric('Volume total', volume_total)

            st.write('Volume por evento')
            st.table(byEvent)
        with col2:
            
            st.write('Perturbação do Sossego em eventos')
            st.metric('Volume total', len(eventos))

            st.write('Média diária de chamados por evento')
            st.table(eventos_media)
        
        media_total = chamado[chamado['subtipo'] == 'Perturbação do sossego'].groupby('data_inicio').agg({'id_chamado':'count'})
        media_total = media_total.mean().iloc[0]
        media_rock = eventos_media.iloc[0,1]
        media_carn = eventos_media.iloc[1,1]
        media_reve = eventos_media.iloc[2,1]
        st.markdown("---")
        st.write('A média diária de chamados do tipo Perturbação do Sossego para todo o período de 01/01/2022 até 31/12/2023 é: {:.2f}'.format(media_total))
        st.write('O Rock in Rio tem uma média diária de chamados do tipo Perturbação do Sossego é {:.2f} vezes maior que a média diária total dos anos 2022/2023'.format(media_rock/media_total))
        st.write('A média diária de chamados deste tipo para o carnaval é bem próxima da geral, representa {:.2f}% em comparação com a média diária do período 2022/2023'.format((media_carn/media_total*100)))
        st.write('Enquanto o Reveillon Possui a menor média diária de chamados, representando {:.2f}% em comparação com a média diária do período de 2022/2023'.format((media_reve/media_total)*100))

        





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