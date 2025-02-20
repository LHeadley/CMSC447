import argparse
import os

from dotenv import load_dotenv

from api.inventoryapi import get_inventory, get_logs, restock_item, checkout_item, delete_all_items, get_item, \
    create_item

load_dotenv()

BASE_URL = os.getenv('INVENTORY_API_URL', 'http://127.0.0.1:8001')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Client for Inventory System')
    parser.add_argument('action', choices=['inventory', 'logs', 'restock', 'checkout', 'delete_all', 'create', 'check'],
                        help='Action to perform')
    parser.add_argument('--name', '-n', type=str, help='Item name (required for restock/checkout/check/create)')
    parser.add_argument('--quantity', '-q', type=int, help='Quantity (required for restock/checkout/create)')
    parser.add_argument('--unit_weight', '--weight', '-weight', '-uw', type=int,
                        help='Weight per unit (required for create)')
    parser.add_argument('--price', '-price', '-p', type=int, help='Price per unit (required for create)')
    parser.add_argument('--local', '-l', action='store_true')
    args = parser.parse_args()

    if args.local:
        BASE_URL = 'http://127.0.0.1:8001'

    if args.action == 'inventory':
        print(get_inventory().formatted_string())
    elif args.action == 'logs':
        print(get_logs().formatted_string())
    elif args.action == 'restock':
        if not args.name or args.quantity is None:
            print('Error: --name and --quantity are required for restock.')
        else:
            print(restock_item(args.name, args.quantity).formatted_string())
    elif args.action == 'checkout':
        if not args.name or args.quantity is None:
            print('Error: --name and --quantity are required for checkout.')
        else:
            print(checkout_item(args.name, args.quantity).formatted_string())
    elif args.action == 'delete_all':
        print(delete_all_items().formatted_string())
    elif args.action == 'check':
        if not args.name:
            print('Error: --name is required.')
        else:
            print(get_item(args.name).formatted_string())
    elif args.action == 'create':
        if not args.name or args.quantity is None or args.unit_weight is None or args.price is None:
            print('Error: --name, --quantity, --unit_weight and --price are required for creation.')
        else:
            print(create_item(args.name, args.quantity, args.unit_weight, args.price).formatted_string())
