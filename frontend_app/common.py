from nicegui import app, ui

from frontend_app.admin_cart import AdminCart
from frontend_app.cart import Cart, CartItem
from frontend_app.inventory import Inventory
from server import db_context, get_items


def show_cart(cart_owner: str | None = None, is_admin: bool = False) -> None:
    """
    Creates a cart and displays it.
    :param cart_owner: The student ID of the cart owner, to be used in checkout.
    :param is_admin: If the cart is an admin cart or not
    """

    def set_max(item_name: str) -> None:

        if not is_admin:
            quantity_select.max = name_max_map.get(item_name, 0)
        elif is_admin:
            quantity_select.max = float('inf')

    with db_context() as db:
        items = get_items(db)

    name_max_map = {item.name: item.max_checkout for item in items}
    name_id_map = {item.name: item.id for item in items}

    if not is_admin:
        cart = Cart(cart_owner=cart_owner)
    else:
        cart = AdminCart(cart_owner=cart_owner)

    with ui.row():
        # adds the name text input which checks if each name is actually an item
        name = ui.input(label='Product Name', autocomplete=list(name_max_map.keys()),
                        validation=lambda item:
                        None if item in name_max_map.keys()
                        else 'Unknown Product')

        # adds the quantity selector and ensures that quantity is a positive integer
        quantity_select = ui.number(label='Quantity', max=0, min=0, value=0,
                                    validation=lambda quantity:
                                    None if isinstance(quantity, int) or quantity.is_integer()
                                    else 'Quantity must be an integer').classes('w-10')

        # and only enables the quantity selector if the item typed in is valid
        quantity_select.bind_enabled_from(name, 'error', lambda e: e is None)
        # and sets the max quantity to the max checkout quantity of the item typed in
        name.on_value_change(lambda e: set_max(e.value))

        add_btn = ui.button('Add to Cart')
        add_btn.bind_enabled_from(quantity_select)

        add_btn.on_click(lambda: cart.add_to_cart(
            CartItem(id=name_id_map[name.value], name=name.value, quantity=int(quantity_select.value),
                     max_checkout=name_max_map[name.value])))

    cart.render()


def show_inventory() -> None:
    """
    Displays all items in the inventory, along with their current stock.
    """
    Inventory().render()
