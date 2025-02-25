import argparse
import os

from dotenv import load_dotenv

from api.inventoryapi import get_inventory, get_logs, restock_item, checkout_item, delete_all_items, get_item, \
    create_item, checkout_items
from models.request_schemas import ItemRequest, MultiItemRequest, CreateRequest

load_dotenv()

BASE_URL = os.getenv('INVENTORY_API_URL', 'http://127.0.0.1:8001')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Client for Inventory System')
    parser.add_argument('action', choices=['inventory', 'logs', 'restock', 'checkout', 'delete_all', 'create', 'check',
                                           'checkout_multi'],
                        help='Action to perform')
    parser.add_argument('--name', '-n', type=str,
                        help='Item name (required for restock/checkout (single-item)/check/create)')
    parser.add_argument('--quantity', '-q', type=int,
                        help='Quantity (required for restock/checkout (single-item)/create)')
    parser.add_argument('--names', type=str, help='Item name list (required for checkout (multi-item)')
    parser.add_argument('--quantities', type=str, help='Quantity list (required for checkout (multi-item)')
    parser.add_argument('--unit_weight', '--weight', '-weight', '-uw', type=int,
                        help='Weight per unit (required for create)')
    parser.add_argument('--price', '-price', '-p', type=int, help='Price per unit (required for create)')
    parser.add_argument('--local', '-l', action='store_true')
    parser.add_argument('--id', '-i', help='Student ID for use in checkout', type=str)
    parser.add_argument('--supplier', '-s', type=str, help='Supplier name for use in create')
    args = parser.parse_args()

    url = 'http://127.0.0.1:8001' if args.local else BASE_URL
    supplier = args.supplier if args.supplier else None
    student_id = args.id if args.id else None

    if args.action == 'inventory':
        print(get_inventory(url=url).formatted_string())
    elif args.action == 'logs':
        print(get_logs(url=url).formatted_string())
    elif args.action == 'restock':
        if not args.name or args.quantity is None:
            print('Error: --name and --quantity are required for restock.')
        else:
            print(restock_item(ItemRequest(name=args.name, quantity=args.quantity), url=url).formatted_string())
    elif args.action == 'checkout':
        if args.names and args.quantities:
            names = args.names.split(',')
            try:
                quantities = [int(quantity) for quantity in args.quantities.split(',')]
            except ValueError:
                print('Error: --quantities expects a list of comma seperated integers')
                exit()

            if len(names) != len(quantities):
                print('Error: --names and --quantities must both be comma seperated lists s the same length')
            else:
                items = []
                for name, quantity in zip(names, quantities):
                    items.append(ItemRequest(name=name, quantity=quantity))

                print(checkout_items(MultiItemRequest(items=items, student_id=student_id), url=url).formatted_string())
        elif args.name and args.quantity:
            print(checkout_item(ItemRequest(name=args.name, quantity=args.quantity, student_id=student_id),
                                url=url).formatted_string())
        else:
            print('Error: Either --name and --quantity or --names and --quantities are required for checkout.')
    elif args.action == 'delete_all':
        print(delete_all_items(url=url).formatted_string())
    elif args.action == 'check':
        if not args.name:
            print('Error: --name is required.')
        else:
            print(get_item(args.name, url=url).formatted_string())
    elif args.action == 'create':
        if not args.name or args.quantity is None or args.unit_weight is None or args.price is None:
            print('Error: --name, --quantity, --unit_weight and --price are required for creation.')
        else:
            print(create_item(
                item=CreateRequest(name=args.name, initial_stock=args.quantity, unit_weight=args.unit_weight,
                                   price=args.price, supplier=supplier), url=url).formatted_string())
