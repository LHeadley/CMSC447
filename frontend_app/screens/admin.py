from nicegui import APIRouter, ui

from frontend_app.common import show_inventory

router = APIRouter(prefix='/admin')


# TODO: Add item creation, logs and restocking
@router.page('')
def admin_page():
    ui.page_title('Admin | Retriever Essentials')
    ui.label('Admin Dashboard')
    show_inventory()
