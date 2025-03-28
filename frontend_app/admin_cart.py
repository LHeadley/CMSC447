from frontend_app.cart import Cart
from nicegui import ui

class AdminCart(Cart):
    def __init__(self, cart_owner=None):
        super().__init__(cart_owner)
        self.restock_btn = None

    def render(self):
        #checkout button
        self.table = ui.table(columns=self.columns, rows=self.rows)
        self.checkout_btn = ui.button('Checkout')
        self.checkout_btn.on_click(lambda: self.checkout())

        #restock button
        self.restock_btn = ui.button('Restock')
        self.restock_btn.on_click(lambda: self.restock())

    def restock(self):
        print('restock button clicked')

