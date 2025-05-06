from nicegui import ui

from frontend_app.cart import Cart, CartItem
from frontend_app.inventory import invalidate_inventory
from models.request_schemas import ItemRequest, MultiItemRequest
from server import db_context, restock_item


class AdminCart(Cart):
    def __init__(self, cart_owner=None):
        super().__init__(cart_owner)
        self.restock_btn = None

    def render_btns(self) -> None:
        with ui.row():
            # checkout button
            self.checkout_btn = ui.button('Checkout')
            self.checkout_btn.on_click(lambda: self.checkout())

            # restock button
            self.restock_btn = ui.button('Restock')
            self.restock_btn.on_click(lambda: self.restock())

            # clear button
            self.clear_btn = ui.button('Clear Cart')
            self.clear_btn.on_click(lambda: self.clear_cart())

    def set_quantity_max(self, ignored: str) -> None:
        """
        For admins, this is set to infinity for all items.
        """
        self.quantity_select.max = float('inf')

    def restock(self):
        # convert cart items to item requests
        requests = []
        for item in self.rows:
            requests.append(ItemRequest(name=item['name'], quantity=item['quantity']))

        # create multi request from item requests
        multi_request = MultiItemRequest(items=requests, student_id=self.cart_owner)

        # pass multi request to checkout_item function
        with db_context() as db:
            result = restock_item(request=multi_request, db=db)
            self.display_result(result)
            invalidate_inventory()

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

                    found = True
                    break

            if not found:
                self.rows.append(item.model_dump())

            if self.table is not None:
                self.table.update()
