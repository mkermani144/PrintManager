from tkinter import *
from tkinter import ttk
from re import match

def close(*args):
	for w in filter(lambda w: args.index(w),args):
		w.destroy()
	args[0].focus()

def validateIP(ip):
	return re.match('^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$',ip.get())

def userPass(ip,w,e):
	if validateIP(ip):
		t=Toplevel(root)
		t.grab_set()
		t.title("ورود کاربر")
		ttk.Label(t,text=':نام کاربری و رمز عبور را وارد کنید').grid(row=0,column=0,columnspan=2,padx=10,pady=10)
		username=StringVar()
		password=StringVar()
		ttk.Label(t,text=':نام کاربری').grid(row=1,column=1,padx=(0,10),pady=10,sticky="e")
		ttk.Label(t,text=':رمز عبور').grid(row=2,column=1,padx=(0,10),pady=10,sticky="e")
		e1=ttk.Entry(t,width=45,textvariable=username)
		e1.grid(row=1,column=0,padx=(10,30),pady=10)
		e2=ttk.Entry(t,width=45,textvariable=password,show="\u2022") # \u2022 is bullet character
		e2.grid(row=2,column=0,padx=(10,30),pady=10)
		ttk.Button(t,text='تایید').grid(row=3,column=0,columnspan=2,padx=10,pady=10,sticky="n")
		e1.focus()
	else:
		t=Toplevel(w)
		t.grab_set()
		t.title("خطا")
		t.columnconfigure(0,minsize="150")
		t.columnconfigure(1,minsize="150")
		ttk.Label(t,text='.آی پی وارد شده معتبر نمی باشد').grid(row=0,column=0,columnspan=2,padx=50,pady=20)
		b=ttk.Button(t,text='تلاش مجدد',command= lambda: [close(w,t),e.delete(0,'end'),e.focus()])
		b.grid(row=1,column=0,padx=10,pady=(10,10),sticky="e")
		ttk.Button(t,text='لغو',command= lambda: close(root,t)).grid(row=1,column=1,padx=10,pady=(10,10),sticky="w")
		b.focus()

def setDefaultIP():
	t=Toplevel(root)
	t.grab_set() # Make parent disabled
	t.title("ورود آی پی")
	ttk.Label(t,text=':لطفا آی پی سرور را وارد کنید').grid(row=0,column=0,columnspan=2,padx=10,pady=10)
	ip=StringVar()
	e=ttk.Entry(t,width=45,textvariable=ip)
	e.grid(row=1,column=0,columnspan=2,padx=30,pady=10)
	e.focus()
	ttk.Button(t,text='تایید',command= lambda: validateIP(ip,t,e)).grid(row=2,column=0,padx=10,pady=10,sticky="e")
	ttk.Button(t,text='لغو',command= lambda: close(root,t)).grid(row=2,column=1,padx=10,pady=10,sticky="w")

def enableEntry(rbv,entry,ip):
	if rbv.get()=='new':
		entry.config(state='enabled')
		ip.set('')
	else:
		entry.config(state='disabled')
		ip.set('127.0.0.1')

root=Tk()
root.title('نرم افزار مدیریت پرینت - مرکز فناوری اطلاعات - دانشگاه صنعتی اصفهان')
root.resizable(False,False)

mainframe=ttk.Frame(root).grid(row=0,column=0,sticky="news")

connectLF=ttk.Labelframe(mainframe,text='اتصال',width=200,height=50,labelanchor="ne")
connectLF.grid(row=0,column=1,padx=(0,5),pady=5,sticky="news")
connectLF.columnconfigure(0,weight=1)
ttk.Label(connectLF,text=':نوع اتصال به سرور').grid(row=0,column=0,columnspan=2,padx=5,pady=(0,5),sticky="e")
v=StringVar()
ip=StringVar()
ttk.Radiobutton(connectLF,variable=v,value='new',command= lambda: enableEntry(v,e,ip)).grid(row=1,column=1,sticky="e")
ttk.Radiobutton(connectLF,variable=v,value='default',command= lambda: enableEntry(v,e,ip)).grid(row=2,column=1,sticky="e")
ttk.Label(connectLF,text='اتصال به سرور جدید').grid(row=1,padx=5,pady=(0,5),sticky="e")
ttk.Label(connectLF,text='اتصال به سرور پیش فرض').grid(row=2,padx=5,pady=(0,5),sticky="e")
e=ttk.Entry(connectLF,textvariable=ip)
e.grid(row=3,sticky="we",padx=(5,50),pady=5)
ttk.Label(connectLF,text=':آی پی سرور').grid(row=3,column=0,columnspan=2,padx=5,pady=(0,5),sticky="e")
ttk.Button(connectLF,text='اتصال',command= lambda: userPass(ip,root,e) ).grid(row=4,column=0,columnspan=2,sticky="news",padx=5,pady=5)

quotaLF=ttk.Labelframe(mainframe,text='سهمیه',width=200,height=350,labelanchor="ne")
quotaLF.grid(row=2,column=1,padx=(0,5),pady=5,sticky="news")
quotaLF.columnconfigure(2,weight=1)
ttk.Label(quotaLF,text='ریال').grid(row=0,column=0,padx=5,pady=5,sticky="e")
ttk.Label(quotaLF,text='ریال').grid(row=1,column=0,padx=5,pady=5,sticky="e")
ttk.Label(quotaLF,text='ریال').grid(row=2,column=0,padx=5,pady=5,sticky="e")
ttk.Label(quotaLF,text='عدد').grid(row=3,column=0,padx=5,pady=5,sticky="e")
ttk.Label(quotaLF,text='عدد').grid(row=4,column=0,padx=5,pady=5,sticky="e")
ttk.Label(quotaLF,text='درصد').grid(row=5,column=0,padx=5,pady=(5,10),sticky="e")
ttk.Entry(quotaLF).grid(row=0,column=1,padx=5,pady=5)
ttk.Entry(quotaLF).grid(row=1,column=1,padx=5,pady=5)
ttk.Entry(quotaLF).grid(row=2,column=1,padx=5,pady=5)
ttk.Entry(quotaLF).grid(row=3,column=1,padx=5,pady=5)
ttk.Entry(quotaLF).grid(row=4,column=1,padx=5,pady=5)
ttk.Entry(quotaLF).grid(row=5,column=1,padx=5,pady=(5,10))
ttk.Label(quotaLF,text=':اعتبار').grid(row=0,column=2,padx=5,pady=5,sticky="e")
ttk.Label(quotaLF,text=':حداکثر اعتبار مجاز').grid(row=1,column=2,padx=5,pady=5,sticky="e")
ttk.Label(quotaLF,text=':حداقل اعتبار مجاز').grid(row=2,column=2,padx=5,pady=5,sticky="e")
ttk.Label(quotaLF,text=':سهمیه ی کاغذ').grid(row=3,column=2,padx=5,pady=5,sticky="e")
ttk.Label(quotaLF,text=':حداکثر سهمیه ی کاغذ مجاز').grid(row=4,column=2,padx=5,pady=5,sticky="e")
ttk.Label(quotaLF,text=':تخفیف').grid(row=5,column=2,padx=5,pady=(5,10),sticky="e")

treeLF=ttk.Labelframe(mainframe,text='نتیجه ی جستجو',labelanchor="ne")
treeLF.grid(row=0,column=0,rowspan=3,padx=5,pady=5,sticky="news")
treeLF.rowconfigure(0,weight=1)
tree=ttk.Treeview(treeLF,)
tree.grid(row=0,column=0,pady=(5,0),sticky="news")
s=ttk.Scrollbar(treeLF,orient=VERTICAL,command=tree.yview)
s.grid(row=0,column=1,pady=(5,0),sticky="ns")
tree.configure(yscrollcommand=s.set)
# tree.heading('#0', text='Name',anchor="w")
# tree.insert('',0,'mother',text='hello',open=True)
# tree.insert('mother',2,text='hello2')
# tree.insert('mother',1,text='hello3')

ttk.Button(mainframe,text='افزودن موارد انتخابی').grid(row=3,column=1,sticky="news",padx=(0,5),pady=(0,5))



root.mainloop()
