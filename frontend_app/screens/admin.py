from nicegui import APIRouter, ui

from frontend_app.common import show_inventory

router = APIRouter(prefix='/admin')


# TODO: Add item creation, logs and restocking
@router.page('')
def admin_page():
    ui.page_title('Admin | Retriever Essentials')
    ui.label('Admin Dashboard')
    show_inventory()
    with ui.row():
        # TODO: REPORT BUTTON
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

        # import/export restock order
        with ui.row():
            ui.label("Import: ")
            ui.button("Upload File")
            ui.label(" or ")
            ui.textarea("Copy/Paste Spreadsheet", placeholder="paste here")
        with ui.row():
            ui.label("Export: ")
            exportOptions = ["Current Inventory", "Transactions", "Orders", "Logs"]
            ui.select(exportOptions, label="What to Export", value="Current Inventory")
            ui.button("Export")

        # manual item input
        with ui.row():
            ui.label("OR input each item manually: ")
            addBtn = ui.button("Add to Restock Order")

        # item information
        addID = ui.number("Item ID", value=0)
        addName = ui.input("Item Name", value="")
        addAmt = ui.number("Amount In-Stock", value=0)
        addMax = ui.number("Max Allowed per Checkout", value=0)

        # bind button clickability to valid input; have to bind to all
        addBtn.bind_enabled_from(addID, "value",
                                 lambda v: validInput(v, addName.value, addAmt.value, addMax.value))
        addBtn.bind_enabled_from(addName, "value",
                                 lambda v: validInput(addID.value, v, addAmt.value, addMax.value))
        addBtn.bind_enabled_from(addAmt, "value",
                                 lambda v: validInput(addID.value, addName.value, v, addMax.value))
        addBtn.bind_enabled_from(addMax, "value",
                                 lambda v: validInput(addID.value, addName.value, addAmt.value, v))

        #TODO: display restock order cart

    ### creating; visibility matches switch value ###
    with ui.column().bind_visibility_from(restockChoice, "value"):
        makeBtn = ui.button("CREATE NEW ITEM")

        # item information
        makeID = ui.number("Item ID", value=0)
        makeName = ui.input("Item Name", value="")
        makeAmt = ui.number("Amount In-Stock", value=0)
        makeMax = ui.number("Max Allowed per Checkout", value=0)

        # bind button clickability to valid input; have to bind to all
        makeBtn.bind_enabled_from(makeID, "value",
                                 lambda v: validInput(v, makeName.value, makeAmt.value, makeMax.value) )
        makeBtn.bind_enabled_from(makeName, "value",
                                 lambda v: validInput(makeID.value, v, makeAmt.value, makeMax.value) )
        makeBtn.bind_enabled_from(makeAmt, "value",
                                 lambda v: validInput(makeID.value, makeName.value, v, makeMax.value) )
        makeBtn.bind_enabled_from(makeMax, "value",
                                 lambda v: validInput(makeID.value, makeName.value, makeAmt.value, v) )


def validInput(id: int, name: str, amt: int, max: int) -> bool:
    # to check all potential input values for validity whenever one is changed
    # TODO: check database for repeat ID
    if id < 0:
        return False

    if len(name.strip()) <= 0:
        return False

    if amt <= 0:
        return False

    if max <= 0:
        return False

    return True
