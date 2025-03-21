import csv

from api import inventoryapi
from api.inventoryapi import APIResponse, ResponseStatus
from models.request_schemas import CreateRequest, ItemRequest, MultiItemRequest, ActionTypeModel, WeekdayModel
from models.response_schemas import ItemResponse, TransactionResponse, MessageResponse, TransactionItemResponse

from server import app, get_items, db_context


# - File input/output -

# file format: first col should be product name, last col quantity (other cols ignored)
# TODO: throw errors
# TODO: detect headers
# TODO: excel .xlsx files
def read_file(filename):
    with open(filename, 'r', newline='') as csvfile:
        # detect dialect with sample from csvfile
        dialect = csv.Sniffer().sniff(csvfile.read(1024))
        csvfile.seek(0)
        # grab rows from file
        freader = csv.reader(csvfile, dialect)
        data = []
        for row in freader:
            data.append([row[0], int(row[-1])])

    return data

# data format: list of 2-len ['name', quantity] lists 
def write_file(filename, data):
    
    with open(filename, 'w', newline='') as csvfile:
        fwriter  = csv.writer(csvfile, delimiter=',', dialect='excel');

        for row in data:
            fwriter.writerow(row);
                
    return data;


# - Database interaction -

# TODO: throw errors
def db_import(url, filename):
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

            print(res.formatted_string())


# TODO: throw errors
def db_export(url, filename):

    # send request to db
    res: APIResponse = inventoryapi.get_inventory(url=url, timeout=50)

    # below is plagiarized from api_example.py
        
    # Check if it was successful
    if res.is_success:
        # Since it was successful, the response type is guaranteed to be a MessageResponse
        message: MessageResponse = res.model
        print(message)
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
            
            print(res.formatted_string())

    items: list[ItemResponse] = res.model
    data = [[x.name, x.stock] for x in items]

    write_file(filename, data)
    
