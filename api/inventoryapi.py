import json
import os
from enum import Enum
from typing import Type, List, Union

import requests
from dotenv import load_dotenv
from pydantic import BaseModel, TypeAdapter, ValidationError
from tabulate import tabulate

from models.request_schemas import ItemRequest, MultiItemRequest, CreateRequest, WeekdayModel, ActionTypeModel
from models.response_schemas import ItemResponse, TransactionResponse, MessageResponse

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
         model (extends BaseModel): Model for the response from the server. None if the request failed.
    """
    response: requests.Response = None
    status_code: ResponseStatus
    raw_status_code: int
    is_success: bool
    is_json: bool
    error: str = None
    model: Union[type[BaseModel], list[type[BaseModel]], None]

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
        return ''


def _make_request(expected_response_model: Type, method: str, endpoint: str, timeout: int = 5,
                  **kwargs) -> APIResponse:
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
        apiresponse = APIResponse(response)
        if expected_response_model is not None:
            try:
                adapter = TypeAdapter(expected_response_model)
                model = adapter.validate_python(apiresponse.json)
            except ValidationError:
                model = None
        else:
            model = None
        apiresponse.model = model
        return apiresponse
    except requests.exceptions.Timeout:
        return APIResponse(error='Request timed out', status=ResponseStatus.TIMEOUT)
    except requests.exceptions.ConnectionError:
        return APIResponse(error='Connection error', status=ResponseStatus.CONNECTION_ERROR)
    except Exception as e:
        return APIResponse(error=str(e), status=ResponseStatus.UNKNOWN_ERROR)


def get_inventory(url: str = BASE_URL, timeout: int = 5) -> APIResponse:
    """
    Make a request to get a list of inventory items.
    If successful, the returned APIResponse's model will be set to a List[ItemResponse]
    :param url: The URL to make the API request.
    :param timeout: The timeout in seconds to make the API request.
    :return: APIResponse object representing the API response.
    """
    return _make_request(expected_response_model=List[ItemResponse], method='GET', endpoint=f'{url}/items',
                         timeout=timeout)


def get_logs(item_name: str = None, student_id: str = None, weekday: WeekdayModel = None, type: ActionTypeModel = None,
             url: str = BASE_URL, timeout: int = 5) -> APIResponse:
    """
    Make a request to get a list of all logs.
    If successful, the returned APIResponse's model will be set to a List[TransactionResponse]

    :param item_name: The name of the item to search logs for.
    :param student_id: The student ID to search logs for.
    :param weekday: The day of the week to search logs for.
    :param type: The type of action to search logs for.
    :param url: The URL to make the API request.
    :param timeout: The timeout in seconds to make the API request.
    :return: APIResponse object representing the API response.
    """

    options = []
    if item_name:
        options.append(f'item_name={item_name}')
    if student_id:
        options.append(f'student_id={student_id}')
    if weekday:
        options.append(f'weekday={weekday}')
    if type:
        options.append(f'action={type}')

    opt_str = '&'.join(options)
    return _make_request(expected_response_model=List[TransactionResponse], method='GET',
                         endpoint=f'{url}/logs?{opt_str}',
                         timeout=timeout)


def get_item(item_name: str, url: str = BASE_URL, timeout: int = 5) -> APIResponse:
    """
    Make a request to get a specific item.
    If successful, the returned APIResponse's model will be set to an ItemResponse
    :param item_name: The name of the item to get.
    :param url: The URL to make the API request.
    :param timeout: The timeout in seconds to make the API request.
    :return: APIResponse object representing the API response.
    """
    return _make_request(expected_response_model=ItemResponse, method='GET', endpoint=f'{url}/items/{item_name}',
                         timeout=timeout)


def restock_item(item: ItemRequest, url: str = BASE_URL, timeout: int = 5) -> APIResponse:
    """
    Make a request to restock a specific item.
    If successful, the returned APIResponse's model will be set to a MessageResponse
    :param item: Model containing item to restock.
    :param url: The URL to make the API request.
    :param timeout: The timeout in seconds to make the API request.
    :return: APIResponse object representing the API response.
    """
    return _make_request(expected_response_model=MessageResponse, method='POST', endpoint=f'{url}/restock',
                         timeout=timeout, json=item.model_dump())


def checkout_item(item: ItemRequest, url: str = BASE_URL, timeout: int = 5) -> APIResponse:
    """
    Make a request to check out a specific item.
    If successful, the returned APIResponse's model will be set to a MessageResponse
    :param item: Model containing item to checkout.
    :param url: The URL to make the API request.
    :param timeout: The timeout in seconds to make the API request.
    :return: APIResponse object representing the API response.
    """
    return _make_request(expected_response_model=MessageResponse, method='POST', endpoint=f'{url}/checkout',
                         timeout=timeout, json=item.model_dump())


def checkout_items(items: MultiItemRequest, url: str = BASE_URL, timeout: int = 5) -> APIResponse:
    """
    Make a request to check out multiple items.
    If successful, the returned APIResponse's model will be set to a MessageResponse
    :param items: Model containing items to checkout.
    :param url: The URL to make the API request.
    :param timeout: The timeout in seconds to make the API request.
    :return: APIResponse object representing the API response
    """

    return _make_request(expected_response_model=MessageResponse, method='POST', endpoint=f'{url}/checkout',
                         timeout=timeout, json=items.model_dump())


def create_item(item: CreateRequest, url: str = BASE_URL,
                timeout: int = 5) -> APIResponse:
    """
    Make a request to create a new item.
    If successful, the returned APIResponse's model will be set to a MessageResponse
    :param item: Model containing item to create.
    :param url: The URL to make the API request.
    :param timeout: The timeout in seconds to make the API request.
    :return: APIResponse object representing the API response.
    """
    return _make_request(expected_response_model=MessageResponse, method='POST', endpoint=f'{url}/create',
                         timeout=timeout,
                         json=item.model_dump())


def delete_all_items(url: str = BASE_URL, timeout: int = 5) -> APIResponse:
    """
    Deletes all items from inventory.
    If successful, the returned APIResponse's model will be set to a MessageResponse
    :param url: The URL to make the API request.
    :param timeout: The timeout in seconds to make the API request.
    :return: The APIResponse object representing the API response.
    """
    return _make_request(expected_response_model=MessageResponse, method='DELETE', endpoint=f'{url}/delete_all',
                         timeout=timeout)
