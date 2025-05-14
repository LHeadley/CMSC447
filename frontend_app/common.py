from nicegui import APIRouter, ui, app
from starlette.responses import JSONResponse
from fastapi import Response
import json

from models.request_schemas import CreateRequest
from models.response_schemas import MessageResponse
from server import db_context, create_item
from frontend_app.inventory import Inventory, invalidate_inventory

# for button/color theming
BTN_MAIN = 'btn_main_color'
# for the admin message board
ADMIN_MSG = 'admin_board_message'

#def show_cart(cart_owner: str | None = None, is_admin: bool = False) -> Cart | AdminCart:
#    """
#    Creates a cart and displays it.
#    :param cart_owner: The student ID of the cart owner, to be used in checkout.
#    :param is_admin: If the cart is an admin cart or not
#    """
#    if not is_admin:
#        cart = Cart(cart_owner=cart_owner)
#    else:
#        cart = AdminCart(cart_owner=cart_owner)
#
#    return cart.render()


#def show_inventory() -> Inventory:
#    """
#    Displays all items in the inventory, along with their current stock.
#    """
#    return Inventory().render()

def valid_input(name: str, amt: int, max: int) -> bool:
    # to check all potential input values for validity whenever one is changed
    # TODO: validation directly in inputs? (next sprint?)

    if name is None or len(name.strip()) <= 0:
        return False

    if amt is None or amt <= 0:
        return False

    if max is None or max <= 0:
        return False

    return True


def make_item(name: str, amt: int, max: int):
    # add new item to the database
    with db_context() as db:
        # attempt to add item to database
        form_name = name.strip().upper()
        result = create_item(CreateRequest(name=form_name, initial_stock=amt, max_checkout=max),
                             Response(), db=db)

        # display popup for success or failure
        if isinstance(result, MessageResponse):
            # success
            with ui.dialog() as dialog, ui.card():
                ui.label(result.message)
                ui.button("Close", on_click=dialog.close)
            dialog.open()
        elif isinstance(result, JSONResponse):
            # failure (item already exists)
            with ui.dialog() as dialog, ui.card():
                ui.label(f"Error {result.status_code}: {json.loads(result.body.decode())["message"]}")
                ui.button("Close", on_click=dialog.close)
            dialog.open()

        invalidate_inventory()
