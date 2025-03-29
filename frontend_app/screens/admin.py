from nicegui import APIRouter, ui

from frontend_app.common import show_inventory
from frontend_app.cart import Cart, CartItem #TODO: change for adminCart

router = APIRouter(prefix='/admin')


# TODO: Add item creation, logs and restocking
@router.page('')
def admin_page():
    ui.page_title('Admin | Retriever Essentials')
    ui.label('Admin Dashboard')
    show_inventory()

    ui.button("Run Report")
    # TODO: make report button switch to report screen
    with ui.row():
        choiceLabel = ui.label("CHOICE: ")
        restockChoice = ui.switch()
        # bind label text to the switch's current position
        choiceLabel.bind_text_from(restockChoice, "value",
                                 lambda v: "Restocking: " if v==False else "Creating: " )

    # creating vs restocking; bind visibility to switch's current position
    ### restocking; visibility opposite switch value ###
    with ui.column().bind_visibility_from(restockChoice, "value",
                                          lambda v: not v):
        ui.label("RESTOCK EXISTING ITEMS")
        ui.space()

        #TODO: this idea, but with an admin version of 'cart'
        ui.label("CURRENT RESTOCK ORDER:")
        restockCart = Cart()
        restockCart.render()
        restockCart.checkout_btn.text = "Restock"
        ui.space()
        #TODO: end todo

        # import/export restock order
        with ui.row():
            ui.label("Import: ")
            # import on_click currently dummy function
            ui.button("Upload File", on_click=lambda: importFile())
            ui.label(" or ")
            ui.textarea("Copy/Paste Spreadsheet", placeholder="paste here")
        with ui.row():
            ui.label("Export: ")
            exportOptions = ["Current Inventory", "Transactions", "Orders", "Logs"]
            exportChoice = ui.select(exportOptions, label="What to Export", value="Current Inventory")
            # export on_click currently dummy function
            ui.button("Export", on_click=lambda: exportFile(exportChoice.value))

        ui.space()
        # manual item input
        with ui.row():
            ui.label("OR input each item manually: ")
            addBtn = ui.button("Add to Restock Order")

            # item information
            addID = ui.number("Item ID", value=0)
            addName = ui.input("Item Name", value="")
            addAmt = ui.number("Amount In-Stock", value=0)
            addMax = ui.number("Max Allowed per Checkout", value=0)

            # set restock-button to take info from input fields
            addBtn.on_click(lambda: addCartItem(restockCart, addID.value, addName.value, addAmt.value, addMax.value))
            # bind restock-button clickability to valid input; have to bind to all
            addBtn.bind_enabled_from(addID, "value",
                                     lambda v: validInput(v, addName.value, addAmt.value, addMax.value))
            addBtn.bind_enabled_from(addName, "value",
                                     lambda v: validInput(addID.value, v, addAmt.value, addMax.value))
            addBtn.bind_enabled_from(addAmt, "value",
                                     lambda v: validInput(addID.value, addName.value, v, addMax.value))
            addBtn.bind_enabled_from(addMax, "value",
                                     lambda v: validInput(addID.value, addName.value, addAmt.value, v))

    ### creating; visibility matches switch value ###
    with ui.column().bind_visibility_from(restockChoice, "value"):
        makeBtn = ui.button("CREATE NEW ITEM")

        # item information
        makeID = ui.number("Item ID", value=0)
        makeName = ui.input("Item Name", value="")
        makeAmt = ui.number("Amount In-Stock", value=0)
        makeMax = ui.number("Max Allowed per Checkout", value=0)

        # set create-item button to take info from input fields
        makeBtn.on_click(lambda: makeItem(makeID.value, makeName.value, makeAmt.value, makeMax.value))
        # bind create-item button clickability to valid input; have to bind to all
        makeBtn.bind_enabled_from(makeID, "value",
                                  lambda v: validInput(v, makeName.value, makeAmt.value, makeMax.value))
        makeBtn.bind_enabled_from(makeName, "value",
                                  lambda v: validInput(makeID.value, v, makeAmt.value, makeMax.value))
        makeBtn.bind_enabled_from(makeAmt, "value",
                                  lambda v: validInput(makeID.value, makeName.value, v, makeMax.value))
        makeBtn.bind_enabled_from(makeMax, "value",
                                  lambda v: validInput(makeID.value, makeName.value, makeAmt.value, v))


def validInput(id: int, name: str, amt: int, max: int) -> bool:
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


def addCartItem(cart: Cart, id: int, name: str, amt: int, max: int) -> None:
    # take input information and add an item to the restock cart
    #TODO: validation
    item = CartItem(id=id, name=name, quantity=amt, max_checkout=max)
    cart.add_to_cart(item)


def makeItem(id: int, name: str, amt: int, max: int):
    # dummy function for making new cart item
    ui.notify(f"ITEM MADE: id:{id}, name:{name}, amt:{amt}, max:{max}", close_button="close")


# dummy functions for import/export #
def importFile():
    # dummy function for now, for importing spreadsheet
    ui.notify("FILE GRABBED", close_button="close")


def exportFile(whichFile):
    # dummy function for now, for exporting spreadsheet
    ui.notify(f"FILE SENT ({whichFile})", close_button="close")
