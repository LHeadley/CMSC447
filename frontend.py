from nicegui import ui

from frontend_app.screens import admin, student
from server import app


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


app.include_router(admin.router)
app.include_router(student.router)

ui.run_with(app)
