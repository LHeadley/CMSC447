from datetime import datetime, timedelta
from enum import Enum

from nicegui import ui


class ReportType(Enum):
    MOST_POPULAR_FREQUENCY = "Popular Items (Frequency)"
    MOST_POPULAR_QUANTITY = "Popular Items (Quantity)"
    LEAST_POPULAR = "Least Popular"
    PEAK_DAYS = "Peak Days"
    NUM_OF_CHECKOUTS = "Number of Checkouts"
    SPECIFIC_ITEM = "Specific Item"


class AnalyticsRequest:
    min_date_in: ui.input
    max_date_in: ui.input

    past_week_autofill: ui.button
    past_month_autofill: ui.button
    all_time_autofill: ui.button

    submit_btn: ui.button
    name_input: ui.input
    report_select: ui.select

    def render(self) -> None:
        # if either value changes, we need to make sure we check the validation for both of them
        def validate_both_dates() -> None:
            self.max_date_in.validate()
            self.min_date_in.validate()

        # autofill the dates
        def fill_dates(min_date: datetime | None = None, max_date: datetime | None = None) -> None:
            self.min_date_in.value = '' if min_date is None else min_date.date().isoformat()
            self.max_date_in.value = '' if max_date is None else max_date.date().isoformat()

        # the validation takes in the current value of the date selector being changed
        # but since we're going to check both we ignore the value
        # this returns either a string with an error message or None if there's no error message
        def validate_date(ignored) -> str | None:
            if self.min_date_in.value == '' or self.max_date_in.value == '':
                return None

            if datetime.fromisoformat(self.min_date_in.value) > datetime.fromisoformat(self.max_date_in.value):
                return 'End date cannot be before start date'

            return None

        # if the report type is specific item and the item name input hasn't been filled then it's invalid
        # if the report type is any other type or the item name input has been filled then it's always valid
        def validate_report_type(value: str) -> bool:
            return (value == ReportType.SPECIFIC_ITEM.value and self.name_input.value != '') or (
                    value != ReportType.SPECIFIC_ITEM.value and value in ReportType)

        # create the date options
        with ui.row():
            self.min_date_in = ui.input('Start Date')
            self.max_date_in = ui.input('End Date')

            # set the validation function
            self.min_date_in.validation = validate_date
            self.max_date_in.validation = validate_date

            # run the validation function on both dates if either was changed
            self.min_date_in.on_value_change(validate_both_dates)
            self.max_date_in.on_value_change(validate_both_dates)

        # create the date selector GUI
        for date in [self.min_date_in, self.max_date_in]:
            with date:
                with ui.menu().props('no-parent-event') as menu:
                    with ui.date().bind_value(date) as date_value:
                        date_value.on_value_change(menu.close)
                        with ui.row().classes('justify-end'):
                            ui.button('Close', on_click=menu.close).props('flat')
                with date.add_slot('append'):
                    ui.icon('edit_calendar').on('click', menu.open).classes('cursor-pointer')

        # create the buttons to autofill date
        with ui.row():
            self.past_week_autofill = ui.button('Past 7 Days', on_click=lambda: fill_dates(
                min_date=datetime.today() - timedelta(days=7)))

            self.past_month_autofill = ui.button('Past 30 Days', on_click=lambda: fill_dates(
                min_date=datetime.today() - timedelta(days=30)))

            self.all_time_autofill = ui.button('All Time', on_click=lambda: fill_dates())

        with ui.row():
            self.submit_btn = ui.button('Submit Query', on_click=lambda: self.submit_report())
            self.report_select = ui.select(label='Select Report Type',
                                           options=[report.value for report in ReportType]).classes('w-40')

            # the submit button should only be enabled if both the date and report type selections are valid
            # so we have to bind the enabled flag from both the report type selector value AND the date error checking
            # so if either one is changed we check to make sure both are valid
            self.submit_btn.bind_enabled_from(self.report_select, 'value', lambda
                value: self.min_date_in.error is None and validate_report_type(value))

            self.submit_btn.bind_enabled_from(self.min_date_in, 'error', lambda
                error: error is None and validate_report_type(self.report_select.value))

            self.name_input = ui.input('Item Name')
            # only show the item name input if specific item report is selected
            self.name_input.bind_visibility_from(self.report_select, 'value', None,
                                                 value=ReportType.SPECIFIC_ITEM.value)

    def submit_report(self) -> None:
        # placeholder, for now just display all the selected values
        min_date = self.min_date_in.value
        max_date = self.max_date_in.value
        report_type = ReportType(self.report_select.value)
        item_name = self.name_input.value if report_type == ReportType.SPECIFIC_ITEM.value else ""

        with ui.dialog() as dialog, ui.card():
            ui.label(f'Report Type: {report_type.value}')
            ui.label(f'Querying from'
                     f' {min_date if min_date != "" else "all time"} {f" to {max_date}" if max_date is not "" else ""}')
            if report_type == ReportType.SPECIFIC_ITEM:
                ui.label(f'Item Name: {item_name}')
            ui.button('Close', on_click=dialog.close)
        dialog.open()
