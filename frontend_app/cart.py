import json
from typing import Self

from nicegui import ui, app
from pydantic import BaseModel
from starlette.responses import JSONResponse

from frontend_app.inventory import invalidate_inventory, INV_VALID_FLAG
from frontend_app.common import valid_input, make_item, upload_image
from models.request_schemas import ItemRequest, MultiItemRequest
from models.response_schemas import MessageResponse
from server import checkout_item, db_context, get_items


class CartItem(BaseModel):
    """
    Represents a single item in the cart. Pydantic is used to easily convert to JSON later.
    """
    id: int
    name: str
    quantity: int
    max_checkout: int


class Cart:
    """
    Represents a Cart to be displayed on the page.
    """
    table: ui.table
    columns: list
    rows: list
    checkout_btn: ui.button
    cart_owner: str | None

    name_max_map: dict[str, int]
    name_id_map: dict[str, int]
    name_in: ui.select
    quantity_select: ui.number

    def __init__(self, cart_owner=None):
        self.columns = [
            # {'id': 'id', 'label': 'ID', 'field': 'id'},
            {'name': 'name', 'label': 'Name', 'field': 'name'},
            {'name': 'quantity', 'label': 'Quantity', 'field': 'quantity'}
        ]
        self.rows = []
        self.table = None
        self.checkout_btn = None
        self.clear_btn = None
        self.cart_owner = cart_owner

        self.name_max_map = {}
        self.name_id_map = {}
        self.name_in = None
        self.quantity_select = None

        # when the inventory is invalidated, update the name_max_map and name_id_map
        app.storage.general.on_change(lambda e: update_event(e))

        def update_event(event):
            if INV_VALID_FLAG in event.sender:
                self.update()

    def update(self) -> None:
        """
        Updates the cart with the current items in the database.
        """
        with db_context() as db:
            items = get_items(db)
        self.name_max_map = {item.name: item.max_checkout for item in items}
        self.name_id_map = {item.name: item.id for item in items}

    def render(self) -> Self:
        """
        Render this cart on the page. The cart will automatically be updated when items are added.
        """
        self.update()
        self.table = ui.table(columns=self.columns, rows=self.rows)
        self.render_item_input()
        self.render_btns()
        return self

    def set_quantity_max(self, item_name: str) -> None:
        """
        Sets the max quantity for the item input based on the item name.
        :param item_name: The name of the item to set the max quantity for.
        """
        self.quantity_select.max = self.name_max_map.get(item_name, 0)

    def render_item_input(self) -> None:
        """
        Renders the item input for the cart. This is a text input for the item name and a number input for the quantity,
        along with a button to add the item to the cart.
        """
        with ui.row():
            # adds the name text input which checks if each name is actually an item
            items = [key for key in self.name_id_map.keys()]
            items.insert(0, "Select Item")
            self.name_in = ui.select(label="Product Name", options=items, with_input=True,
                                     value=items[0])

            # adds the quantity selector and ensures that quantity is a positive integer
            self.quantity_select = ui.number(label='Quantity', max=0, min=0, value=0,
                                             validation=lambda quantity:
                                             None if isinstance(quantity, int) or quantity.is_integer()
                                             else 'Quantity must be an integer').classes('w-10')

            # and only enables the quantity selector if the item typed in is valid
            self.quantity_select.bind_enabled_from(self.name_in, 'value',
                                                   lambda v: v in self.name_id_map.keys())
            # and sets the max quantity to the max checkout quantity of the item typed in
            self.name_in.on_value_change(lambda e: self.set_quantity_max(e.value))

            # make add-to-cart button and bind to item validation and quantity
            add_btn = ui.button('Add to Cart')
            add_btn.bind_enabled_from(self.quantity_select, target_name="value",
                                      backward=lambda v: v > 0)
            add_btn.bind_enabled_from(self.quantity_select)

            add_btn.on_click(lambda: self.add_to_cart(
                CartItem(id=self.name_id_map.get(self.name_in.value, 0),
                         name=self.name_in.value,
                         quantity=int(self.quantity_select.value),
                         max_checkout=self.name_max_map[self.name_in.value])))

    def render_btns(self) -> None:
        """
        Renders the buttons for the cart, excluding the item input.
        """
        with ui.row():
            #checkout button
            self.checkout_btn = ui.button('Checkout')
            self.checkout_btn.on_click(lambda: self.checkout())

            # clear button
            self.clear_btn = ui.button('Clear Cart')
            self.clear_btn.on_click(lambda: self.clear_cart())

    def add_to_cart(self, item: CartItem) -> None:
        """
        Adds an item to the cart. If the cart has already been rendered, it will be updated.
        :param item: The item to add.
        """
        if item.quantity > 0:
            found = False
            for row in self.rows:
                if row['name'] == item.name:
                    row['quantity'] += item.quantity
                    if row['quantity'] > item.max_checkout:
                        row['quantity'] = item.max_checkout
                    found = True
                    break

            if not found:
                self.rows.append(item.model_dump())

            if self.table is not None:
                self.table.update()

    def checkout(self):
        """

        """
        # convert cart items to item requests
        requests = []
        for item in self.rows:
            requests.append(ItemRequest(name=item['name'], quantity=item['quantity']))

        # create multi request from item requests
        multi_request = MultiItemRequest(items=requests, student_id=self.cart_owner)

        # pass multi request to checkout_item function
        with db_context() as db:
            result = checkout_item(request=multi_request, db=db)
            self.display_result(result)
            invalidate_inventory()

    def display_result(self, result):
        if isinstance(result, MessageResponse):
            self.rows.clear()
            self.table.update()
            with ui.dialog() as dialog, ui.card():
                ui.label('Success')
                ui.button('Close', on_click=dialog.close)
        elif isinstance(result, JSONResponse):
            with ui.dialog() as dialog, ui.card():
                ui.label(f'Error {result.status_code}: {json.loads(result.body.decode("utf-8"))["message"]}')
                ui.button('Close', on_click=dialog.close)
        else:
            with ui.dialog() as dialog, ui.card():
                ui.label('Unknown Error')
                ui.button('Close', on_click=dialog.close)
        dialog.open()

    # dialogue if attempted to restock cart items missing from database
    def create_from_cart(self, result):
        if isinstance(result, JSONResponse):
            print("\n\nCREATING FROM CART\n\n")
            
            missing_jsonstr = json.loads(result.body.decode("utf-8"))["missing"]
            missing = json.loads(missing_jsonstr)

            for i in range(len(missing)):
                
                with ui.dialog() as create_popup, ui.card():
                    ui.label(f'Item not found in database: {missing[i]["name"].upper()}')
                    ui.label(f'Would you like to create it?')
                    make_name = ui.input("Item Name", value=missing[i]["name"].upper())
                    make_max = ui.number("Max Allowed per Checkout", value=0)


                    img_data = {'path': None, 'suffix': None, 'file': None}
                    image_upload = ui.upload(label='Image Upload', auto_upload=True).props('accept=.png,.jpg,.jpeg')
                    image_upload.on_upload(lambda e: upload_image(e, img_data))

                    # set create-item button to take info from input fields
                    def create_btn_action(name, value, img_upload, img_data):
                        make_item(name, 0, value, img_upload, img_data)
                        create_popup.close()
                    create_btn = ui.button('Create', on_click = lambda:create_btn_action(make_name.value, make_max.value, image_upload, img_data))

                    # bind create-item button clickability to valid input; have to bind to all
                    create_btn.bind_enabled_from(make_name, "value",
                                               lambda v: valid_input(v, 1, make_max.value))
                    create_btn.bind_enabled_from(make_max, "value",
                                               lambda v: valid_input(make_name.value.upper(), 1, v))

                    cancel_btn = ui.button('Cancel', on_click=create_popup.close())

                create_popup.open().wait()
            
        
    def clear_cart(self):
        self.rows.clear()
        self.table.update()
