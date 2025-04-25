from nicegui import APIRouter, ui, app

from frontend_app.common import show_inventory, show_cart
from frontend_app.inventory import STUDENT_VISIBLE
from frontend_app.common import BTN_MAIN

router = APIRouter(prefix='/student')


@router.page('/{student_id}')
def student_page(student_id: str):
    ui.page_title('Student Dashboard | Retriever Essentials')
    ui.label(f'Student Dashboard - ID: {student_id}')
    ui.colors(primary=app.storage.general[BTN_MAIN])

    with ui.element().bind_visibility(app.storage.general, STUDENT_VISIBLE):
        show_inventory()
    with ui.card():
        with ui.expansion("CART", value=True):
            show_cart(student_id)
