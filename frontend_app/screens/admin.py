import json

from fastapi import Response
from nicegui import APIRouter, ui, app
from starlette.responses import JSONResponse

from frontend_app.analytics import AnalyticsRequest
from frontend_app.cart import CartItem
from frontend_app.common import show_inventory, show_cart
from frontend_app.inventory import invalidate_inventory, STUDENT_VISIBLE
from frontend_app.common import BTN_MAIN

from models.request_schemas import CreateRequest
from models.response_schemas import MessageResponse
from server import db_context, create_item


try:
    from io import StringIO
    from form_io import form_io
except ImportError:
    print("Error: file_io module (or its dependencies) broken or not present")

router = APIRouter(prefix='/admin')


# TODO: Add item creation, logs and restocking
@router.page('')
def admin_page():
    ui.page_title('Admin | Retriever Essentials')
    ui.label('Admin Dashboard')
    ui.colors(primary=app.storage.general[BTN_MAIN])

    with ui.card():
        ui.button('Go to Analytics', on_click=lambda: ui.navigate.to('admin/analytics'))
        ui.switch(text='Toggle Student Inventory View').bind_value(app.storage.general, STUDENT_VISIBLE)

    with ui.card():
        show_inventory()

        with ui.expansion("Cart", value=True):
            curr_cart = show_cart('admin', True)


    #with ui.card():
    #    with ui.row():
    #        choice_label = ui.label("CHOICE: ")
    #        restock_choice = ui.switch()
    #        # bind label text to the switch's current position
    #        choice_label.bind_text_from(restock_choice, "value",
    #                                    lambda v: "Import/Export: " if v == False else "Creating: ")


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

            # set create-item button to take info from input fields
            make_btn.on_click(lambda: make_item(make_name.value, make_amt.value, make_max.value))
            # bind create-item button clickability to valid input; have to bind to all
            make_btn.bind_enabled_from(make_name, "value",
                                       lambda v: valid_input(v, make_amt.value, make_max.value))
            make_btn.bind_enabled_from(make_amt, "value",
                                       lambda v: valid_input(make_name.value, v, make_max.value))
            make_btn.bind_enabled_from(make_max, "value",
                                       lambda v: valid_input(make_name.value, make_amt.value, v))

    # to post messages to the front page
    with ui.card():
        with ui.expansion("ANNOUNCEMENTS"):
            message_btn = ui.button(text="Post Message")
            message_area = ui.textarea()

            message_btn.on_click(lambda: post_message(message_area.value))


@router.page('/analytics')
def analytics_page():
    ui.button('Home Page', on_click=lambda: ui.navigate.to('/admin'))
    ui.colors(primary=app.storage.general[BTN_MAIN])
    analytics = AnalyticsRequest()
    analytics.render()


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


def make_item(name: str, amt: int, max: int):
    # add new item to the database
    with db_context() as db:
        # attempt to add item to database
        result = create_item(CreateRequest(name=name, initial_stock=amt, max_checkout=max),
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
        dest_cart.add_to_cart(CartItem(id=1337, name=row[0], quantity=int(row[1]), max_checkout=12))

def import_text(dest_cart, text):
    # first parse text to extract its data
    ui.notify("DATA GRABBED", close_button="close")

    print("\nTEXT=\n", text)
    
    data = form_io.read_csv(StringIO(text))
    # now put the data into CartItems
    for row in data:
        dest_cart.add_to_cart(CartItem(id=1337, name=row[0], quantity=int(row[1]), max_checkout=12))
    print("\nDATA=\n", data)
    

def export_file(which_file):
    # dummy function for now, for exporting spreadsheet
    ui.notify(f"FILE SENT ({which_file})", close_button="close")

    data = [["hello", 132], ["goodbye", 123]]
    re_csv = form_io.server_export("RE_EXPORT.csv")
    ui.download("RE_EXPORT.csv", "RE_EXPORT.csv")


def post_message(message: str):
    # dummy function for posting message; maybe update general storage...?
    ui.notify(message, close_button="close")
