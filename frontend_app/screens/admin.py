from nicegui import APIRouter, ui

from frontend_app.analytics import AnalyticsRequest
from frontend_app.common import show_inventory, show_cart
from frontend_app.cart import CartItem


try:
    from io import StringIO
    from form_io import form_io
except ImportError:
    print("Error: file_io module broken or not present")
    
router = APIRouter(prefix='/admin')


# TODO: Add item creation, logs and restocking
@router.page('')
def admin_page():
    ui.page_title('Admin | Retriever Essentials')
    ui.label('Admin Dashboard')
    ui.button('Go to Analytics', on_click=lambda:ui.navigate.to('admin/analytics'))
    show_inventory()

    curr_cart = show_cart('admin', True)

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
            ui.label("IMPORT")
            with ui.element('div'):
                ui.upload(label='Upload file', on_upload=lambda e: import_file(curr_cart, e))
                ui.label("Select CSV or excel file, then confirm.")
            ui.label(" or ")
            ui.textarea("Copy/Paste Spreadsheet", placeholder="paste here").props('clearable')
            
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
        make_id = ui.number("Item ID", value=0)
        make_name = ui.input("Item Name", value="")
        make_amt = ui.number("Amount In-Stock", value=0)
        make_max = ui.number("Max Allowed per Checkout", value=0)

        # set create-item button to take info from input fields
        make_btn.on_click(lambda: make_item(make_id.value, make_name.value, make_amt.value, make_max.value))
        # bind create-item button clickability to valid input; have to bind to all
        make_btn.bind_enabled_from(make_id, "value",
                                   lambda v: valid_input(v, make_name.value, make_amt.value, make_max.value))
        make_btn.bind_enabled_from(make_name, "value",
                                   lambda v: valid_input(make_id.value, v, make_amt.value, make_max.value))
        make_btn.bind_enabled_from(make_amt, "value",
                                   lambda v: valid_input(make_id.value, make_name.value, v, make_max.value))
        make_btn.bind_enabled_from(make_max, "value",
                                   lambda v: valid_input(make_id.value, make_name.value, make_amt.value, v))


@router.page('/analytics')
def analytics_page():
    ui.button('Home Page', on_click=lambda:ui.navigate.to('/admin'))
    analytics = AnalyticsRequest()
    analytics.render()


def valid_input(id: int, name: str, amt: int, max: int) -> bool:
    # to check all potential input values for validity whenever one is changed
    # TODO: check database for repeat ID, name
    if id < 0:
        return False

    if len(name.strip()) <= 0:
        return False

    if amt <= 0:
        return False

    if max <= 0:
        return False

    return True


def make_item(id: int, name: str, amt: int, max: int):
    # dummy function for making new cart item
    ui.notify(f"ITEM MADE: id:{id}, name:{name}, amt:{amt}, max:{max}", close_button="close")


# dummy functions for import/export #
def import_file(dest_cart, e):

    # first parse file to extract its data
    ui.notify("FILE GRABBED", close_button="close")
    if (e.name.endswith('.xlsx')):
        data = form_io.read_excel(e.content)
    else:
        data = form_io.read_csv(StringIO(e.content.read().decode('utf-8')))

    print(data)

    # now put the data into CartItems
    i = 1000
    for row in data:
        dest_cart.add_to_cart(CartItem(id=i, name=row[0], quantity=int(row[1]), max_checkout=12))
        i+=1



def export_file(which_file):
    # dummy function for now, for exporting spreadsheet
    ui.notify(f"FILE SENT ({which_file})", close_button="close")
