from tkinter import *
from tkinter import ttk


root=Tk()
root.title('نرم افزار مدیریت پرینت - مرکز فناوری اطلاعات - دانشگاه صنعتی اصفهان')
root.resizable(False,False)

mainframe=ttk.Frame(root).grid(row=0,column=0,sticky="news")

connectLF=ttk.Labelframe(mainframe,text='اتصال',width=200,height=50,labelanchor="ne")
connectLF.grid(row=0,column=1,padx=(0,5),pady=5,sticky="news")
connectLF.columnconfigure(0,weight=1)
ttk.Button(connectLF,text='اتصال').grid(row=0,column=0,sticky="news",padx=(5,0),pady=(0,5))
ttk.Label(connectLF,text=':اتصال به سرور جدید').grid(row=0,column=1,padx=5,pady=(0,5))

quotaLF=ttk.Labelframe(mainframe,text='سهمیه',width=200,height=350,labelanchor="ne")
quotaLF.grid(row=2,column=1,padx=(0,5),pady=5,sticky="news")
quotaLF.columnconfigure(2,weight=1)
ttk.Label(quotaLF,text='ریال').grid(row=0,column=0,padx=5,pady=(5,0),sticky="e")
ttk.Label(quotaLF,text='ریال').grid(row=1,column=0,padx=5,pady=(5,0),sticky="e")
ttk.Label(quotaLF,text='ریال').grid(row=2,column=0,padx=5,pady=(5,0),sticky="e")
ttk.Label(quotaLF,text='عدد').grid(row=3,column=0,padx=5,pady=(5,0),sticky="e")
ttk.Label(quotaLF,text='عدد').grid(row=4,column=0,padx=5,pady=(5,0),sticky="e")
ttk.Label(quotaLF,text='درصد').grid(row=5,column=0,padx=5,pady=(5,0),sticky="e")
ttk.Entry(quotaLF).grid(row=0,column=1,padx=5,pady=5)
ttk.Entry(quotaLF).grid(row=1,column=1,padx=5,pady=5)
ttk.Entry(quotaLF).grid(row=2,column=1,padx=5,pady=5)
ttk.Entry(quotaLF).grid(row=3,column=1,padx=5,pady=5)
ttk.Entry(quotaLF).grid(row=4,column=1,padx=5,pady=5)
ttk.Entry(quotaLF).grid(row=5,column=1,padx=5,pady=5)
ttk.Label(quotaLF,text=':اعتبار').grid(row=0,column=2,padx=5,pady=5,sticky="e")
ttk.Label(quotaLF,text=':حداکثر اعتبار مجاز').grid(row=1,column=2,padx=5,pady=5,sticky="e")
ttk.Label(quotaLF,text=':حداقل اعتبار مجاز').grid(row=2,column=2,padx=5,pady=5,sticky="e")
ttk.Label(quotaLF,text=':سهمیه ی کاغذ').grid(row=3,column=2,padx=5,pady=5,sticky="e")
ttk.Label(quotaLF,text=':حداکثر سهمیه ی کاغذ مجاز').grid(row=4,column=2,padx=5,pady=5,sticky="e")
ttk.Label(quotaLF,text=':تخفیف').grid(row=5,column=2,padx=5,pady=5,sticky="e")

addB=ttk.Button(mainframe,text='افزودن موارد انتخابی')
addB.grid(row=3,column=1,sticky="news",padx=(0,5),pady=(0,5))

treeLF=ttk.Labelframe(mainframe,text='نتیجه ی جستجو',width=400,labelanchor="ne")
treeLF.grid(row=0,column=0,rowspan=3,padx=5,pady=5,sticky="news")



root.mainloop()

