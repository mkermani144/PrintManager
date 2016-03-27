from tkinter import *
from tkinter import ttk


root=Tk()
root.title('نرم افزار مدیریت پرینت - مرکز فناوری اطلاعات - دانشگاه صنعتی اصفهان')
root.resizable(False,False)

mainframe=ttk.Frame(root).grid(row=0,column=0,sticky=(N,E,W,S))

connectLF=ttk.Labelframe(mainframe,text='اتصال',width=200,height=50,labelanchor=NE)
connectLF.grid(row=0,column=1,padx=(0,5),pady=5,sticky=(N,E,W,S))

quotaLF=ttk.Labelframe(mainframe,text='سهمیه',width=200,height=350,labelanchor=NE)
quotaLF.grid(row=2,column=1,padx=(0,5),pady=5,sticky=(N,E,W,S))

addB=ttk.Button(mainframe,text='افزودن موارد انتخابی')
addB.grid(row=3,column=1,sticky=(N,E,W,S),padx=(0,5),pady=(0,5))

treeLF=ttk.Labelframe(mainframe,text='نتیجه ی جستجو',width=400,labelanchor=NE)
treeLF.grid(row=0,column=0,rowspan=3,padx=5,pady=5,sticky=(N,E,W,S))



root.mainloop()

