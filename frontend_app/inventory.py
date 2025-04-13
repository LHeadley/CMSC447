from typing import Self

from nicegui import ui, app
from nicegui.functions.update import update

from server import db_context, get_items

INV_VALID_FLAG = 'inv_valid'
STUDENT_VISIBLE = 'student_visible'

class Inventory:
    table: ui.table

    def render(self) -> Self:
        """
        Displays all items in the inventory, along with their current stock.
        """
        with db_context() as db:
            items = get_items(db)

        def swap_toggle(visible: bool):
            toggle.text = 'Hide Inventory' if visible else 'Show Inventory'

        toggle = ui.expansion(text='Hide Inventory', value=True)
        toggle.on_value_change(lambda e: swap_toggle(e.value))

        with toggle:
            self.table = ui.table(
                columns=[
                    {'id': 'id', 'label': 'ID', 'field': 'id'},
                    {'name': 'name', 'label': 'Name', 'field': 'name'},
                    {'name': 'stock', 'label': 'Stock', 'field': 'stock'},
                    {'name': 'max_checkout', 'label': 'Max Checkout', 'field': 'max_checkout'},
                ],
                rows=[item.model_dump() for item in items],
                pagination=5
            )
        app.storage.general.on_change(lambda e: refresh(e))

        def refresh(event):
            if INV_VALID_FLAG in event.sender:
                update(self)

        return self

    def update(self):
        if self.table is not None:
            with db_context() as db:
                new_items = get_items(db)
                self.table.rows.clear()
                self.table.rows = [item.model_dump() for item in new_items]


def invalidate_inventory() -> None:
    """
    Invalidates the inventory by marking a general storage flag.
    This is then checked by show_inventory to refresh clients inventory lists.
    Only call this after making an edit to the inventory (like checkout/restock).
    """
    app.storage.general[INV_VALID_FLAG] = app.storage.general.get(INV_VALID_FLAG, 0) + 1
