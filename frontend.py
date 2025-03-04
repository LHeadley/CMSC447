from nicegui import ui

from server import app, get_items, db_context


# TODO: Switch to using sessions for login screen
# See https://github.com/zauberzeug/nicegui/blob/main/examples/authentication/main.py and https://nicegui.io/documentation/storage
# While authentication is out of the scope of this project, it's still best to have dummy authentication rather than having
# /admin and /student/{student_id} exposed without requiring any login screen beforehand
@ui.page('/')
def show():
    ui.page_title('Login | Retriever Essentials')
    with ui.column():
        ui.label('Please select your role:')
        with ui.row():
            ui.button('Admin', on_click=lambda: ui.navigate.to(f'/admin'))
        with ui.row():
            id_input = ui.input('Enter Student ID')
            login_btn = ui.button('Student', on_click=lambda: ui.navigate.to(f'/student/{id_input.value}'))
            # binds the enabled status of the login button to the length of the inputted student id
            # so if len(login_btn.value.strip()) > 0 then the button is enabled, otherwise its disabled
            login_btn.bind_enabled_from(id_input, 'value', backward=lambda e: len(e.strip()) > 0)


# TODO: Add item creation, logs and restocking
@ui.page('/admin')
def admin_page():
    ui.page_title('Admin | Retriever Essentials')
    ui.label('Admin Dashboard')
    list_items()


@ui.page('/student/{student_id}')
def student_page(student_id: str):
    ui.page_title('Student Dashboard | Retriever Essentials')
    ui.label(f'Student Dashboard - ID: {student_id}')
    list_items()
    create_cart()


def create_cart():
    def set_max(item_name: str) -> None:
        quantity_select.max = name_max_map.get(item_name, 0)

    with db_context() as db:
        items = get_items(db)
    name_max_map = {item.name: item.max_checkout for item in items}
    with ui.row():
        # adds the name text input which checks if each name is actually an item
        name = ui.input(label='Product Name', autocomplete=list(name_max_map.keys()),
                        validation=lambda item: None if item in name_max_map.keys() else 'Unknown Product')
        # adds the quantity selector and ensures that quantity is a positive integer
        quantity_select = ui.number(label='Quantity', max=0, min=0, value=0,
                                    validation=lambda
                                        quantity: None if quantity.is_integer() else 'Quantity must be an integer')
        # and only enables the quantity selector if the item typed in is valid
        quantity_select.bind_enabled_from(name, 'error', lambda e: e is None)
        # and sets the max quantity to the max checkout quantity of the item typed in
        name.on_value_change(lambda e: set_max(e.value))

        add_btn = ui.button('Add to Cart')

    # TODO: Add the rest of the cart functionality


def list_items():
    with db_context() as db:
        items = get_items(db)

    ui.table(
        columns=[
            {'id': 'id', 'label': 'ID', 'field': 'id'},
            {'name': 'name', 'label': 'Name', 'field': 'name'},
            {'name': 'stock', 'label': 'Stock', 'field': 'stock'},
            {'name': 'max_checkout', 'label': 'Max Checkout', 'field': 'max_checkout'},
        ],
        rows=[item.model_dump() for item in items]
    )


ui.run_with(app)
