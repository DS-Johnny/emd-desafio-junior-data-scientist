# ---------------------------------------------------------------------------- IMPORTS
import sys
import os
import streamlit as st
import pandas as pd

# para conseguir importar a classe Weather de utils
#sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))


# ---------------------------------------------------------------------------- DADOS

# ---------------------------------------------------------------------------- FUNÇÃO PARA CARREGAR DADOS
def load_data():
    """Função para carregar e armazenar os dados na sessão."""
    
    # Caminho para a pasta raiz do projeto para conseguir importar os datasets
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

    # Caminhos para os arquivos
    parquet_path = os.path.join(base_dir, 'datasets/chamado_treated.parquet')
    csv_path = os.path.join(base_dir, 'datasets/bairro_treated.csv')

    # Verifica se os dados já foram carregados
    if 'chamado_data' not in st.session_state:
        st.session_state.chamado_data = pd.read_parquet(parquet_path)
        st.session_state.bairro_data = pd.read_csv(csv_path)

# ---------------------------------------------------------------------------- CARREGAMENTO DOS DADOS
load_data()

# ------------------------------------------------------------------------- BODY

st.title('Desafio Técnico - Cientista de Dados Júnior')
st.markdown('#### Escritório de Dados - Prefeitura da Cidade do Rio de Janeiro')

tab1, tab2, tab3 = st.tabs(['Descrição do desafio', 'O que você vai encontrar nesta aplicação', 'Sobre mim'])

with tab1:
    st.write("""
             O desafio técnico para a vaga de Cientista de Dados Júnior, direcionado para soluções tecnológicas e iniciativas de Governo Digital no setor público do Rio de Janeiro, tem como objetivo avaliar competências essenciais em dados. Ao longo de 13 dias, é necessário trabalhar com diferentes conjuntos de dados, incluindo chamados do serviço 1746, informações dos bairros do Rio de Janeiro e dados de ocupação hoteleira durante grandes eventos.

O foco do desafio é a demonstração de habilidades em manipulação de dados, realização de análises exploratórias, integração de dados por meio de APIs, execução de consultas SQL no BigQuery e criação de visualizações de dados que apresentem insights de forma clara e eficaz. Além disso, o desafio destaca a importância da capacidade de adaptação rápida a novas tecnologias, essencial para enfrentar as demandas dinâmicas do setor público, onde o uso inteligente de dados pode contribuir significativamente para a melhoria dos serviços oferecidos à população.
             """)
            

with tab2:
    st.write("""
            Este relatório/dashboard foi desenvolvido para responder às perguntas do desafio e proporcionar uma análise aprofundada dos chamados do serviço 1746 no Rio de Janeiro, com foco na identificação de sua distribuição geográfica.

            Nas páginas "Chamados 1746" e "Temperatura por Bairro", você pode explorar mapas interativos que facilitam a visualização desses dados. Devido ao grande volume de dados, pode haver um breve tempo de carregamento para renderização dos mapas.
            """)

with tab3:
    st.write("""
            Olá! Me chamo Johnny, muito prazer.
            Sou um estudante no último ano de Bacharelado em Ciência de Dados, sempre curioso e dedicado e com facilidade para aprender de forma autodidata. 
            
            Tive meu primeiro contato com programação em 2020 e de lá para cá acabei desenvolvendo uma grande paixão pelo mundo dos dados, o que me levou a iniciar o curso de Ciência de dados em 2021 pela UNIVESP.
            
            Durante minha jornada tive o prazer de estagiar na empresa Movida - Aluguel de carros, o que contribuiu bastante com minhas abilidades de análise e ETL.
            Minhas habilidades incluem análise de dados com Python e SQL, além de desenvolver dashboards com Streamlit e Power BI. 
            No momento, estou me aprofundando nos estudos de machine learning para expandir ainda mais meu conhecimento na área.
            
            Também curto bastante o desenvolvimento backend e web e já desenvolvi alguns projetos utilizando Flask.
            
            Uma curiosidade sobre mim é que tenho uma paixão pelo mundo náutico e veleiros, o que também me levou a desenvolver um interesse por meteorologia.
            
            Meu objetivo é iniciar minha carreira como cientista de dados e adquirir uma experiência sólida na área. Assim que me graduar tenho planos de iniciar uma pós em Engenharia de Machine Learning
            e outra em Engenharia de Dados.
            
            Tenho um grande interesse em trabalhar em projetos na área de meteorologia ou em projetos envolvendo inteligencia artifical.
            """)
