import argparse
import requests
import json
from tabulate import tabulate

BASE_URL = 'http://127.0.0.1:8000'


def print_table(response):
    try:
        data = response.json()
        print(data)
        if response.status_code != 200 and response.status_code != 201:
            print(f'Error: Received status code {response.status_code}. Reason is {data["detail"]}')

        if isinstance(data, list) and data:
            print(tabulate(data, headers='keys', tablefmt='grid'))
        elif isinstance(data, dict) and 'message' in data:
            print(f'Response:  {data["message"]}')
        else:
            print(json.dumps(data, indent=4))
    except json.JSONDecodeError:
        print(f'Error: Unable to parse json response. Raw response is as follows: {response.text}')
    except KeyError:
        print(f'Error: Unable to parse response. Raw response is as follows: {response.text}')


def get_inventory():
    response = requests.get(f'{BASE_URL}/items')
    print_table(response)


def get_item(name):
    response = requests.get(f'{BASE_URL}/item', json={'name': name})
    print_table(response)


def get_logs():
    response = requests.get(f'{BASE_URL}/logs')
    print_table(response)


def restock_item(name, quantity):
    response = requests.post(f'{BASE_URL}/restock', json={'name': name, 'quantity': quantity})
    print_table(response)


def checkout_item(name, quantity):
    response = requests.post(f'{BASE_URL}/checkout', json={'name': name, 'quantity': quantity})
    print_table(response)


def delete_all_items():
    response = requests.delete(f'{BASE_URL}/delete_all')
    print_table(response)


def create_item(name, initial_stock, unit_weight, price):
    response = requests.post(f'{BASE_URL}/create',
                             json={'name': name, 'initial_stock': initial_stock, 'unit_weight': unit_weight,
                                   'price': price})
    print_table(response)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Client for Inventory System')
    parser.add_argument('action', choices=['inventory', 'logs', 'restock', 'checkout', 'delete_all', 'create', 'check'],
                        help='Action to perform')
    parser.add_argument('--name', '-n', type=str, help='Item name (required for restock/checkout/check/create)')
    parser.add_argument('--quantity', '-q', type=int, help='Quantity (required for restock/checkout/create)')
    parser.add_argument('--unit_weight', '--weight', '-weight', '-uw', type=int,
                        help='Weight per unit (required for create)')
    parser.add_argument('--price', '-price', '-p', type=int, help='Price per unit (required for create)')
    args = parser.parse_args()

    if args.action == 'inventory':
        get_inventory()
    elif args.action == 'logs':
        get_logs()
    elif args.action == 'restock':
        if not args.name or args.quantity is None:
            print('Error: --name and --quantity are required for restock.')
        else:
            restock_item(args.name, args.quantity)
    elif args.action == 'checkout':
        if not args.name or args.quantity is None:
            print('Error: --name and --quantity are required for checkout.')
        else:
            checkout_item(args.name, args.quantity)
    elif args.action == 'delete_all':
        delete_all_items()
    elif args.action == 'check':
        if not args.name:
            print('Error: --name is required.')
        else:
            get_item(args.name)
    elif args.action == 'create':
        if not args.name or args.quantity is None or args.unit_weight is None or args.price is None:
            print('Error: --name, --quantity, --unit_weight and --price are required for creation.')
        else:
            create_item(args.name, args.quantity, args.unit_weight, args.price)
