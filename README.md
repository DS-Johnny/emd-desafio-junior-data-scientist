# DESAFIO TÉCNICO JUNIOR DATA SCIENTIST - ESCRITORIO DE DADOS - RIO DE JANEIRO

## Objetivo

Este repositório contém as soluções para o desafio técnico da vaga de Cientista de Dados Júnior, focado em manipulação de dados, análises exploratórias, integração com APIs, consulta SQL no BigQuery, e visualização de dados. O desafio tem como foco o desenvolvimento de soluções tecnológicas para a área pública no Rio de Janeiro.

## Estrutura do Repositório

A organização do repositório é a seguinte:

├── dashboards                              # Diretório contendo dashboards criados com Streamlit
│   ├── streamlit                           # Diretório com scripts do Streamlit
│       ├── pages                           # Páginas da aplicação Streamlit
│           ├── 02_Perguntas_do_Desafio.py  # Perguntas do desafio implementadas no Streamlit
│           ├── 03_Chamados_1746.py         # Chamados 1746 visualizados no Streamlit
│           ├── 04_Reclamacoes.py           # Reclamações visualizadas no Streamlit
│           ├── 05_Temperatura_por_Bairro.py # Temperatura por bairro no Streamlit
│       ├── Inicio.py                       # Página inicial da aplicação Streamlit
│       ├── map_chamados.html               # Mapa de chamados (renderizado em HTML)
│       ├── map_temperatura.html            # Mapa de temperatura (renderizado em HTML)
├── requirements.txt                        # Lista de dependências de Python para o projeto
├── datasets                                # Diretório contendo os datasets utilizados no projeto
├── govrio                                  # Ambiente virtual Python
├── utils                                   # Diretório para funções utilitárias
├── analise_api.ipynb                       # Respostas das questões API utilizando Python
├── analise_python.ipynb                    # Respostas das questões SQL utilizando Python e Pandas
├── analise_sql.sql                         # Respostas das questões SQL no BigQuery
├── api_first_test.ipynb                    # Primeiro teste com a API (notebook de testes iniciais)
├── datario_EDA.ipynb                       # Análise Exploratória de Dados do datario
├── Desafio.md                              # Arquivo detalhando o desafio proposto
├── ETL.ipynb                               # Pipeline de ETL (Extração, Transformação e Carga)
├── faq.md                                  # Perguntas frequentes sobre o desafio
├── perguntas_api.md                        # Perguntas sobre APIs a serem respondidas
├── perguntas_sql.md                        # Perguntas SQL a serem respondidas
└── README.md                               # Documentação do projeto (este arquivo)

## Tecnologias usadas
- Python
- SQL
- BigQuery
- Basedosdados
- Streamlit
- Pandas
- Geopandas
- Folium
- matplotlib

## Instruções para Execução

1. Clone o repositório:
-   git clone https://github.com/DS-Johnny/emd-desafio-junior-data-scientist
2. Dentro do diretório do projeto crie um ambiente virtual e instale as dependências:
-  python -m venv govrio
-  govrio\scripts\activate
-  python -m pip install -r requirements.txt
3. Execute os notebooks para análises
4. Para executar a aplicação do relatório Streamlit
-  python -m streamlit run dashboards/streamlit/Inicio.py

## Histórico de Desenvolvimento do Projeto

**Primeiro Passo:** Comecei o projeto criando o arquivo first_api_test.ipynb, que basicamente serviu para eu testar e ter meu primeiro contato com as APIs. Foi uma boa introdução para entender como integrar isso no restante do projeto.

**Segundo Passo:** Na sequência, criei o datario_Eda.ipynb para fazer uma análise exploratória inicial dos dados. A ideia aqui era entender as variáveis e dimensões do dataset para poder planejar melhor as consultas SQL e as análises que seriam usadas nos dashboards. Durante essa fase, desenvolvi o módulo utils.py, onde criei a classe Weather. Essa classe se conecta à "Open-Meteo Historical Weather API" para puxar dados meteorológicos históricos com base em datas e coordenadas específicas. Basicamente, você passa as coordenadas de latitude e longitude na hora de instanciar a classe, e depois utiliza as datas como argumento no método forecast, que te retorna um dataframe com as colunas: data, temperatura média e clima.

Durante essa análise exploratória, notei que o dataset de Chamados do 1746 tinha umas informações geográficas interessantes, como objetos Polygon e Multipolygon, que poderiam ser trabalhados com a biblioteca geopandas para definir o perímetro dos bairros do Rio de Janeiro e fazer umas análises visuais usando mapas. Fiz alguns testes iniciais com as bibliotecas geopandas, folium, shapely e matplotlib.pyplot.

No começo, usei uma coordenada que achei no Google para fazer as requisições da API meteorológica, mas depois percebi que era uma coordenada do estado do Rio, não da cidade. Então, usei a geopandas para identificar a coordenada centróide e a central da cidade, e acabei decidindo pela central, que é basicamente a média das coordenadas limites da cidade. Essas coordenadas limites também foram úteis mais tarde para filtrar os chamados fora da região da cidade na hora de desenvolver a aplicação em Streamlit.

Como o dataset de Chamados do 1746 era enorme, fiz uma seleção das variáveis para reduzir o consumo de dados no GCP e puxar só o necessário para responder às perguntas do desafio e outras análises que achei interessantes, como informações geográficas e o volume de reclamações por tipo de chamado. Também criei um banco de dados SQL local para testar e modelar as consultas antes de rodá-las no GCP.

**Terceiro Passo:** Criei o arquivo ETL.ipynb para fazer a extração dos dados no GCP, tratá-los e gerar arquivos .csv e .parquet. Esses arquivos são usados nas respostas do desafio nos arquivos analise_sql.ipynb e também para desenvolver os dashboards, assim não preciso consumir os dados do GCP toda vez que rodo os scripts.

**Quarto Passo:** Nessa fase, foquei em resolver as perguntas do desafio. Criei os arquivos analise_api.ipynb, analise_sql.ipynb e analise_sql.sql para isso.

**Quinto Passo:** Finalmente, comecei a desenvolver a aplicação em Streamlit para apresentar os resultados das análises de uma maneira interativa e fácil de entender.

**Link para a aplicação na nuvem StreamlitShare** - Caso a nuvem esteja com alguma instabilidade, por favor rodar a aplicação conforme as instruções contidas anteriormente neste arquivo.
- https://govrio.streamlit.app/