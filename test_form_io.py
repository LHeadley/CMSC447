from form_io import form_io

# change this to the db url & port you are using
TEST_URL = 'http://82.29.198.185:8002'
# name of the csv to read (can detect delimeters)
TEST_FILENAME = 'form_io/example.csv'
TEST_EXPORTNAME = 'form_io/export.csv'

print("^ form_io functions loaded ^")
#print(form_io.db_import(TEST_URL, TEST_FILENAME))

#print( form_io.write_file(TEST_EXPORTNAME, form_io.read_file(TEST_FILENAME)) )

form_io.db_export(url=TEST_URL, filename=TEST_EXPORTNAME)

# launch 
