from nicegui import APIRouter, ui, app, events
from starlette.responses import JSONResponse
from fastapi import Response
import json
import tempfile
from pathlib import Path
from PIL import Image

from models.request_schemas import CreateRequest
from models.response_schemas import MessageResponse
from server import db_context, create_item
from frontend_app.inventory import Inventory, invalidate_inventory

from nicegui import app

# for button/color theming
BTN_MAIN = 'btn_main_color'
# for the admin message board
ADMIN_MSG = 'admin_board_message'
# bool for dark mode
DARK_MODE = 'dark_mode_active'


def manage_dark_mode(dark_mode):
    if app.storage.general[DARK_MODE]:
        dark_mode.enable()
       
      
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

    if len(name.strip()) <= 0:
        return False

    if amt <= 0:
        return False

    if max <= 0:
        return False

    return True


def make_item(name_field: str,
              amt_field: int,
              max_field: int,
              upload_field: ui.upload,
              img_data: dict):

    # this is scuffed
    name = name_field
    amt = amt_field
    max_val = max_field
    
    # add new item to the database
    with db_context() as db:
        # attempt to add item to database
        form_name = name.strip().upper()
        result = create_item(CreateRequest(name=form_name, initial_stock=amt, max_checkout=max_val),
                             Response(), db=db)

        # display popup for success or failure
        if isinstance(result, MessageResponse):
            # success
            # now create a new file in /static with the image
            if img_data['file'] is not None:
                dest = Path('static') / f'{name}.png'
                with Image.open(img_data['file']) as img:
                    img.save(dest)

                # clear temp file
                img_data['file'].close()
                img_data['file'] = None
                img_data['path'] = None
                img_data['suffix'] = None

            upload_field.reset()

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


def upload_image(e: events.UploadEventArguments, img_data):
    if e.type not in ['image/png', 'image/jpeg']:
        ui.notify('Only .png and .jpg files are allowed.')
        return

    if img_data['file'] is not None:
        img_data['file'].close()

    temp_img_file = tempfile.NamedTemporaryFile()
    temp_img_file.write(e.content.read())
    img_data['file'] = temp_img_file
    img_data['path'] = temp_img_file.name
    img_data['suffix'] = Path(e.name).suffix
