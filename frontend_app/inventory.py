from pathlib import Path
from typing import Self

from nicegui import ui, app
from nicegui.functions.update import update

from models.response_schemas import ItemResponse
from server import db_context, get_items

INV_VALID_FLAG = 'inv_valid'
STUDENT_VISIBLE = 'student_visible'
TAGS_FIELD = 'tags'


class Inventory:
    table: ui.table
    tag_filter: ui.select

    def render(self) -> Self:
        """
        Displays all items in the inventory, along with their current stock.
        """
        with db_context() as db:
            items = get_items(db)

        toggle = ui.expansion(text='Inventory', value=True)

        with toggle:
            tag_names = list(app.storage.general[TAGS_FIELD])
            tag_names.insert(0, '')
            self.tag_filter = ui.select(tag_names, label='Filter by Tags', with_input=True, clearable=True)

            self.table = ui.table(
                columns=[
                    {'name': 'id', 'label': 'ID', 'field': 'id', 'sortable': True},
                    {'name': 'name', 'label': 'Name', 'field': 'name', 'sortable': True},
                    {'name': 'stock', 'label': 'Stock', 'field': 'stock', 'sortable': True},
                    {'name': 'max_checkout', 'label': 'Max Checkout', 'field': 'max_checkout'},
                    {'name': 'image', 'label': 'Image', 'field': 'image'},
                    {'name': 'tags', 'label': 'Tags', 'field': 'tags'}
                ],
                rows=self.create_item_json(items),
                pagination=5
            )

            self.tag_filter.bind_value(self.table, 'filter')

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

            # set a custom filter function for the table that only filters by the tag column
            self.table.props('''
                :filter-method="(rows, terms, cols) => rows.filter(row => row.tags.toLowerCase().includes(terms.toLowerCase()))"
            ''')
        app.storage.general.on_change(lambda e: refresh(e))

        def refresh(event):
            if INV_VALID_FLAG in event.sender:
                update(self)

        return self

    @staticmethod
    def create_item_json(items: list[ItemResponse]):
        """
        Creates a JSON representation of the items in the inventory.
        :param items: The items to create a JSON representation of.
        :return: A JSON representation of the items.
        """
        json = []
        items.sort(key=lambda e: e.name)

        # tags are a dictionary of tag names to a list of item names
        # we need to find the tags for each item
        tags = app.storage.general[TAGS_FIELD]
        item_tags = {}
        for tag, item_names in tags.items():
            for name in item_names:
                if name not in item_tags:
                    item_tags[name] = []
                item_tags[name].append(tag)

        for item in items:
            # for images, we use the name of the item as the filename or default.png if it doesn't exist
            image_filename = f'{item.name}.png'
            image_path = Path('static') / image_filename
            image_url = f'/static/{image_filename}' if image_path.exists() else '/static/default.png'

            # turn the list of tags for this item into a comma separated string
            tag_list = ', '.join(item_tags.get(item.name, []))

            json.append({
                'id': item.id,
                'name': item.name,
                'stock': item.stock,
                'max_checkout': item.max_checkout,
                'image': image_url,
                'tags': tag_list if tag_list else 'No Tags',
            })

        return json

    def update(self):
        if self.table is not None:
            with db_context() as db:
                new_items = get_items(db)
                self.table.rows.clear()
                self.table.rows = self.create_item_json(new_items)
                self.table.update()

        if self.tag_filter is not None:
            tag_names = list(app.storage.general[TAGS_FIELD])
            tag_names.insert(0, '')
            self.tag_filter.options = tag_names
            self.tag_filter.update()


def invalidate_inventory() -> None:
    """
    Invalidates the inventory by marking a general storage flag.
    This is then checked by show_inventory to refresh clients inventory lists.
    Only call this after making an edit to the inventory (like checkout/restock).
    """
    app.storage.general[INV_VALID_FLAG] = app.storage.general.get(INV_VALID_FLAG, 0) + 1
