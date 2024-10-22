import json
import requests
import re


# Информация о заказах с Озона
class OzonOrder:
    def __init__(self, api_key, client_id):
        self.api_key = api_key
        self.client_id = client_id
        self.url_ozon = "https://api-seller.ozon.ru/v3/posting/fbs/unfulfilled/list"

    def get_orders(self):
        header_ozon = {
            "Api-Key": self.api_key,
            "Client-Id": self.client_id,
            "Content-Type": "application/json",
            "Accept-Language": "ru-RU"
        }

        body = {
            "dir": "ASC",
            "filter": {
                "cutoff_from": "2024-01-28T09:00:00Z",
                "cutoff_to": "2024-12-23T17:00:00Z",
                "delivery_method_id": [],
                "provider_id": [],
                "status": "awaiting_deliver",
                "warehouse_id": []
            },
            "limit": 100,
            "offset": 0,
            "with": {
                "analytics_data": True,
                "barcodes": True,
                "financial_data": True,
                "translit": True
            }
        }

        ozon_response = json.loads((requests.post(self.url_ozon, headers=header_ozon, data=json.dumps(body))).text)
        return ozon_response


ozon_order = OzonOrder("", "")  # api и client id Озона
orders = ozon_order.get_orders()

postings = orders['result']['postings']
russian_post_data = {
    "address-type-to": "DEFAULT",
    "mail-type": "ONLINE_PARCEL",
    "mail-category": "ORDINARY",
    "mail-direct": 643,
    "mass": 1000,
    "index-to": 108832,
    "region-to": "Кленовское пос",  # область
    "place-to": "Лукошкино",  # город
    "street-to": "Невская ул.",
    "house-to": "28",
    "recipient-name": "",  # имя
    "postoffice-code": "400066",  # Всегда!
    "tel-address": "79676920725",
    "order-num": "73169698-0116-3"
}

# Информация о запросе в Почту России
url_pochta = "https://otpravka-api.pochta.ru/1.0/user/backlog"
authorization = ""  # Ваш токен в Почте России
user_authorization = ""  # Ваш ключ в Почте России

# Заголовки запроса с API key и Client ID
header_pochta = {
    "Authorization": authorization,
    "X-User-Authorization": user_authorization,
    "Content-Type": "application/json;charset=UTF-8"
}

for posting in postings:

    index_to = int(posting['customer']['address']['zip_code'])
    russian_post_data['index-to'] = index_to

    region_to = posting['analytics_data']['region']
    russian_post_data['region-to'] = region_to

    place_to = posting['analytics_data']['city']
    russian_post_data['place-to'] = place_to

    # Получение номера дома
    match = re.search(r'd\.\s?(\d+)', posting['customer']['address']['address_tail'])
    if match:
        house_to = match.group(1)
    russian_post_data['house-to'] = house_to

    recipient_name = posting['addressee']['name'][:-1]
    russian_post_data['recipient-name'] = recipient_name

    order_num = posting['posting_number']
    russian_post_data['order-num'] = order_num

    tracking_num = posting['tracking_number']

    print(russian_post_data)
