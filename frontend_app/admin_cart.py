import cart

class Admin_cart(cart):
    def __init__(self, cart_owner=None):
        super.__init__(self, cart_owner)
        self.restock_button = None

    def restock(self):

