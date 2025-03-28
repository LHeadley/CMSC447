import json

from starlette.responses import JSONResponse
from frontend_app.cart import Cart, CartItem
from nicegui import ui

from models.request_schemas import ItemRequest, MultiItemRequest
from models.response_schemas import MessageResponse
from server import db_context, restock_item


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
        # convert cart items to item requests
        requests = []
        for item in self.rows:
            requests.append(ItemRequest(name=item['name'], quantity=item['quantity']))

        # create multi request from item requests
        multi_request = MultiItemRequest(items=requests, student_id=self.cart_owner)

        # pass multi request to checkout_item function
        with db_context() as db:
            result = restock_item(request=multi_request, db=db)
            if isinstance(result, MessageResponse):
                self.rows.clear()
                self.table.update()
                with ui.dialog() as dialog, ui.card():
                    def reload():
                        dialog.close()
                        ui.navigate.reload()

                    ui.label('Success')
                    ui.button('Close', on_click=dialog.close)

                dialog.on('hide', reload)

            elif isinstance(result, JSONResponse):
                with ui.dialog() as dialog, ui.card():
                    ui.label(f'Error {result.status_code}: {json.loads(result.body.decode("utf-8"))["message"]}')
                    ui.button('Close', on_click=dialog.close)
            else:
                with ui.dialog() as dialog, ui.card():
                    ui.label('Unknown Error')
                    ui.button('Close', on_click=dialog.close)
            dialog.open()

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
