from nicegui import ui
from pydantic import BaseModel


class CartItem(BaseModel):
    """
    Represents a single item in the cart. Pydantic is used to easily convert to JSON later.
    """
    id: int
    name: str
    quantity: int


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

    # TODO: Increment items already in cart instead of adding a new row
    #       Add a button to remove items from the cart
    #       And check items to make sure the cart isn't above the max takeout quantity
    def add_to_cart(self, item: CartItem) -> None:
        """
        Adds an item to the cart. If the cart has already been rendered, it will be updated.
        :param item: The item to add.
        """
        if item.quantity > 0:
            self.rows.append(item.model_dump())
            if self.table is not None:
                self.table.update()
