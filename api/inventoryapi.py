import json
import os
from enum import Enum

import requests
from dotenv import load_dotenv
from tabulate import tabulate

load_dotenv()
BASE_URL = os.getenv('INVENTORY_API_URL', 'http://127.0.0.1:8001')


class ResponseStatus(Enum):
    """
    Enum representing the response status code, along with other request failure types.
    """
    OK = 200
    CREATED = 201
    NOT_FOUND = 404
    CONFLICT = 409
    UNPROCESSABLE_CONTENT = 422
    INTERNAL = 500
    CONNECTION_ERROR = -2
    TIMEOUT = -1
    UNKNOWN_ERROR = 0


class APIResponse:
    """
    Wrapper class for the API response.

    Attributes:
         response (requests.Response): Response from API. None if the request failed.
         status_code (ResponseStatus): ResponseStatus representing the HTTP status code.
         raw_status_code (int): Response status code. -1 if the request failed.
         is_success (bool): True if the response status code is a 2xx status code.
         is_json (bool): True if the response status code is a json object.
         error (str): Error message if the request failed.
    """
    response: requests.Response = None
    status_code: ResponseStatus
    raw_status_code: int
    is_success: bool
    is_json: bool
    error: str = None

    def __init__(self, response: requests.Response = None, error: str = None,
                 status: ResponseStatus = None):
        self.response = response

        if status is None:
            if response is not None:
                self.status_code = ResponseStatus(response.status_code) \
                    if response.status_code in [item.value for item in ResponseStatus] \
                    else ResponseStatus.UNKNOWN_ERROR
            else:
                self.status_code = ResponseStatus.UNKNOWN_ERROR
        else:
            self.status_code = status

        self.is_success = self.status_code in (ResponseStatus.OK, ResponseStatus.CREATED)

        self.is_json = False
        self.json = None
        self.error = error
        self.raw_status_code = -1
        if response is not None:
            self.raw_status_code = response.status_code

            if not self.is_success and error is None:
                self.error = f'Failed with status code {self.raw_status_code}: {response.text}'
            try:
                self.json = response.json()
                self.is_json = True
            except json.decoder.JSONDecodeError:
                self.is_json = False

    def formatted_string(self) -> str:
        """
        Creates a formatted string representation of the response.
        :return: A formatted string representation of the response.
        """
        if not self.is_success:
            return f'{self.error}'

        if self.is_json:
            headers = 'keys'
            data = self.json

            if isinstance(data, dict):
                data = [[key, value] for key, value in data.items()]
                headers = ['Key', 'Value']

            return tabulate(data, headers=headers, tablefmt='grid')
        elif self.is_success:
            return self.response.text


def _make_request(method: str, endpoint: str, timeout: int = 5, **kwargs) -> APIResponse:
    """
    Internal method to make an API request.
    :param method: The HTTP request method to use.
    :param endpoint: The endpoint to make the API request.
    :param timeout: The timeout in seconds to make the API request.
    :param kwargs: Additional keyword arguments to pass to the request.
    :return: The APIResponse object representing the API response.
    """
    try:
        response = requests.request(method, endpoint, timeout=timeout, **kwargs)
        return APIResponse(response)
    except requests.exceptions.Timeout:
        return APIResponse(error='Request timed out', status=ResponseStatus.TIMEOUT)
    except requests.exceptions.ConnectionError:
        return APIResponse(error='Connection error', status=ResponseStatus.CONNECTION_ERROR)
    except Exception as e:
        return APIResponse(error=str(e), status=ResponseStatus.UNKNOWN_ERROR)


def get_inventory(url: str = BASE_URL, timeout: int = 5) -> APIResponse:
    """
    Make a request to get a list of inventory items.
    :param url: The URL to make the API request.
    :param timeout: The timeout in seconds to make the API request.
    :return: APIResponse object representing the API response.
    """
    return _make_request(method='GET', endpoint=f'{url}/items', timeout=timeout)


def get_logs(url: str = BASE_URL, timeout: int = 5) -> APIResponse:
    """
    Make a request to get a list of all logs.
    :param url: The URL to make the API request.
    :param timeout: The timeout in seconds to make the API request.
    :return: APIResponse object representing the API response.
    """
    return _make_request(method='GET', endpoint=f'{url}/logs', timeout=timeout)


def get_item(item_name: str, url: str = BASE_URL, timeout: int = 5) -> APIResponse:
    """
    Make a request to get a specific item.
    :param item_name: The name of the item to get.
    :param url: The URL to make the API request.
    :param timeout: The timeout in seconds to make the API request.
    :return: APIResponse object representing the API response.
    """
    return _make_request(method='GET', endpoint=f'{url}/items/{item_name}', timeout=timeout)


def restock_item(item_name: str, quantity: int, url: str = BASE_URL, timeout: int = 5) -> APIResponse:
    """
    Make a request to restock a specific item.
    :param item_name: The name of the item to restock.
    :param quantity: The number of items to restock.
    :param url: The URL to make the API request.
    :param timeout: The timeout in seconds to make the API request.
    :return: APIResponse object representing the API response.
    """
    return _make_request(method='POST', endpoint=f'{url}/restock', timeout=timeout,
                         json={'name': item_name, 'quantity': quantity})


def checkout_item(item_name: str, quantity: int, url: str = BASE_URL, timeout: int = 5) -> APIResponse:
    """
    Make a request to check out a specific item.
    :param item_name: Item to checkout.
    :param quantity: Quantity to checkout.
    :param url: The URL to make the API request.
    :param timeout: The timeout in seconds to make the API request.
    :return: APIResponse object representing the API response.
    """
    return _make_request(method='POST', endpoint=f'{url}/checkout', timeout=timeout,
                         json={'name': item_name, 'quantity': quantity})


def create_item(item_name: str, initial_stock: int, unit_weight: int, price: int, url: str = BASE_URL,
                timeout: int = 5) -> APIResponse:
    """
    Make a request to create a new item.
    :param item_name: The name of the new item.
    :param initial_stock: The initial stock of the new item.
    :param unit_weight: Weight per unit, or the amount per unit for the new item.
    :param price: Price per unit for the new item.
    :param url: The URL to make the API request.
    :param timeout: The timeout in seconds to make the API request.
    :return: APIResponse object representing the API response.
    """
    return _make_request(method='POST', endpoint=f'{url}/create', timeout=timeout,
                         json={'name': item_name, 'initial_stock': initial_stock, 'unit_weight': unit_weight,
                               'price': price})


def delete_all_items(url: str = BASE_URL, timeout: int = 5) -> APIResponse:
    """
    Deletes all items from inventory.
    :param url: The URL to make the API request.
    :param timeout: The timeout in seconds to make the API request.
    :return: The APIResponse object representing the API response.
    """
    return _make_request(method='DELETE', endpoint=f'{url}/delete_all', timeout=timeout)
