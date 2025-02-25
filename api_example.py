import os

from dotenv import load_dotenv

from api import inventoryapi
from api.inventoryapi import APIResponse, ResponseStatus
from models.request_schemas import CreateRequest, ItemRequest, MultiItemRequest, ActionTypeModel, WeekdayModel
from models.response_schemas import ItemResponse, TransactionResponse, MessageResponse, TransactionItemResponse

load_dotenv()
URL = os.getenv('INVENTORY_API_URL', 'http://127.0.0.1:8001')


def main():
    # Set local = False to test with INVENTORY_API_URL
    global URL
    local = True
    if local:
        URL = 'http://127.0.0.1:8001'

    inventory_example()
    create_example()
    item_example()
    checkout_example()
    checkout_multi_example()
    restock_example()
    logs_example()


def inventory_example():
    print('Running inventory example:')
    # Make the API request
    res: APIResponse = inventoryapi.get_inventory(url=URL)

    # Check if the response was a success first
    if res.is_success:
        # If it's a success, then the response model type is guaranteed to be the one specified in the API.
        # In this case, it's guaranteed to be a list[ItemResponse]
        # See models.response_schemas.py for what an ItemResponse contains
        items: list[ItemResponse] = res.model
        for item in items:
            # Do whatever you want with each item
            print(item)
    else:
        print('Something went wrong.')

    print()


def create_example():
    print('Running create example:')
    # Create the request data. See models.request_schemas.py for more details on CreateRequest
    request = CreateRequest(
        name='name',
        unit_weight=1,
        price=1,
        initial_stock=0,
        supplier='A'  # Can be None
    )

    res: APIResponse = inventoryapi.create_item(item=request, url=URL)

    # Check if it was successful
    if res.is_success:
        # Since it was successful, the response type is guaranteed to be a MessageResponse
        message: MessageResponse = res.model
        print(message.message)
    else:
        # If it wasn't successful, res.model will be set to None, but you can check the response status code like this:
        if res.status_code == ResponseStatus.CONFLICT:
            print('HTTP 409 Conflict')
        elif res.status_code == ResponseStatus.INTERNAL:
            print('HTTP 500 Internal Server Error')
        elif res.status_code == ResponseStatus.CONNECTION_ERROR:
            print('Could not connect to server.')
        elif res.status_code == ResponseStatus.TIMEOUT:
            print('Server took too long to respond.')
        elif res.status_code == ResponseStatus.UNKNOWN_ERROR:
            print('An unknown error occurred.')

        # You can also get a human-readable version of the error with:
        print(res.formatted_string())
        # or use res.error. Both will be equal if the request failed

    print()


def item_example():
    print('Running item example:')
    # Make the request
    name = 'name'
    res = inventoryapi.get_item(item_name=name, url=URL)

    if res.is_success:
        # Since it was successful, the model is guaranteed to be an ItemResponse
        item: ItemResponse = res.model
        print(item.name, item.stock, item.unit_weight, item.price, item.supplier)

        # formatted_string can also format successful responses
        print(res.formatted_string())
    # just like before, you can check the failure types
    elif res.status_code == ResponseStatus.NOT_FOUND:
        print('Item not found.')
    else:
        print('Something else went wrong.')

    print()


def checkout_example():
    print('Running checkout (single) example:')

    # Create the request data
    item = ItemRequest(
        name='item',
        quantity=1,
        student_id='ABC123'  # Can be None
    )

    # Make the request
    res = inventoryapi.checkout_item(item=item, url=URL)

    if res.is_success:
        # Since it was successful, the response model is guaranteed to be a MessageResponse
        message: MessageResponse = res.model
        print(message.message)
    elif res.status_code == ResponseStatus.NOT_FOUND:
        print('Item not found.')
    elif res.status_code == ResponseStatus.CONFLICT:
        print('Not enough stock.')
    else:
        print('Something else went wrong.')

    print()


def checkout_multi_example():
    print('Running checkout (multi) example:')

    # You can also checkout multiple items at a time.
    # If performing a multi item request, only the MultiItemRequest itself should have a student ID
    items: list[ItemRequest] = [
        ItemRequest(name='A', quantity=1),
        ItemRequest(name='B', quantity=2),
        ItemRequest(name='C', quantity=1, student_id='ABC123')  # This student ID will be ignored!
    ]

    request = MultiItemRequest(
        items=items,
        student_id='XYZ987'  # This student ID will be used for all items
    )

    res = inventoryapi.checkout_items(items=request, url=URL)
    if res.is_success:
        print('All items have been checked out successfully')
    elif res.status_code == ResponseStatus.NOT_FOUND:
        print('At least 1 item was not found, and so nothing has been checked out.')
    elif res.status_code == ResponseStatus.CONFLICT:
        print('At least 1 item did not have enough quantity, and so nothing has been checked out.')
    else:
        print('Something else went wrong.')
    print()


def restock_example():
    print('Running restock example:')
    # Create the request data. This uses an ItemRequest just like checkout
    item = ItemRequest(
        name='item',
        quantity=1,
        student_id='ABC123'  # Will be ignored if not None.
    )

    # Make the request
    res = inventoryapi.restock_item(item=item, url=URL)

    if res.is_success:
        # Since it was successful, the response model is guaranteed to be a MessageResponse
        message: MessageResponse = res.model
        print(message.message)
    elif res.status_code == ResponseStatus.NOT_FOUND:
        print('Item not found.')
    else:
        print('Something else went wrong.')

    print()


def logs_example():
    print('Running logs example:')

    # Make the request
    res = inventoryapi.get_logs(url=URL)

    if res.is_success:
        # Since it was successful, the response model is guaranteed to be a list[TransactionResponse]
        transactions: list[TransactionResponse] = res.model
        for transaction in transactions:
            print(transaction.transaction_id, transaction.student_id, transaction.day_of_week, transaction.action,
                  transaction.timestamp)

            # Each TransactionResponse is made up of TransactionItemResponses which contain the actual transaction items
            items: list[TransactionItemResponse] = transaction.items
            print('Items: ')
            for item in items:
                print(item.item_name, item.item_quantity)

        # Just like before, you can get a human-readable string with
        print(res.formatted_string())

    # You can also search logs based on item name, weekday, student id, and action (checkout or restock)

    # Get logs for all items with name A
    res = inventoryapi.get_logs(
        item_name='A'
    )

    print(res.formatted_string())

    # Options can be combined so this gets all items checked out on a Monday by student with ID ABC123
    res = inventoryapi.get_logs(
        type=ActionTypeModel.CHECKOUT,
        weekday=WeekdayModel.MONDAY,
        student_id='ABC123'
    )
    print(res.formatted_string())
    print()


if __name__ == '__main__':
    main()
