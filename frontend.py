from nicegui import app as guiapp
from nicegui import ui

from frontend_app.common import BTN_MAIN, ADMIN_MSG
from frontend_app.inventory import INV_VALID_FLAG, TAGS_FIELD
from frontend_app.inventory import STUDENT_VISIBLE
from frontend_app.screens import admin, student
from server import app


# TODO: Switch to using sessions for login screen
# See https://github.com/zauberzeug/nicegui/blob/main/examples/authentication/main.py and https://nicegui.io/documentation/storage
# While authentication is out of the scope of this project, it's still best to have dummy authentication rather than having
# /admin and /student/{student_id} exposed without requiring any login screen beforehand
@ui.page('/')
def show():
    ui.page_title('Login | Retriever Essentials')
    ui.colors(primary=guiapp.storage.general[BTN_MAIN])
    ui.button.default_classes("!text-black")

    with ui.column():
        ui.label('Please select your role:')
        with ui.row():
            ui.button('Admin', on_click=lambda: ui.navigate.to(f'/admin'))
        with ui.row():
            id_input = ui.input('Enter Student ID')
            login_btn = ui.button('Student', on_click=lambda: ui.navigate.to(f'/student/{id_input.value}'))
            # binds the enabled status of the login button to the length of the inputted student id
            # so if len(login_btn.value.strip()) > 0 then the button is enabled, otherwise its disabled
            login_btn.bind_enabled_from(id_input, 'value', backward=lambda e: (len(e.strip()) > 0 and len(e.strip()) <= 10) )

        with ui.card():
            # allows admin messages to be formatted using markdown (incl. html tags)
            ui.markdown("<u> <h4> ANNOUNCEMENTS </h4> </u>")
            ui.markdown(guiapp.storage.general[ADMIN_MSG])


guiapp.storage.general[INV_VALID_FLAG] = 0
if STUDENT_VISIBLE not in guiapp.storage.general:
    guiapp.storage.general[STUDENT_VISIBLE] = True

# tags are a dictionary of tag names to a list of item names
# so tags['tag_name'] = [item_name_1, item_name_2, ...]
# this is because we want to be able to search for items by tag
if TAGS_FIELD not in guiapp.storage.general:
    guiapp.storage.general[TAGS_FIELD] = {}


# theming/colors
guiapp.storage.general[BTN_MAIN] = "#FDB515" # applied through ui.colors
# admin message board
guiapp.storage.general[ADMIN_MSG] = "*announcements from staff go here*"

app.include_router(admin.router)
app.include_router(student.router)
guiapp.add_static_files('/static', 'static')
ui.run_with(app)
