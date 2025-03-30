from datetime import datetime, timedelta, date
from enum import Enum

from nicegui import ui

from models.request_schemas import ActionTypeModel
from models.response_schemas import TransactionResponse
from server import db_context, get_logs


class ReportType(Enum):
    MOST_POPULAR_FREQUENCY = "Popular Items (Frequency)"
    MOST_POPULAR_QUANTITY = "Popular Items (Quantity)"
    LEAST_POPULAR = "Least Popular"
    PEAK_DAYS = "Peak Days"
    SPECIFIC_ITEM = "Specific Item"


class ReportResult:
    """
    Class for displaying the results of a report.
    """
    report_type: ReportType
    data: list[TransactionResponse]
    item_name: str | None
    start_date: date | None
    end_date: date | None

    def __init__(self, report_type: ReportType,
                 data: list[TransactionResponse],
                 item_name: str | None = None,
                 start_date: date | None = None,
                 end_date: date | None = None) -> None:
        self.report_type = report_type
        self.data = data
        self.item_name = item_name
        self.start_date = start_date
        self.end_date = end_date

    def render(self) -> None:
        """
        Render the report results.
        """
        ui.label(f'Showing {self.report_type.value} results from '
                 f'{self.start_date.isoformat() if self.start_date is not None else "ALL TIME "}'
                 f'{"to " + self.end_date.isoformat() if self.end_date is not None else ""}')

        if len(self.data) == 0:
            ui.label('No logs found for this query')
            return

        for log in self.data:
            print(log.model_dump())

        if self.report_type == ReportType.MOST_POPULAR_FREQUENCY or self.report_type == ReportType.LEAST_POPULAR:
            # go through each log and count the number of times each item was checked out
            item_count = {}
            for log in self.data:
                for item in log.items:
                    # if the item is deleted, we don't want to count it
                    if item.item_name.startswith('[DELETED]'):
                        continue

                    if item.item_name not in item_count:
                        item_count[item.item_name] = 0
                    item_count[item.item_name] += 1

            print(item_count)
            # sort the items by the number of times they were checked out
            sorted_items = sorted(item_count.items(), key=lambda x: x[1],
                                  reverse=self.report_type == ReportType.MOST_POPULAR_FREQUENCY)
            with ui.row():
                ui.table(columns=[{'id': 'item_name', 'label': 'Item Name', 'field': 'item_name'},
                                  {'id': 'frequency', 'label': 'Frequency', 'field': 'frequency'}],
                         rows=[{'item_name': item[0], 'frequency': item[1]} for item in sorted_items])

        elif self.report_type == ReportType.MOST_POPULAR_QUANTITY:
            # go through each log and sum the quantity of each item checked out
            item_count = {}
            for log in self.data:
                for item in log.items:
                    # if the item is deleted, we don't want to count it
                    if item.item_name.startswith('[DELETED]'):
                        continue

                    if item.item_name not in item_count:
                        item_count[item.item_name] = 0
                    item_count[item.item_name] += item.item_quantity

            # sort the items by the number of times they were checked out
            sorted_items = sorted(item_count.items(), key=lambda x: x[1],
                                  reverse=self.report_type == ReportType.MOST_POPULAR_QUANTITY)
            ui.table(columns=[{'id': 'item_name', 'label': 'Item Name', 'field': 'item_name'},
                              {'id': 'quantity', 'label': 'Quantity', 'field': 'quantity'}],
                     rows=[{'item_name': item[0], 'quantity': item[1]} for item in sorted_items])

        elif self.report_type == ReportType.PEAK_DAYS:
            # go through each log and count the number of checkouts per day
            day_count = {}
            for log in self.data:
                log_date = log.timestamp.date()
                if log_date not in day_count:
                    day_count[log_date] = 0
                day_count[log_date] += 1

            # sort the days by the number of checkouts
            sorted_days = sorted(day_count.items(), key=lambda x: x[1], reverse=True)
            ui.table(columns=[{'id': 'date', 'label': 'Date', 'field': 'date'},
                              {'id': 'frequency', 'label': 'Frequency', 'field': 'frequency'}],
                     rows=[{'date': item[0], 'frequency': item[1]} for item in sorted_days])
        elif self.report_type == ReportType.SPECIFIC_ITEM:
            # go through each log and count the number of times the item was checked out
            # and the total quantity checked out
            # and the dates with the most checkouts
            item_quantity = 0
            item_frequency = 0
            highest_quantity_days = {}
            for log in self.data:
                item_frequency += 1
                if log.timestamp.date() not in highest_quantity_days:
                    highest_quantity_days[log.timestamp.date()] = 0

                for item in log.items:
                    if item.item_name != self.item_name:
                        continue

                    highest_quantity_days[log.timestamp.date()] += item.item_quantity
                    item_quantity += item.item_quantity

            ui.label(f'Item "{self.item_name}" was involved in {item_frequency} checkouts'
                     f' with {item_quantity} total being checked out')
            # sort the days by the number of checkouts
            sorted_days = sorted(highest_quantity_days.items(), key=lambda x: x[1], reverse=True)
            ui.table(columns=[{'id': 'date', 'label': 'Date', 'field': 'date'},
                              {'id': 'quantity', 'label': 'Quantity', 'field': 'quantity'}],
                     rows=[{'date': item[0], 'quantity': item[1]} for item in sorted_days])


class AnalyticsRequest:
    min_date_in: ui.input
    max_date_in: ui.input

    past_week_autofill: ui.button
    past_month_autofill: ui.button
    all_time_autofill: ui.button

    submit_btn: ui.button
    name_input: ui.input
    report_select: ui.select

    result_container: ui.element

    def render(self) -> None:
        def submit_report():
            min_date = datetime.fromisoformat(self.min_date_in.value).date() if self.min_date_in.value != '' else None
            max_date = datetime.fromisoformat(self.max_date_in.value).date() if self.max_date_in.value != '' else None
            report_type = ReportType(self.report_select.value)
            item_name = self.name_input.value if report_type == ReportType.SPECIFIC_ITEM else None

            with db_context() as db:
                logs = get_logs(db=db,
                                action=ActionTypeModel.CHECKOUT,
                                item_name=item_name,
                                start_date=min_date,
                                end_date=max_date)
                result = ReportResult(report_type=report_type, data=logs, item_name=item_name, start_date=min_date,
                                      end_date=max_date)

            with self.result_container:
                ui.separator()
                result.render()

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

        # create the container for the report results
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
        for selected_date in [self.min_date_in, self.max_date_in]:
            with selected_date:
                with ui.menu().props('no-parent-event') as menu:
                    with ui.date().bind_value(selected_date) as date_value:
                        date_value.on_value_change(menu.close)
                        with ui.row().classes('justify-end'):
                            ui.button('Close', on_click=menu.close).props('flat')
                with selected_date.add_slot('append'):
                    ui.icon('edit_calendar').on('click', menu.open).classes('cursor-pointer')

        # create the buttons to autofill date
        with ui.row():
            self.past_week_autofill = ui.button('Past 7 Days', on_click=lambda: fill_dates(
                min_date=datetime.today() - timedelta(days=7)))

            self.past_month_autofill = ui.button('Past 30 Days', on_click=lambda: fill_dates(
                min_date=datetime.today() - timedelta(days=30)))

            self.all_time_autofill = ui.button('All Time', on_click=lambda: fill_dates())

        with ui.row():
            self.submit_btn = ui.button('Submit Query')
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

        self.submit_btn.on_click(lambda: submit_report())
        self.result_container = ui.element()
