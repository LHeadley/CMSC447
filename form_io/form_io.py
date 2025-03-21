import csv

from api import inventoryapi
from api.inventoryapi import APIResponse, ResponseStatus
from models.request_schemas import CreateRequest, ItemRequest, MultiItemRequest, ActionTypeModel, WeekdayModel
from models.response_schemas import ItemResponse, TransactionResponse, MessageResponse, TransactionItemResponse

from server import app, get_items, db_context


def form_io_read_file(filename):
    with open(filename, 'r', newline='') as csvfile:
        # detect dialect with sample from csvfile
        dialect = csv.Sniffer().sniff(csvfile.read(1024))
        csvfile.seek(0)
        # grab rows from file
        myreader = csv.reader(csvfile, dialect)
        data = []
        for row in myreader:
            data.append([row[0], int(row[-1])])

    return data

def form_io_import(url, filename):
    # get relevant data from file
    data = form_io_read_file(filename)
    
    # put data into DB
    with db_context() as db:
        items = get_items(db)

    for row in data:
        request = CreateRequest(
            name=row[0],
            initial_stock=row[1],
            max_checkout=5
        )

        # send request to db
        res: APIResponse = inventoryapi.create_item(item=request, url=url, timeout=50)

        # below is plagiarized from api_example.py
        
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
    
