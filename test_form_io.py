from form_io import form_io

# change this to the db url & port you are using
TEST_URL = 'http://82.29.198.185:8002'
# name of the csv to read (can detect delimeters)
TEST_FILENAME = 'form_io/example.csv'

print("^ form_io functions loaded ^")
print(form_io.form_io_import(TEST_URL, TEST_FILENAME))

# launch 
