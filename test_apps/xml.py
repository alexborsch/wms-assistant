import tkinter
from tkinter import *
from tkinter.filedialog import asksaveasfile, askopenfile
from tkinter.messagebox import showerror
from tkinter import messagebox
import pyodbc 
from decimal import Decimal

FILE_NAME = tkinter.NONE

def new_file():
	global FILE_NAME
	FILE_NAME = "Untitled"
	text.delete('1.0', tkinter.END)

def save_file():
	data = text.get('1.0', tkinter.END)
	out = open(FILE_NAME, 'w')
	out.write(data)
	out.close()

def save_as():
	out = asksaveasfile(mode='w', defaultextension='txt')
	data = text.get('1.0', tkinter.END)
	try:
		out.write(data.rstrip())
	except Exception:
		showerror(title="Error", message="Saving file error")

def open_file():
	global FILE_NAME
	inp = askopenfile(mode="r")
	if inp is None:
		return
	FILE_NAME = inp.name
	data = inp.read()
	text.delete('1.0', tkinter.END)
	text.insert('1.0', data)

def info():
	messagebox.showinfo("Information", "CDL Notepad v.0.1\nby CoderLog\nhttps://coderlog.top")


root = tkinter.Tk()
root.title("WMS v.0.1")

root.minsize(width=800, height=500)
root.maxsize(width=800, height=500)

'''
Подключение к серверу, вывод остатков из БД

'''
server = ',' 
database = '' 
username = '' 
password = '' 
cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
cursor = cnxn.cursor()

cursor.execute("SELECT TOP 10 * from v_wms_binlocat_din_attr;") 
row = cursor.fetchone() 
while row: 
    #print(row[1])
    '''
    product = tkinter.Label(root, text=row[2])
    name = tkinter.Label(root, text=row[3])
    p_type = tkinter.Label(root, text=row[5])
    qty = tkinter.Label(root, text=row[4])
    qty_u = tkinter.Label(root, text=row[6])

    product.pack()
    name.pack()
    p_type.pack()
    qty.pack()
    qty_u.pack()
    '''
    label = str(row[2]+' | '+row[4]+' | '+row[6])
    qty = Decimal(row[5])
    product = tkinter.Label(root, text=label)
    qty = tkinter.Label(root, text=qty)

    product.pack()
    qty.pack()
    row = cursor.fetchone()



menuBar = tkinter.Menu(root)
fileMenu = tkinter.Menu(menuBar)
fileMenu.add_command(label="New", command=new_file)
fileMenu.add_command(label="Open", command=open_file)
fileMenu.add_command(label="Save", command=save_file)
fileMenu.add_command(label="Save as", command=save_as)

menuBar.add_cascade(label="File", menu=fileMenu)
menuBar.add_cascade(label="Info", command=info)
menuBar.add_cascade(label="Exit", command=root.quit)
root.config(menu=menuBar)
root.mainloop()