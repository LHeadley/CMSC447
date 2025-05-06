from pathlib import Path
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

        toggle = ui.expansion(text='Inventory', value=True)

        with toggle:
            self.table = ui.table(
                columns=[
                    {'name': 'id', 'label': 'ID', 'field': 'id'},
                    {'name': 'name', 'label': 'Name', 'field': 'name'},
                    {'name': 'stock', 'label': 'Stock', 'field': 'stock'},
                    {'name': 'max_checkout', 'label': 'Max Checkout', 'field': 'max_checkout'},
                    {'name': 'image', 'label': 'Image', 'field': 'image'}
                ],
                rows=self.create_item_json(items),
                pagination=5
            )

            # insert the images into the table
            # to do this we tell the table to use a custom template for the body
            # where if the column name is 'image', we insert the image
            # otherwise just insert the default value for the column so only images are changed
            self.table.add_slot('body', r'''
            <q-tr :props="props">
                <q-td v-for="col in props.cols" :key="col.name" :props="props">
                    <template v-if="col.name === 'image'">
                        <img :src="`${props.row.image}`"
                             style="width: 100px; height: auto;" />
                    </template>
                    <template v-else>
                        {{ col.value }}
                    </template>
                </q-td>
            </q-tr>
            ''')
        app.storage.general.on_change(lambda e: refresh(e))

        def refresh(event):
            if INV_VALID_FLAG in event.sender:
                update(self)

        return self

    @staticmethod
    def create_item_json(items):
        """
        Creates a JSON representation of the items in the inventory.
        :param items: The items to create a JSON representation of.
        :return: A JSON representation of the items.
        """
        json = []
        for item in items:
            # for images, we use the name of the item as the filename or default.png if it doesn't exist
            image_filename = f'{item.name}.png'
            image_path = Path('static') / image_filename
            image_url = f'/static/{image_filename}' if image_path.exists() else '/static/default.png'

            json.append({
                'id': item.id,
                'name': item.name,
                'stock': item.stock,
                'max_checkout': item.max_checkout,
                'image': image_url,
            })
        return json

    def update(self):
        if self.table is not None:
            with db_context() as db:
                new_items = get_items(db)
                self.table.rows.clear()
                self.table.rows = self.create_item_json(new_items)
                self.table.update()


def invalidate_inventory() -> None:
    """
    Invalidates the inventory by marking a general storage flag.
    This is then checked by show_inventory to refresh clients inventory lists.
    Only call this after making an edit to the inventory (like checkout/restock).
    """
    app.storage.general[INV_VALID_FLAG] = app.storage.general.get(INV_VALID_FLAG, 0) + 1
