from tkinter import *
from tkinter import ttk
def openGetIP(root):
	t=Toplevel(root)
	t.title("ورود آی پی")
	ttk.Label(t,text=':لطفا آی پی سرور را وارد کنید').grid(row=0,column=0,padx=10,pady=10)
	ttk.Entry(t,width=50).grid(row=1,column=0,padx=10,pady=10)
	ttk.Button(t,text='تایید').grid(row=2,column=0,padx=10,pady=10)


