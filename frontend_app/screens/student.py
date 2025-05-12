from nicegui import APIRouter, ui, app

from frontend_app.common import show_inventory, show_cart, manage_dark_mode
from frontend_app.inventory import STUDENT_VISIBLE
from frontend_app.common import BTN_MAIN, DARK_MODE

router = APIRouter(prefix='/student')


@router.page('/{student_id}')
def student_page(student_id: str):
    ui.page_title('Student Dashboard | Retriever Essentials')
    ui.label(f'Student Dashboard - ID: {student_id}')
    ui.colors(primary=app.storage.general[BTN_MAIN])

    dark_mode = ui.dark_mode()
    manage_dark_mode(dark_mode)

    # screen navigation
    with ui.card():
        ui.button(text="Logout", on_click=lambda: ui.navigate.to("/"))

    # functionality
    with ui.card():
        with ui.element().bind_visibility(app.storage.general, STUDENT_VISIBLE):
            show_inventory()
        with ui.expansion("CART", value=True):
            show_cart(student_id)
