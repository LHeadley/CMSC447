import json

from nicegui import APIRouter, ui
from starlette.responses import JSONResponse
from fastapi import Response

from frontend_app.analytics import AnalyticsRequest
from frontend_app.common import show_inventory, show_cart

from server import db_context, create_item
from models.request_schemas import CreateRequest
from models.response_schemas import MessageResponse

router = APIRouter(prefix='/admin')


# TODO: Add item creation, logs and restocking
@router.page('')
def admin_page():
    ui.page_title('Admin | Retriever Essentials')
    ui.label('Admin Dashboard')
    ui.colors(primary='#EBB000') # styling to umbc gold
    
    ui.button('Go to Analytics', on_click=lambda:ui.navigate.to('admin/analytics'))
    show_inventory()

    show_cart('admin', True)

    with ui.row():
        choice_label = ui.label("CHOICE: ")
        restock_choice = ui.switch()
        # bind label text to the switch's current position
        choice_label.bind_text_from(restock_choice, "value",
                                    lambda v: "Import/Export: " if v == False else "Creating: ")

    # creating vs restocking; bind visibility to switch's current position
    ### restocking; visibility opposite switch value ###
    with ui.column().bind_visibility_from(restock_choice, "value",
                                          lambda v: not v):
        # import/export restock order
        with ui.row():
            ui.label("Import: ")
            # import on_click currently dummy function
            ui.button("Upload File", on_click=lambda: import_file())
            ui.label(" or ")
            ui.textarea("Copy/Paste Spreadsheet", placeholder="paste here")
        with ui.row():
            ui.label("Export: ")
            export_options = ["Current Inventory", "Transactions", "Orders", "Logs"]
            export_choice = ui.select(export_options, label="What to Export", value="Current Inventory")
            # export on_click currently dummy function
            ui.button("Export", on_click=lambda: export_file(export_choice.value))

        ui.space()

    ### creating; visibility matches switch value ###
    with ui.column().bind_visibility_from(restock_choice, "value"):
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


@router.page('/analytics')
def analytics_page():
    ui.button('Home Page', on_click=lambda:ui.navigate.to('/admin'))
    analytics = AnalyticsRequest()
    analytics.render()


def valid_input(id: int, name: str, amt: int, max: int) -> bool:
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

        #TODO: reload database/screen/?


# dummy functions for import/export #
def import_file():
    # dummy function for now, for importing spreadsheet
    ui.notify("FILE GRABBED", close_button="close")


def export_file(which_file):
    # dummy function for now, for exporting spreadsheet
    ui.notify(f"FILE SENT ({which_file})", close_button="close")
