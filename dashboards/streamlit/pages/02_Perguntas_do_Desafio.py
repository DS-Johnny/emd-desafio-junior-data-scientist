# ---------------------------------------------------------------------------- IMPORTS
import sys
import os
import json
import requests
import streamlit as st
import pandas as pd
import plotly.express as px
from utils.utils import Weather

# para conseguir importar a classe Weather de utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..', '..', '..')))
wrio = Weather(-22.914469232838528, -43.44618954745923) # Coordenada CENTRO calculada utilizando geopandas

# ---------------------------------------------------------------------------- DADOS
chamado = st.session_state.chamado_data
bairro = st.session_state.bairro_data

bairro['id_bairro'] = bairro['id_bairro'].apply(lambda x: str(x))
chamado = pd.merge(chamado, bairro, how='left', on='id_bairro')


# Caminho para a pasta raiz do projeto para conseguir importar os datasets
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),'..', '..', '..'))
ocup_path = os.path.join(base_dir, 'datasets/ocupacao_treated.csv')
ocup = pd.read_csv(ocup_path)

# Faz o join do dataframe cham_bair com o df_explodido
merged = pd.merge(chamado, ocup, how='left', on='data_inicio') 

# Dados de feriados
response = requests.get('https://date.nager.at/api/v3/publicholidays/2024/BR')
public_holidays = json.loads(response.content)
holidays = pd.DataFrame(public_holidays)

# dicionário para converter os meses de integer para string em Português
meses = {
    1 : 'Janeiro',
    2 : 'Fevereiro',
    3 : 'Março',
    4 : 'Abril',
    5 : 'Maio',
    6 : 'Junho',
    7 : 'Julho',
    8 : 'Agosto',
    9 : 'Setembro',
    10: 'Outubro',
    11: 'Novembro',
    12: 'Dezembro'
}
# dicionário para converter os dias de integer para string em Português
dias_semana = {
    0: "Segunda-feira",
    1: "Terça-feira",
    2: "Quarta-feira",
    3: "Quinta-feira",
    4: "Sexta-feira",
    5: "Sábado",
    6: "Domingo"
}
# Novas colunas
holidays['date'] = pd.to_datetime(holidays['date']) # Converte a coluna date para datetime
holidays['month'] = holidays['date'].apply(lambda x: x.month).map(meses) # Extrai o mês da coluna date e transcreve para o Português
holidays['weekday_n'] = holidays['date'].apply(lambda x: x.weekday()) # Extrai o dia da semana da coluna date como um inteiro 
holidays['weekday'] = holidays['date'].apply(lambda x: x.weekday()).map(dias_semana) # Transcreve o dia da semana em Português



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
        st.write('A média diária de chamados do tipo Perturbação do Sossego para todo o período de 01/01/2022 até 31/12/2023 é: {:.1f}'.format(media_total))
        st.write('O Rock in Rio tem uma média diária de chamados do tipo Perturbação do Sossego é {:.1f} vezes maior que a média diária total dos anos 2022/2023'.format(media_rock/media_total))
        st.write('A média diária de chamados deste tipo para o carnaval é bem próxima da geral, representa {:.1f}% em comparação com a média diária do período 2022/2023'.format((media_carn/media_total*100)))
        st.write('Enquanto o Reveillon Possui a menor média diária de chamados, representando {:.1f}% em comparação com a média diária do período de 2022/2023'.format((media_reve/media_total)*100))

        





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

    with respostas_a:
        col1, col2 = st.columns(2)
        with col1:
            st.metric('Feriados em 2024',len(holidays))

            # Utiliza o método forecast de Weather que recebe uma data de inicio e fim de um período de dias para obter os dados de temperatura de cada dia
            temperaturas_diarias_2024 = wrio.forecast('2024-01-01', '2024-08-01') # retorna um dataframe com data, clima(tempo) e temperatura média

            # Cria novas colunas 
            temperaturas_diarias_2024['month_n'] = temperaturas_diarias_2024['data'].apply(lambda x: x.month) # Extrai o mês de cada registro como um valor inteiro
            temperaturas_diarias_2024['month'] = temperaturas_diarias_2024['data'].apply(lambda x: x.month).map(meses) # Transcreve o mês de inteiro para os nomes dos meses em Português

            # Agrupa os dados por mês e agrega a média de temperatura média de cada mês, ordena os meses de Janeiro a Dezembro
            by_month = temperaturas_diarias_2024.groupby(['month_n','month']).agg({'temperatura media':'mean'}).sort_values('month_n', ascending=True).reset_index()

            st.write('Temperatura média dos meses até agosto')
            st.table(by_month)


        with col2:
            feriados_na_semana = sum(holidays['weekday_n'].apply(lambda x: True if x in range(0, 5) else False))
            st.metric('Feriados em dia de semana', feriados_na_semana)

            clima_predominante = temperaturas_diarias_2024.groupby(['month_n','month'])['clima'].apply(lambda x: x.mode()[0]).reset_index()
            clima_predominante = clima_predominante[['month', 'clima']]
            st.write('Clima predominante')
            st.table(clima_predominante)

        st.markdown("""---""")

        holidays['temperatura media'] = holidays[holidays['date'] <= '2024-08-01']['date'].apply(lambda x: wrio.forecast(x.date(), x.date())['temperatura media']) # Temperatura média do dia
        holidays['clima'] = holidays[holidays['date'] <= '2024-08-01']['date'].apply(lambda x: wrio.forecast(x.date(), x.date())['clima']) # Clima do dia
        clima_temp_ate_agosto = holidays[holidays['date'] <= '2024-08-01'][['date', 'localName', 'temperatura media', 'clima']] # Filtra o dataframe para exibir apenas o período correto e colunas relevantes para a resposta

        st.write('Clima e a temperatura média em cada feriado de 01/01/2024 a 01/08/2024')
        st.table(clima_temp_ate_agosto[['localName', 'temperatura media', 'clima']])

        # Função que retorna True para dias parcialmente nublados ou "melhores", e false para todos os outros(dias com garoa, chuva ou nublados são considerados false)
        def clima_aproveitavel(clima):
            clima_ok = ['Mainly Sunny', 'Sunny', 'Partly Cloudy']
            if clima in clima_ok:
                return True
            else:
                return False

        # Cria um novo dataframe que apenas os registros até 01/08/2024
        holidays_2 = holidays[holidays['date'] <= '2024-08-01']

        # Cria uma nova coluna de booleanos, True caso a temperatura seja maior ou igual a 20ºC e clima considerado aproveitável
        holidays_2['praia'] = (holidays_2['temperatura media'] >= 20) & (holidays_2['clima'].apply(lambda x: clima_aproveitavel(x)))
        n_aprov = holidays_2[holidays_2['praia'] == False][['date', 'localName', 'temperatura media', 'clima']] # Filtra somente os feriados não aproveitáveis
        aprov = holidays_2[holidays_2['praia'] == True][['date', 'localName', 'temperatura media', 'clima']]
        st.write("Feriados não aproveitáveis")
        st.table(n_aprov[['localName', 'temperatura media', 'clima']])

        st.write("Feriado mais aproveitável do ano")
        st.table(aprov[['localName', 'temperatura media', 'clima']])

