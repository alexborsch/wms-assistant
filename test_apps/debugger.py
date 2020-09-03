import tkinter
from tkinter import *
from tkinter import messagebox
import json
import os


with open('settings.json') as f:
    file_content = f.read()
    data = json.loads(file_content)

log_dir = data['log_dir']
debug_file = data['debug_file']

def info():
	messagebox.showinfo("Information", "CDL Debugger v.0.1")

root = tkinter.Tk()
root.title("CDL Debugger v.0.1")

root.minsize(width=1000, height=500)
root.maxsize(width=1000, height=500)

text = tkinter.Text(root, width=400, height=400, wrap="word")
scrollb = Scrollbar(root, orient=VERTICAL, command=text.yview)
scrollb.pack(side="right", fill="y")
text.configure(yscrollcommand=scrollb.set)
text.tag_configure("WARNING", foreground="red")
text.pack()

if os.path.exists(log_dir+'/'+debug_file):
    data = open (log_dir+'/'+debug_file, 'r', encoding='utf-8')
    text.delete('1.0', tkinter.END)
    text.insert('1.0', data.read())
    
else:
    text.delete('1.0', tkinter.END)
    text.insert('1.0', 'Debug File not found')


menuBar = tkinter.Menu(root)
fileMenu = tkinter.Menu(menuBar)

menuBar.add_cascade(label="Checking for errors")
menuBar.add_cascade(label="Setting up services")
menuBar.add_cascade(label="Checking for updates")
menuBar.add_cascade(label="Log upload")
menuBar.add_cascade(label="Info", command=info)
menuBar.add_cascade(label="Exit", command=root.quit)
root.config(menu=menuBar)
root.mainloop()