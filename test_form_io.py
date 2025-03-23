################################################################################
# File: test_form_io.py                                                        #
#                                                                              #
# Purpose: Test functionality of the form_io module.                           #
# Remember to start server, update PYTHON_BIN, and set the .env file as        #
# appropriate. DO NOT USE ON PRODUCTION DATABASE.                              #
################################################################################

import sys
import os
from dotenv import load_dotenv

from form_io import form_io

# path to the python binary you are using
PYTHON_BIN='~/pyenv/bin/python3'

# update .env to the url & port you are using to test
load_dotenv()
test_url = os.getenv('INVENTORY_API_URL', 'http://127.0.0.1:8001')

# name of the csv to read (can detect delimeters)
CSV_EXAMPLE = 'form_io/example.csv'
XLSX_EXAMPLE = 'form_io/example.xlsx'
CSV_EXPORT = 'form_io/export.csv'
XLSX_EXPORT = 'form_io/export.xlsx'

print("================= SETTING UP ======================")
# THIS WILL CLEAR THE DATABASE
print("Clearing existing database...")
ret = os.system(f'{PYTHON_BIN} client.py delete_all')
if (ret == 0): print(" Done")
else: sys.exit("!! Error clearing the database")


print("\n============= IMPORT EXAMPLE CSV ================")
print(form_io.db_import(test_url, CSV_EXAMPLE))
# To-do... verify

print("================= SETTING UP ======================")
print("Clearing existing database...")
ret = os.system(f'{PYTHON_BIN} client.py delete_all')
if (ret == 0): print(" Done")
else: sys.exit("!! Error clearing the database")

print("\n============= IMPORT EXAMPLE XLSX ===============")
print(form_io.db_import(test_url, XLSX_EXAMPLE))
# To-do... verify

print("\n============= EXPORT EXAMPLE CSV ================")
print(form_io.db_export(test_url, CSV_EXPORT))
# To-do... verify

print("\n============= EXPORT EXAMPLE XLSX ===============")
print(form_io.db_export(test_url, XLSX_EXPORT))
# To-do... verify

print("\n=================================================")
print(" Tests complete!\n")
print(" This is a work in progress; for now tests must be reviewed manually...")
print(" See the export files in the form_io directory.")
print("==================================================")
