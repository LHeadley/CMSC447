################################################################################
# File: test_form_io.py                                                        #
#                                                                              #
# Purpose: Automated tests for form_io module                                  #
################################################################################

import os
import sys
from dotenv import load_dotenv

from io import StringIO

from form_io import form_io

# name of the csv to read (can detect delimiters)
CSV_EXAMPLE = \
"""Sona Masoori Rice	20	25	13
Toor Dahl (Red Lentils)	179	1.25	179
Black chickpeas (channa)	85	1.25	85
Maggi Noodles	1	0.5	400
PARLE KREAM BOUR	1	0.49	10
P HID SEEK BOURB	1	0.49	10
SW MASL BANA	1	1.99	10
GOP SNACK PE CHO	1	1.29	10
AD BANGA MIX	1	1.99	10
SW BHEL CUP	1	1.29	10
MAGIC MAS UPMA	1	0.89	10
KURKURE MASLLAYS CHILE LIMON	1	0.99	10
MTR navaratan korma	1	2.99	10
MTR alu muttar	1	2.99	10
MTR mutter paneer	1	2.99	10
Mixed vegetable curry	1	2.99	10
MTR palak paneer	1	2.99	10
MTR shahi paneer	1	2.99	10
MTR bhindi masala	1	2.99	10
MTR alu methi	1	2.99	10
MTR chana masala	1	2.99	10
MTR kadhi pakora	1	2.99	10
GITS paneer tikka masala	1	2.99	10
GITS bhindi masala	1	2.99	10
GITS pau bhakti	1	2.99	10
GITS paneer makhani	1	2.99	10
GITS aloo raswala	1	2.99	10
GITS veg biryani	1	2.99	10
5 Minute khana aloo mutter	1	2.99	10
5 Minute khana pao bhaji	1	2.99	10"""
XLSX_EXAMPLE = 'form_io/example.xlsx'
CSV_EXPORT = 'form_io/export.csv'
XLSX_EXPORT = 'form_io/export.xlsx'

PYTHON_BIN = None
TEST_URL = None

def init(python_bin, test_url):
    global PYTHON_BIN
    global TEST_URL
    PYTHON_BIN = python_bin
    TEST_URL = test_url

def setup():
    print("================= SETTING UP ======================")
    # THIS WILL CLEAR THE DATABASE
    print("Clearing existing database...")
    ret = os.system(f'{PYTHON_BIN} client.py delete_all')
    if ret == 0:
        print(" Done")
    else: sys.exit("!! Error clearing the database")
    
def import_example_csv():
    print("\n============= IMPORT EXAMPLE CSV ================")

    expected_result = [['Sona Masoori Rice', 13], ['Toor Dahl (Red Lentils)', 179], ['Black chickpeas (channa)', 85], ['Maggi Noodles', 400], ['PARLE KREAM BOUR', 10], ['P HID SEEK BOURB', 10], ['SW MASL BANA', 10], ['GOP SNACK PE CHO', 10], ['AD BANGA MIX', 10], ['SW BHEL CUP', 10], ['MAGIC MAS UPMA', 10], ['KURKURE MASLLAYS CHILE LIMON', 10], ['MTR navaratan korma', 10], ['MTR alu muttar', 10], ['MTR mutter paneer', 10], ['Mixed vegetable curry', 10], ['MTR palak paneer', 10], ['MTR shahi paneer', 10], ['MTR bhindi masala', 10], ['MTR alu methi', 10], ['MTR chana masala', 10], ['MTR kadhi pakora', 10], ['GITS paneer tikka masala', 10], ['GITS bhindi masala', 10], ['GITS pau bhakti', 10], ['GITS paneer makhani', 10], ['GITS aloo raswala', 10], ['GITS veg biryani', 10], ['5 Minute khana aloo mutter', 10], ['5 Minute khana pao bhaji', 10]]

    result = form_io.read_csv(StringIO(CSV_EXAMPLE))
    
    print(result)

    if expected_result == result:
        print("\n+ + + PASS + + +")
        return True
    else:
        print("\n- - - FAIL - - -")
        return False
    

def import_example_xlsx():
    print("\n============= IMPORT EXAMPLE XLSX ===============")

    expected_result = [['Sona Masoori Rice', 13], ['Toor Dahl (Red Lentils)', 179], ['Black chickpeas (channa)', 85], ['Maggi Noodles', 400], ['PARLE KREAM BOUR', 10], ['P HID SEEK BOURB', 10], ['SW MASL BANA', 10], ['GOP SNACK PE CHO', 10], ['AD BANGA MIX', 10], ['SW BHEL CUP', 10], ['MAGIC MAS UPMA', 10], ['KURKURE MASLLAYS CHILE LIMON', 10], ['MTR navaratan korma', 10], ['MTR alu muttar', 10], ['MTR mutter paneer', 10], ['Mixed vegetable curry', 10], ['MTR palak paneer', 10], ['MTR shahi paneer', 10], ['MTR bhindi masala', 10], ['MTR alu methi', 10], ['MTR chana masala', 10], ['MTR kadhi pakora', 10], ['GITS paneer tikka masala', 10], ['GITS bhindi masala', 10], ['GITS pau bhakti', 10], ['GITS paneer makhani', 10], ['GITS aloo raswala', 10], ['GITS veg biryani', 10], ['5 Minute khana aloo mutter', 10], ['5 Minute khana pao bhaji', 10]]
    
    result = form_io.read_excel(XLSX_EXAMPLE)
    
    print(result)
    
    # To-do... verify
    if expected_result == result:
        print("\n+ + + PASS + + +")
        return True
    else:
        print("\n- - - FAIL - - -")
        return False

def export_example_csv():
    print("\n============= EXPORT EXAMPLE CSV ================")

    input_data = [['Sona Masoori Rice', 13], ['Toor Dahl (Red Lentils)', 179], ['Black chickpeas (channa)', 85], ['Maggi Noodles', 400], ['PARLE KREAM BOUR', 10], ['P HID SEEK BOURB', 10], ['SW MASL BANA', 10], ['GOP SNACK PE CHO', 10], ['AD BANGA MIX', 10], ['SW BHEL CUP', 10], ['MAGIC MAS UPMA', 10], ['KURKURE MASLLAYS CHILE LIMON', 10], ['MTR navaratan korma', 10], ['MTR alu muttar', 10], ['MTR mutter paneer', 10], ['Mixed vegetable curry', 10], ['MTR palak paneer', 10], ['MTR shahi paneer', 10], ['MTR bhindi masala', 10], ['MTR alu methi', 10], ['MTR chana masala', 10], ['MTR kadhi pakora', 10], ['GITS paneer tikka masala', 10], ['GITS bhindi masala', 10], ['GITS pau bhakti', 10], ['GITS paneer makhani', 10], ['GITS aloo raswala', 10], ['GITS veg biryani', 10], ['5 Minute khana aloo mutter', 10], ['5 Minute khana pao bhaji', 10]]
    
    form_io.write_file(CSV_EXPORT, input_data)
    
    # To-do... verify
    print(f"Please verify the {CSV_EXPORT} output file in the form_io folder.")

def export_example_xlsx():
    print("\n============= EXPORT EXAMPLE XLSX ===============")

    input_data = [['Sona Masoori Rice', 13], ['Toor Dahl (Red Lentils)', 179], ['Black chickpeas (channa)', 85], ['Maggi Noodles', 400], ['PARLE KREAM BOUR', 10], ['P HID SEEK BOURB', 10], ['SW MASL BANA', 10], ['GOP SNACK PE CHO', 10], ['AD BANGA MIX', 10], ['SW BHEL CUP', 10], ['MAGIC MAS UPMA', 10], ['KURKURE MASLLAYS CHILE LIMON', 10], ['MTR navaratan korma', 10], ['MTR alu muttar', 10], ['MTR mutter paneer', 10], ['Mixed vegetable curry', 10], ['MTR palak paneer', 10], ['MTR shahi paneer', 10], ['MTR bhindi masala', 10], ['MTR alu methi', 10], ['MTR chana masala', 10], ['MTR kadhi pakora', 10], ['GITS paneer tikka masala', 10], ['GITS bhindi masala', 10], ['GITS pau bhakti', 10], ['GITS paneer makhani', 10], ['GITS aloo raswala', 10], ['GITS veg biryani', 10], ['5 Minute khana aloo mutter', 10], ['5 Minute khana pao bhaji', 10]]
    
    form_io.write_file(XLSX_EXPORT, input_data)

    # To-do... verify
    print(f"Please verify the {XLSX_EXPORT} output file in the form_io folder.")


