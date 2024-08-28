
import json
import openmeteo_requests
import requests
import requests_cache
import pandas as pd
from retry_requests import retry


# =-=-=-=-=-==-=-=-=-=-==-=-=-=-=-==-=-=-=-=-==-=-=-=-=-==-=-=-=-=-==-=-=-=-=-==-=-=-=-=-==-=-=-=-=-==-=-=-=-=-==-=-=-=-=-==-=-=-=-=-==-=-=-=-=-==-=-=-=-=-
class Weather():
    def __init__ (self, lat:float, lon:float):
        self.lat = lat # Latitude
        self.lon = lon # Longitude
        self.tz = "America/Sao_Paulo"
        self.cache_session = requests_cache.CachedSession('.cache', expire_after=-1)  # Configura uma sessão de cache para armazenar as respostas da API indefinidamente
        self.retry_session = retry(self.cache_session, retries=5, backoff_factor=0.2)  # Configura a sessão de cache para tentar novamente até 5 vezes com um fator de backoff
        self.openmeteo = openmeteo_requests.Client(session=self.retry_session)  # Cria um cliente da Open-Meteo API usando a sessão configurada
        self.url = "https://archive-api.open-meteo.com/v1/archive"  # Define a URL da API de arquivos da Open-Meteo

    def forecast(self, data_inicio, data_fim):
        params = {
            "latitude": self.lat,  # Latitude do local de interesse
            "longitude": self.lon,  # Longitude do local de interesse
            "start_date": data_inicio,  # Data de início do período de interesse
            "end_date": data_fim,  # Data de término do período de interesse
            "daily": ["weather_code", "temperature_2m_mean"],  # Variáveis diárias solicitadas (código do clima e temperatura média)
            "timezone": "America/Sao_Paulo"  # Fuso horário a ser utilizado
        }
        responses = self.openmeteo.weather_api(self.url, params=params)  # Faz a solicitação à API com os parâmetros definidos
        # Processa a primeira localização.
        response = responses[0]  # Obtém a primeira resposta da API

        # Processa os dados diários. A ordem das variáveis precisa ser a mesma que foi solicitada.
        daily = response.Daily()  # Obtém os dados diários da resposta
        daily_weather_code = daily.Variables(0).ValuesAsNumpy()  # Extrai o código do clima diário como um array numpy
        daily_temperature_2m_mean = daily.Variables(1).ValuesAsNumpy()  # Extrai a temperatura média diária como um array numpy
        # Cria um dicionário para armazenar os dados diários com as datas
        daily_data = {"date": pd.date_range(
            start=pd.to_datetime(daily.Time(), unit="s", utc=True),  # Converte o tempo inicial para datetime
            end=pd.to_datetime(daily.TimeEnd(), unit="s", utc=True),  # Converte o tempo final para datetime
            freq=pd.Timedelta(seconds=daily.Interval()),  # Define a frequência de tempo dos dados
            inclusive="left"  # Inclui o limite inferior do intervalo
        )}
        daily_data["weather_code"] = daily_weather_code  # Adiciona o código do clima ao dicionário
        daily_data["temperature_2m_mean"] = daily_temperature_2m_mean  # Adiciona a temperatura média ao dicionário

        # Converte os dados diários em um DataFrame do pandas
        daily_dataframe = pd.DataFrame(data=daily_data)
        # Renomeia as colunas
        daily_dataframe.columns = ['data', 'clima', 'temperatura media']
        # Trata a coluna de códigos de clima para que seja possível converter de código de clima para texto/descrição do clima
        daily_dataframe['clima'] = daily_dataframe['clima'].apply(lambda x: str(int(x)))


        # URL do arquivo JSON bruto no GitHub com a referência de códigos de clima
        url = "https://gist.githubusercontent.com/stellasphere/9490c195ed2b53c707087c8c2db4ec0c/raw/76b0cb0ef0bfd8a2ec988aa54e30ecd1b483495d/descriptions.json"
        # Faz a requisição GET para a URL
        rjson = requests.get(url)
        
        # Converte o conteúdo da resposta em um dicionário Python
        codigos_clima = json.loads(rjson.text)
        
        
        daily_dataframe['clima'] = daily_dataframe['clima'].apply(lambda x: codigos_clima[x]['day']['description'])

        # Retorna um dataframe com dia, código do clima, temperatura
        return daily_dataframe
    

