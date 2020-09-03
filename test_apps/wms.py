import pyodbc 
server = ',' 
database = '' 
username = '' 
password = '' 
cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
cursor = cnxn.cursor()

product = 'T0000092239'
cursor.execute(f"SELECT * from v_wms_binlocat_din_attr where product = '{product}';") 
row = cursor.fetchone() 
while row: 
    print(row[2])
    print(row[3])
    print(row[5])
    print(row[6])
    print(row[8])
    row = cursor.fetchone()