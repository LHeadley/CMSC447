import json
import os.path
import tempfile
from pathlib import Path

from PIL import Image
from fastapi import Response
from nicegui import APIRouter, ui, app, events
from starlette.responses import JSONResponse

import server
from frontend_app.analytics import AnalyticsRequest
from frontend_app.cart import CartItem
from frontend_app.admin_cart import AdminCart
from frontend_app.common import valid_input, make_item, upload_image, BTN_MAIN, ADMIN_MSG
from frontend_app.inventory import Inventory, invalidate_inventory, STUDENT_VISIBLE

from models.request_schemas import CreateRequest
from models.response_schemas import MessageResponse
from server import db_context, create_item

try:
    from io import StringIO
    from form_io import form_io
except ImportError:
    print("Error: file_io module (or its dependencies) broken or not present")

router = APIRouter(prefix='/admin')


@router.page('')
def admin_page():
    ui.page_title('Admin | Retriever Essentials')
    ui.label('Admin Dashboard')
    ui.colors(primary=app.storage.general[BTN_MAIN])

    # screen navigation
    with ui.card():
        with ui.row():
            ui.button(text="Logout", on_click=lambda: ui.navigate.to("/"))
            ui.button('Go to Analytics', on_click=lambda: ui.navigate.to('admin/analytics'))

    # inventory
    with ui.card():
        ui.switch(text='Toggle Student Inventory View').bind_value(app.storage.general, STUDENT_VISIBLE)
        Inventory().render()

        with ui.expansion("Cart", value=True):
            curr_cart = AdminCart(cart_owner=None)
            curr_cart.render()

    # creating and importing
    with ui.card():
        ### importing ###
        with ui.expansion("IMPORT/EXPORT"):
            # import/export restock order
            with ui.row():
                ui.label("IMPORT")
                with ui.element('div'):
                    ui.upload(label='Upload file', on_upload=lambda e: import_file(curr_cart, e))
                    ui.label("Select CSV or excel file, then confirm.")
                ui.label(" or ")
                ui.textarea("Copy/Paste Spreadsheet", placeholder="paste here",
                            on_change=lambda e: import_text(curr_cart, e.value)).props('clearable')

            with ui.row():
                ui.label("Export: ")
                export_options = ["Current Inventory", "Transactions", "Orders", "Logs"]
                export_choice = ui.select(export_options, label="What to Export", value="Current Inventory")
                # export on_click currently dummy function
                ui.button("Export", on_click=lambda: export_file(export_choice.value))

    with ui.card():
        ### creating; visibility matches switch value ###
        with ui.expansion("CREATE ITEM"):
            make_btn = ui.button("CREATE NEW ITEM")

            # item information
            make_name = ui.input("Item Name", value="")
            make_amt = ui.number("Amount In-Stock", value=0)
            make_max = ui.number("Max Allowed per Checkout", value=0)

            img_data = {'path': None, 'suffix': None, 'file': None}
            image_upload = ui.upload(label='Image Upload', auto_upload=True).props('accept=.png,.jpg,.jpeg')
            image_upload.on_upload(lambda e: upload_image(e, img_data))

            def clear_fields():
                make_name.value = ''
                make_amt.value = 0
                make_max.value = 0
                image_upload.reset()

            # set create-item button to take info from input fields
            make_btn.on_click(lambda: make_item(make_name.value, make_amt.value, make_max.value, image_upload, img_data))
            # make_btn.on_click(lambda: clear_fields())
            # bind create-item button clickability to valid input; have to bind to all
            make_btn.bind_enabled_from(make_name, "value",
                                       lambda v: valid_input(v, make_amt.value, make_max.value))
            make_btn.bind_enabled_from(make_amt, "value",
                                       lambda v: valid_input(make_name.value, v, make_max.value))
            make_btn.bind_enabled_from(make_max, "value",
                                       lambda v: valid_input(make_name.value, make_amt.value, v))

    with ui.card():
        ### creating; visibility matches switch value ###
        with ui.expansion("DELETE ITEM"):
            delete_btn = ui.button("DELETE ITEM")

            # item information
            delete_name = ui.input("Item Name", value="")

            # set delete-item button to take info from input fields
            delete_btn.on_click(lambda: delete_item(delete_name.value))
            # bind create-item button clickability to valid input; have to bind to all
            delete_btn.bind_enabled_from(delete_name, "value",
                                         lambda v: v)

    # to post messages to the front page
    with ui.card():
        with ui.expansion("ANNOUNCEMENTS"):
            message_btn = ui.button(text="Update Message")
            message_area = ui.textarea(value=app.storage.general[ADMIN_MSG]).props("clearable")

            message_btn.on_click(lambda: post_message(message_area.value))


            
@router.page('/analytics')
def analytics_page():
    ui.button('Home Page', on_click=lambda: ui.navigate.to('/admin'))
    ui.colors(primary=app.storage.general[BTN_MAIN])
    analytics = AnalyticsRequest()
    analytics.render()


# functions for import/export #
def import_file(dest_cart, e):
    # first parse file to extract its data
    ui.notify("FILE GRABBED", close_button="close")
    if (e.name.endswith('.xlsx')):
        data = form_io.read_excel(e.content)
    else:
        data = form_io.read_csv(StringIO(e.content.read().decode('utf-8')))

    print(data)

    # now put the data into CartItems
    for row in data:
        dest_cart.add_to_cart(CartItem(id=1337, name=row[0].upper(), quantity=int(row[1]), max_checkout=12))


def import_text(dest_cart, text):
    # first parse text to extract its data
    ui.notify("DATA GRABBED", close_button="close")

    print("\nTEXT=\n", text)

    data = form_io.read_csv(StringIO(text))
    # now put the data into CartItems
    for row in data:
        dest_cart.add_to_cart(CartItem(id=1337, name=row[0].upper(), quantity=int(row[1]), max_checkout=12))
    print("\nDATA=\n", data)


    
def export_file(which_file):
    # dummy function for now, for exporting spreadsheet
    ui.notify(f"FILE SENT ({which_file})", close_button="close")

    data = [["hello", 132], ["goodbye", 123]]
    re_csv = form_io.server_export("RE_EXPORT.csv")
    ui.download("RE_EXPORT.csv", "RE_EXPORT.csv")


def post_message(message: str):
    # update front page with admin message
    if message is not None:
        ui.notify("Message Updated", close_button="close")
        app.storage.general[ADMIN_MSG] = message
    else:
        ui.notify("Error: cannot update to empty message", close_button="close")


def delete_item(name: str):
    with db_context() as db:
        result = server.delete_item(name, db)

        if isinstance(result, MessageResponse):
            # success
            with ui.dialog() as dialog, ui.card():
                ui.label(result.message)
                ui.button("Close", on_click=dialog.close)
            dialog.open()

            # check if the image file exists, and if it does then delete it
            if name != 'default':
                if os.path.exists(f'static/{name}.png'):
                    os.remove(f'static/{name}.png')

        elif isinstance(result, JSONResponse):
            # failure (item already exists)
            with ui.dialog() as dialog, ui.card():
                ui.label(f"Error {result.status_code}: {json.loads(result.body.decode())["message"]}")
                ui.button("Close", on_click=dialog.close)
            dialog.open()

        invalidate_inventory()
