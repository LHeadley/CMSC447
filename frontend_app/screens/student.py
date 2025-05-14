from nicegui import APIRouter, ui, app

from frontend_app.inventory import Inventory, STUDENT_VISIBLE
from frontend_app.common import BTN_MAIN
from frontend_app.cart import Cart

router = APIRouter(prefix='/student')


@router.page('/{student_id}')
def student_page(student_id: str):
    ui.page_title('Student Dashboard | Retriever Essentials')
    ui.label(f'Student Dashboard - ID: {student_id}')
    ui.colors(primary=app.storage.general[BTN_MAIN])

    # screen navigation
    with ui.card():
        ui.button(text="Logout", on_click=lambda: ui.navigate.to("/"))

    # functionality
    with ui.card():
        with ui.element().bind_visibility(app.storage.general, STUDENT_VISIBLE):
            Inventory().render()
        with ui.expansion("CART", value=True):
            cart = Cart(cart_owner=student_id)
            cart.render()
