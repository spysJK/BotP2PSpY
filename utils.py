import requests
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("API_KEY_COIN")

class Teste:
    def __init__(self,symbol,moeda):
        self.API_KEY = API_KEY
        self.url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
        self.symbol = symbol
        self.moeda = moeda
        
        self.params = {
            "symbol": symbol,
            "convert": moeda
            }

        self.headers = {
            "X-CMC_PRO_API_KEY": self.API_KEY,
            "Accepts": "application/json"
            }

    def requesicao(self):
        resposta = requests.get(self.url,params=self.params,headers=self.headers)
        data = resposta.json()
        preco = data["data"][self.symbol]["quote"][self.moeda]["price"]
        convercao_float = (round(preco,2))
        print(convercao_float)
        return convercao_float
    
