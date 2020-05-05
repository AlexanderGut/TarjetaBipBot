import requests
import os

from flask import request
from flask_restful import Resource
from bs4 import BeautifulSoup


class TelegramBot:

    _url = 'https://api.telegram.org/bot'
    _token = os.getenv('BOT_TOKEN')

    def __init__(self, chat_id):
        self.chat_id = chat_id

    def send_message(self, msg):
        data = {
            "chat_id": self.chat_id,
            "text": msg
        }
        requests.post(
            f"{self._url}{self._token}/sendMessage",
            data=data
        )


class TelegramMessage:

    def __init__(self, telegram_post):
        self._message = telegram_post['message']
        self.chat_id = self._message['chat']['id']
        self.text = self._message['text']
        self.entities = self._message['entities'][0] if 'entities' in self._message.keys() else None

    def is_command(self):
        return True if self.entities and self.entities['type'] == 'bot_command' else False


class SaldoBip:

    _url = 'http://pocae.tstgo.cl/PortalCAE-WAR-MODULE/SesionPortalServlet'

    def __init__(self, card_id):
        self.card_id = card_id
        self._params = {
            "accion": 6,
            "NumDistribuidor": 99,
            "NomUsuario": "usuInternet",
            "NomHost": "AFT",
            "NomDominio": "aft.cl",
            "Trx": "",
            "RutUsuario": 0,
            "NumTarjeta": card_id,
            "bloqueable": ""
        }

    def get_data(self):
        res = requests.get(self._url, params=self._params)
        b = BeautifulSoup(res.text, 'html.parser')
        data_list = b.find_all('td', {'bgcolor': '#B9D2EC'})
        if data_list:
            return {
                "ok": True,
                "card_id": data_list[0].text,
                "state": data_list[1].text,
                "balance": data_list[2].text,
                "balance_date": data_list[3].text
            }
        else:
            return {"ok": False}


class TelegramApi(Resource):

    def post(self):
        body = request.get_json()
        message = TelegramMessage(body)
        bot = TelegramBot(message.chat_id)
        text = message.text
        msg = ''
        if not message.is_command():
            try:
                card_id = int(text)
                saldobip = SaldoBip(card_id)
                res = saldobip.get_data()
                if res['ok']:
                    msg = (
                        f"No° de tarjeta: {res['card_id']}\n"
                        f"Estado de contrato: {res['state']}\n"
                        f"Saldo: {res['balance']}\n"
                        f"Fecha saldo: {res['balance_date']}\n"
                    )

                else:
                    msg = "Error en la consulta"

            except Exception as e:
                msg = f"No° de tarjeta no válido"

        else:
            if message.text == '/start':
                msg = (
                    "¡Bienvenido a TarjetaBipBot!\n"
                    "Solo debes escribir el numero de tu tarjeta bip para hacer la consulta de tu saldo."
                )
            else:
                msg = "El comando no es valido"

        bot.send_message(msg)


class ConsultaSaldoApi(Resource):

    def get(self, card_id):
        pass


routes = [
    (TelegramApi, "/telegram"),
    (ConsultaSaldoApi, "/consultasaldo/<card_id>")
]


def init_routes(api):
    for route in routes:
        api.add_resource(route[0], f"/api{route[1]}")
