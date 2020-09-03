# -*- coding:utf -8 -*-
# !/usr/bin/python3
from tkinter import *
import random
import webbrowser
import pyodbc 
from decimal import Decimal

root = Tk()
#root.iconbitmap('p_gen.ico')
root.resizable(width=True, height=True)
root.title("WMS")
root.geometry("750x338+300+300")
calculated_text = Text(root, height=15, width=90)


def erase():
    calculated_text.delete('1.0', END)


chars = '+-/*!&$#?=@<>abcdefghijklnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'

def info():
    return webbrowser.open('https://coderlog.top/')

def binlocat():
    server = ',' 
    database = '' 
    username = '' 
    db_password = '' 
    cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ db_password)
    cursor = cnxn.cursor()

    product = str(number_entry.get())
    cursor.execute(f"SELECT * from v_wms_binlocat_din_attr where product = '{product}';") 
    #cursor.execute("SELECT col(binlocat_id);") 
    row = cursor.fetchone() 
    while row: 
        label = str(row[2]+' | '+row[4]+' | '+row[6]+' | ')
        qty = str(row[5])
        calculated_text.insert(END, label + qty + "\n")
        row = cursor.fetchone()

binlocate_button = Button(text="Товарный запас", command=binlocat)
erase_button = Button(text="Очистить", command=erase)
info_button = Button(text="Информация", command=info)
text_label = Label(text="", fg="#003363", bg="#99adc0")
number_entry = Entry(width=10, justify=CENTER)
number_entry.insert(0, "")
number_label = Label(text="      Код товара")
number_label.grid(row=0, column=0, sticky="w")
number_entry.grid(row=0,column=1, padx=1, pady=10)

binlocate_button.grid(row=2, column=1, padx=5, pady=5, sticky="e")
erase_button.grid(row=2, column=2, padx=7, pady=5, sticky="w")
info_button.grid(row=2, column=0, padx=12, pady=5, sticky="w")
text_label.place(x=0,y=320)
calculated_text.grid(row=4, column=0, sticky='nsew', columnspan=3)

scrollb = Scrollbar(root, command=calculated_text.yview)
scrollb.grid(row=4, column=4, sticky='nsew')
calculated_text.configure(yscrollcommand=scrollb.set)

root.mainloop()