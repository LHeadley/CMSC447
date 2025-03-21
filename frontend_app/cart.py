from nicegui import ui
from pydantic import BaseModel

from models.request_schemas import ItemRequest, MultiItemRequest
from models.response_schemas import MessageResponse
from server import checkout_item, db_context


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

    def __init__(self, cart_owner=None):
        self.columns = [{'id': 'id', 'label': 'ID', 'field': 'id'},
                        {'name': 'name', 'label': 'Name', 'field': 'name'},
                        {'name': 'quantity', 'label': 'Quantity', 'field': 'quantity'}
                        ]
        self.rows = []
        self.table = None
        self.checkout_btn = None
        self.cart_owner = cart_owner

    def render(self) -> None:
        """
        Render this cart on the page. The cart will automatically be updated when items are added.
        """
        self.table = ui.table(columns=self.columns, rows=self.rows)
        self.checkout_btn = ui.button('Checkout')
        self.checkout_btn.on_click(lambda : self.checkout())
    # TODO: Increment items already in cart instead of adding a new row
    #       Add a button to remove items from the cart
    #       And check items to make sure the cart isn't above the max takeout quantity
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
        # convert cart items to item requests
        requests = []
        for item in self.rows:

            requests.append(ItemRequest(name=item['name'], quantity=item['quantity']))

        #create multi request from item requests
        multi_request = MultiItemRequest(items=requests, student_id=self.cart_owner)

        #pass multi request to checkout_item function
        with db_context() as db:
            result = checkout_item(request=multi_request, db=db)
            if isinstance(result, MessageResponse):
                print('success')
                self.rows.clear()
                self.table.update()
            else:
                print('failure')

