from frontend_app.admin_cart import AdminCart
from frontend_app.cart import Cart
from frontend_app.inventory import Inventory


def show_cart(cart_owner: str | None = None, is_admin: bool = False) -> Cart:
    """
    Creates a cart and displays it.
    :param cart_owner: The student ID of the cart owner, to be used in checkout.
    :param is_admin: If the cart is an admin cart or not
    """
    if not is_admin:
        cart = Cart(cart_owner=cart_owner)
    else:
        cart = AdminCart(cart_owner=cart_owner)

    cart.render()
    return cart


def show_inventory() -> None:
    """
    Displays all items in the inventory, along with their current stock.
    """
    Inventory().render()
