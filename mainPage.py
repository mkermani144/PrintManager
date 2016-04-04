from tkinter import *
from tkinter import ttk
from re import match
from ldap3 import *
import pypyodbc

def close(*args):
	for w in filter(lambda w: args.index(w),args):
		w.destroy()
	args[0].grab_set()
	args[0].focus()

def validateIP(ip):
	return re.match('^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$',ip.get())

def userPass(ip,w,e):
	if validateIP(ip):
		t=Toplevel(root)
		t.grab_set()
		t.title('ورود کاربر')
		ttk.Label(t,text=':نام کاربری و رمز عبور را وارد کنید').grid(row=0,column=0,columnspan=2,padx=10,pady=10)
		username=StringVar()
		password=StringVar()
		ttk.Label(t,text=':نام کاربری').grid(row=1,column=1,padx=(0,10),pady=10,sticky='e')
		ttk.Label(t,text=':رمز عبور').grid(row=2,column=1,padx=(0,10),pady=10,sticky='e')
		e1=ttk.Entry(t,width=45,textvariable=username)
		e1.grid(row=1,column=0,padx=(10,30),pady=10)
		e2=ttk.Entry(t,width=45,textvariable=password,show='\u2022') # \u2022 is bullet character
		e2.grid(row=2,column=0,padx=(10,30),pady=10)
		myButton=ttk.Button(t,text='تایید',command= lambda: connect(ip,username,password,t))
		myButton.grid(row=3,column=0,columnspan=2,padx=10,pady=10,sticky='n')
		myButton.bind('<Return>',lambda ev: connect(ip,username,password,t))
		e1.focus()
	else:
		t=Toplevel(w)
		t.grab_set()
		t.title('خطا')
		t.columnconfigure(0,minsize='150')
		t.columnconfigure(1,minsize='150')
		ttk.Label(t,text='.آی پی وارد شده معتبر نمی باشد').grid(row=0,column=0,columnspan=2,padx=50,pady=20)
		b=ttk.Button(t,text='تلاش مجدد',command= lambda: [close(w,t),e.delete(0,'end'),e.focus()])
		b.grid(row=1,column=0,padx=10,pady=(10,10),sticky='e')
		b.bind('<Return>',lambda ev: [close(w,t),e.delete(0,'end')])
		b2=ttk.Button(t,text='لغو',command= lambda: close(root,t))
		b2.grid(row=1,column=1,padx=10,pady=(10,10),sticky='w')
		b2.bind('<Return>',lambda ev: close(root,t))
		b.focus()

def connect(ip,username,password,w):
	w.destroy()
	server=Server(ip.get()) # use_ssl=False
	print(ip.get())
	connection=Connection(server,username.get(),password.get(),read_only=True)
	connection.bind()
	tree.insert('',0,text='salon.iut',iid='DC=salon,DC=iut',tags='white')
	connection.search(search_base='dc=salon,dc=iut',
		search_filter='(objectClass=organizationalUnit)',
		search_scope=SUBTREE,
		attributes=['dn'])
	connection.entries.reverse()
	for entry in connection.entries:
		dn=entry.entry_get_dn()
		tree.insert(dn[dn.find(',')+1:],0,text=dn[dn.find('=')+1:dn.find(',')],iid=dn,tags='white')

	connection.search(search_base='dc=salon,dc=iut',
		search_filter='(objectClass=user)',
		search_scope=SUBTREE,
		attributes=['cn','sn','studentNumber','dn'])
	for entry in connection.entries:
		dn=entry.entry_get_dn()
		try:
			tree.insert(dn[dn.find(',')+1:],0,text=entry['cn'],iid=dn,tags='white')
		except:
			pass

		# t=Toplevel(root)
		# t.grab_set()
		# t.title('خطا')
		# t.columnconfigure(0,minsize='150')
		# ttk.Label(t,text='.امکان برقراری ارتباط با سرور وجود ندارد').grid(row=0,column=0,padx=50,pady=20)
		# myButton=ttk.Button(t,text='بازگشت',command= lambda: close(root,t))
		# myButton.grid(row=1,column=0,padx=10,pady=(10,10))
		# myButton.bind('<Return>',lambda ev: close(root,t))

def setDefaultIP(configurations,w):
	def setDefaultIPInner():
		if validateIP(ip):
			configurations[0]=ip.get()
			updateConf(configurations)
			t1=Toplevel(root)
			t1.grab_set()
			t1.title('عملیات موفقیت آمیز')
			t1.columnconfigure(0,minsize='150')
			ttk.Label(t1,text='.آی پی سرور پیش فرض با موفقیت تغییر یافت').grid(row=0,column=0,padx=50,pady=20)
			b=ttk.Button(t1,text='تایید',command= lambda: close(root,t1))
			b.grid(row=1,column=0,padx=10,pady=(10,10))
			b.bind('<Return>',lambda ev: close(root,t1))
			b.focus()
			close(t1,t)
		else:
			t1=Toplevel(t)
			t1.grab_set()
			t1.title('خطا')
			t1.columnconfigure(0,minsize='150')
			t1.columnconfigure(1,minsize='150')
			ttk.Label(t1,text='.آی پی وارد شده معتبر نمی باشد').grid(row=0,column=0,columnspan=2,padx=50,pady=20)
			b=ttk.Button(t1,text='تلاش مجدد',command= lambda: [close(t,t1),e.delete(0,'end'),e.focus()])
			b.grid(row=1,column=0,padx=10,pady=(10,10),sticky='e')
			b.bind('<Return>',lambda ev: [close(t,t1),e.delete(0,'end'),e.focus()])
			b2=ttk.Button(t1,text='لغو',command= lambda: close(root,t1,t))
			b2.grid(row=1,column=1,padx=10,pady=(10,10),sticky='w')
			b2.bind('<Return>',lambda ev: close(root,t1,t))
			b.focus()
	close(root,w)
	t=Toplevel(root)
	t.grab_set() # Make parent disabled
	t.title('ورود آی پی سرور پیش فرض')
	ttk.Label(t,text=':لطفا آی پی سرور پیش فرض را وارد کنید').grid(row=0,column=0,columnspan=2,padx=10,pady=10)
	ip=StringVar()
	e=ttk.Entry(t,width=45,textvariable=ip)
	e.grid(row=1,column=0,columnspan=2,padx=30,pady=10)
	e.focus()
	b=ttk.Button(t,text='تایید',command= setDefaultIPInner)
	b.grid(row=2,column=0,padx=10,pady=10,sticky='e')
	b.bind('<Return>',setDefaultIPInner(e))
	b2=ttk.Button(t,text='لغو',command= lambda: close(root,t))
	b2.grid(row=2,column=1,padx=10,pady=10,sticky='w')
	b2.bind('<Return>',lambda ev: close(root,t))

def toggleEntry(rbv,entry,ip):
	if rbv.get()=='new':
		entry.config(state='enabled')
		ip.set('')
	else:
		entry.config(state='disabled')
		with open('conf') as f:
			ip.set(f.readlines()[0].rstrip())

def updateConf(configurations):
	with open('conf','w') as f:
		for item in configurations:
			f.write(item+'\n')

def toggleColor(flag,l):
	def toggleFatherColor(entry):
		p=tree.parent(entry)
		if p:
			tree.item(p,tags=[w.replace(state[0],'yellow') for w in tree.item(p)['tags']])
			l=[tree.item(x)['tags'] for x in tree.get_children(p)]
			if(flag==1):
				for child in l:
					if 'yellow' in child or 'white' in child:
						break;
				else:
					tree.item(p,tags=[w.replace('yellow','green') for w in tree.item(p)['tags']])
			else:
				for child in l:
					if 'yellow' in child or 'green' in child:
						break;
				else:
					tree.item(p,tags=[w.replace('yellow','white') for w in tree.item(p)['tags']])
			toggleFatherColor(tree.parent(entry))
	def toggleChildColor(entry):
		for e in tree.get_children(entry):
			tree.item(e,tags=[w.replace(state[0],state[1]) for w in tree.item(e)['tags']])
			tree.item(e,tags=[w.replace('yellow',state[1]) for w in tree.item(e)['tags']])
			toggleChildColor(e)

	state=('white','green') if flag==1 else ('green','white')
	for entry in l:
		tree.item(entry,tags=[w.replace(state[0],state[1]) for w in tree.item(entry)['tags']])
		tree.item(entry,tags=[w.replace('yellow',state[1]) for w in tree.item(entry)['tags']])
		toggleFatherColor(entry)
		toggleChildColor(entry)

	tree.selection_set(tuple())

def addToDB(e):
	MDB = 'db.mdb'
	DRV = '{Microsoft Access Driver (*.mdb)}'
	# PWD = 'mypassword'
	connection = pyodbc.connect('DRIVER={};DBQ={}'.format(DRV,MDB))
	cursor=connection.cursor()
	selectionIIDs=tree.tag_has('green')
	for item in selectionIIDs:
		SQ='''
		IF NOT EXISTS(SELECT * from db WHERE firstName=%s AND lastName=%s AND studentNumber=%s)
		 BEGIN
		  INSERT INTO db VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
		 END
		''' % (item['cn'], item['sn'], item['studentNumber'],item['cn'], item['sn'], item['studentNumber']),
		credit.get(),maxCredit.get(),minCredit.get(),sheetCredit.get(),sheetMax.get(),discount.get()
		cursor.execute(SQ)
	cursor.close()
	connection.close()


root=Tk()
root.title('نرم افزار مدیریت پرینت - مرکز فناوری اطلاعات - دانشگاه صنعتی اصفهان')
root.resizable(False,False)

mainframe=ttk.Frame(root).grid(row=0,column=0,sticky='news')

connectLF=ttk.Labelframe(mainframe,text='اتصال',width=200,height=50,labelanchor='ne')
connectLF.grid(row=0,column=1,padx=(0,5),pady=5,sticky='news')
connectLF.columnconfigure(0,weight=1)
ttk.Label(connectLF,text=':نوع اتصال به سرور').grid(row=0,column=0,columnspan=2,padx=5,pady=(0,5),sticky='e')
v=StringVar()
v.set('default')
ip=StringVar()
ttk.Radiobutton(connectLF,variable=v,value='new',command= lambda: toggleEntry(v,e,ip)).grid(row=1,column=1,sticky='e')
ttk.Radiobutton(connectLF,variable=v,value='default',command= lambda: toggleEntry(v,e,ip)).grid(row=2,column=1,sticky='e')
ttk.Label(connectLF,text='اتصال به سرور جدید').grid(row=1,padx=5,pady=(0,5),sticky='e')
ttk.Label(connectLF,text='اتصال به سرور پیش فرض').grid(row=2,padx=5,pady=(0,5),sticky='e')
e=ttk.Entry(connectLF,textvariable=ip)
e.grid(row=3,sticky='we',padx=(5,50),pady=5)
toggleEntry(v,e,ip)
ttk.Label(connectLF,text=':آی پی سرور').grid(row=3,column=0,columnspan=2,padx=5,pady=(0,5),sticky='e')
b=ttk.Button(connectLF,text='اتصال',command= lambda: userPass(ip,root,e) )
b.grid(row=4,column=0,columnspan=2,sticky='news',padx=5,pady=5)
b.bind('<Return>',lambda ev: userPass(ip,root,e))

quotaLF=ttk.Labelframe(mainframe,text='سهمیه',width=200,height=350,labelanchor='ne')
quotaLF.grid(row=2,column=1,padx=(0,5),pady=5,sticky='news')
quotaLF.columnconfigure(2,weight=1)
credit=StringVar()
maxCredit=StringVar()
minCredit=StringVar()
sheetCredit=StringVar()
sheetMax=StringVar()
discount=StringVar()
ttk.Label(quotaLF,text='ریال').grid(row=0,column=0,padx=5,pady=5,sticky='e')
ttk.Label(quotaLF,text='ریال').grid(row=1,column=0,padx=5,pady=5,sticky='e')
ttk.Label(quotaLF,text='ریال').grid(row=2,column=0,padx=5,pady=5,sticky='e')
ttk.Label(quotaLF,text='برگ').grid(row=3,column=0,padx=5,pady=5,sticky='e')
ttk.Label(quotaLF,text='برگ').grid(row=4,column=0,padx=5,pady=5,sticky='e')
ttk.Label(quotaLF,text='درصد').grid(row=5,column=0,padx=5,pady=(5,10),sticky='e')
ttk.Entry(quotaLF,textvariable=credit).grid(row=0,column=1,padx=5,pady=5)
ttk.Entry(quotaLF,textvariable=maxCredit).grid(row=1,column=1,padx=5,pady=5)
ttk.Entry(quotaLF,textvariable=minCredit).grid(row=2,column=1,padx=5,pady=5)
ttk.Entry(quotaLF,textvariable=sheetCredit).grid(row=3,column=1,padx=5,pady=5)
ttk.Entry(quotaLF,textvariable=sheetMax).grid(row=4,column=1,padx=5,pady=5)
ttk.Entry(quotaLF,textvariable=discount).grid(row=5,column=1,padx=5,pady=(5,10))
ttk.Label(quotaLF,text=':اعتبار').grid(row=0,column=2,padx=5,pady=5,sticky='e')
ttk.Label(quotaLF,text=':حداکثر اعتبار مجاز').grid(row=1,column=2,padx=5,pady=5,sticky='e')
ttk.Label(quotaLF,text=':حداقل اعتبار مجاز').grid(row=2,column=2,padx=5,pady=5,sticky='e')
ttk.Label(quotaLF,text=':سهمیه ی کاغذ').grid(row=3,column=2,padx=5,pady=5,sticky='e')
ttk.Label(quotaLF,text=':حداکثر سهمیه ی کاغذ مجاز').grid(row=4,column=2,padx=5,pady=5,sticky='e')
ttk.Label(quotaLF,text=':تخفیف').grid(row=5,column=2,padx=5,pady=(5,10),sticky='e')

treeLF=ttk.Labelframe(mainframe,text='نتیجه ی جستجو',labelanchor='ne')
treeLF.grid(row=0,column=0,rowspan=3,padx=5,pady=5,sticky='news')
treeLF.rowconfigure(0,weight=1)
tree=ttk.Treeview(treeLF)
tree.grid(row=0,column=0,columnspan=2,pady=(5,0),sticky='nws')
s=ttk.Scrollbar(treeLF,orient=VERTICAL,command=tree.yview)
s.grid(row=0,column=2,pady=(5,0),sticky='ns')
tree.configure(yscrollcommand=s.set)
tree.tag_configure('green',background='green')
tree.tag_configure('white',background='white')
tree.tag_configure('yellow',background='yellow')
b=ttk.Button(treeLF,text='انتخاب',command= lambda: toggleColor(1,tree.selection()))
b.grid(row=1,column=0,sticky='news',padx=5,pady=5)
b.bind('<Return>',lambda ev: toggleColor(1))
b2=ttk.Button(treeLF,text='لغو انتخاب',command= lambda: toggleColor(0,tree.selection()))
b2.grid(row=1,column=1,sticky='news',padx=5,pady=5)
b2.bind('<Return>',lambda ev: toggleColor(0))

# tree.insert('', 'end', text='button', tags=('white', 'simple'))
# tree.insert('', 'end', text='button2', tags=( 'white','simple'))
# tree.insert('', 'end', text='but5ton', tags=('white', 'simple'))
# tree.insert('', 'end', text='button3', tags=( 'white','simple'))
# tree.insert('', 'end', text='butt546on', tags=('white', 'simple'))
# tree.insert('', 'end', text='but456345ton', tags=( 'white','simple'))
# tree.insert('', 'end', text='but34534534534ton', tags=('white', 'simple'))
# tree.insert('', 'end', text='but345345345345345345ton', tags=( 'white','simple'))

addB=ttk.Button(mainframe,text='افزودن موارد انتخابی',command=addToDB)
addB.grid(row=3,column=1,sticky='news',padx=(0,5),pady=(0,5))
addB.bind('<Return>',addToDB)

with open('conf') as f:
	configurations=f.readlines()
	configurations[0]=configurations[0].strip()
	configurations[1]=configurations[1].strip()
	if(configurations[1]=='1'):
		configurations[1]='0'
		updateConf(configurations)
		pypyodbc.win_create_mdb('database.mdb')
		conn=pypyodbc.win_connect_mdb('database.mdb')
		cur=conn.cursor()
		query='''
			CREATE TABLE credits
			(
				first_name VARCHAR(30),
				last_name VARCHAR(30),
				entrance_year INTEGER,
				student_number INTEGER,
				grade VARCHAR(3),
				department VARCHAR(15),
				field VARCHAR(15),
				credit INTEGER,
				max_credit INTEGER,
				min_credit INTEGER,
				paper_credit INTEGER,
				paper_max_credit INTEGER,
				discount VARCHAR(3)
			)
		'''
		cur.execute(query)
		cur.close()
		conn.commit()
		conn.close()
		t=Toplevel(root)
		t.grab_set()
		t.focus()
		t.title('تغییر آی پی سرور پیش فرض')
		ttk.Label(t,text='آی پی سرور پیش فرض 127.0.0.1 تنظیم شده است. آیا می خواهید آن را تغییر دهید؟').grid(row=0,column=0,columnspan=2,padx=10,pady=10)
		y=ttk.Button(t,text='بله',command= lambda: setDefaultIP(configurations,t))
		y.grid(row=2,column=0,padx=10,pady=10,sticky='e')
		y.bind('<Return>',lambda ev: setDefaultIP(configurations,t))
		n=ttk.Button(t,text='خیر',command= lambda: close(root,t))
		n.grid(row=2,column=1,padx=10,pady=10,sticky='w')
		n.bind('<Return>',lambda ev: close(root,t))


root.mainloop()
