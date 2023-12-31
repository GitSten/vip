import requests
from datetime import datetime, timedelta


def get_orders_in_range(start_date, end_date):
    url = ''  #your url

    # WooCommerce API credentials
    consumer_key = '' #your api key
    consumer_secret = '' #your api key

    per_page = 100  # Adjust as needed based on your requirements

    orders = []

    page = 1
    while True:
        params = {
            'consumer_key': consumer_key,
            'consumer_secret': consumer_secret,
            'page': page,
            'per_page': per_page,
            'after': start_date.isoformat(),  # ISO 8601 formatted date
            'before': end_date.isoformat(),  # ISO 8601 formatted date
        }

        response = requests.get(url, params=params)

        print(f"Request URL: {response.url}")
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            orders_page = response.json()

            if not orders_page:
                break

            orders.extend(orders_page)
            page += 1
        else:
            print(f"Failed to fetch orders. Status code: {response.status_code}")
            break

    return orders
