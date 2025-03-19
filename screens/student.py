from nicegui import APIRouter, ui

from screens.common import show_inventory, show_cart

router = APIRouter(prefix='/student')


@router.page('/{student_id}')
def student_page(student_id: str):
    ui.page_title('Student Dashboard | Retriever Essentials')
    ui.label(f'Student Dashboard - ID: {student_id}')
    ui.label(f'Inventory:')
    show_inventory()
    ui.label(f'Cart')
    show_cart(student_id)
