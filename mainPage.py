from tkinter import *
from tkinter import ttk
from re import match
from ldap3 import *
import pypyodbc
import time


'''
++++++++++++++++++++++++++++++++++++++++++

Function to destroy widgets passed to it
excluding the first one

>>> *args : All of the widgets to be
			destroyed and the widget to be
			kept.

++++++++++++++++++++++++++++++++++++++++++
'''
def close(*args):
	for w in filter(lambda w: args.index(w),args):
		w.destroy()
	args[0].grab_set()
	args[0].focus()


'''
++++++++++++++++++++++++++++++++++++++++++

Function to see if the IP is valid

>>> ip : The IP to be validated.

++++++++++++++++++++++++++++++++++++++++++
'''
def validateIP(ip):
	return re.match('^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$',ip.get())


'''
++++++++++++++++++++++++++++++++++++++++++

Function to connect to the LDAP server and
to make the result tree

>>> ip : The IP of the LDAP server.
>>> e : Entry of above IP.

++++++++++++++++++++++++++++++++++++++++++
'''
def connect(ip,e):
	if validateIP(ip):
		server=Server(ip.get(),use_ssl=True,connect_timeout=.5)
		username='cn=administrator,cn=users,dc=salon,dc=iut'
		password='Server2014'
		connection=Connection(server,username,password,read_only=True)
		try:
			connection.bind()
			tree.insert('',0,text='salon.iut',iid='DC=salon,DC=iut',tags='white')
			connection.search(search_base='dc=salon,dc=iut',
				search_filter='(objectClass=organizationalUnit)',
				search_scope=SUBTREE,)
			connection.entries.sort()
			i=0
			for entry in connection.entries:
				dn=entry.entry_get_dn()
				tree.insert(dn[dn.find(',')+1:],i,text=dn[dn.find('=')+1:dn.find(',')],iid=dn,tags='white')
				i+=1

			connection.search(search_base='dc=salon,dc=iut',
				search_filter='(objectClass=user)',
				search_scope=SUBTREE,
				attributes=['cn','sn','studentNumber'])
			connection.entries.sort()
			i=0
			for entry in connection.entries:
				dn=entry.entry_get_dn()
				try:
					tree.insert(dn[dn.find(',')+1:],i,text=entry['cn'],iid=dn,tags='white')
					i+=1
				except:
					pass
			connection.unbind()
			connectLabel.configure(text='Successfully connected to server.',foreground='green')
		except:
			t=Toplevel(root)
			t.grab_set()
			t.title('خطا')
			t.columnconfigure(0,minsize='150')
			ttk.Label(t,text='Cannot connect to server').grid(row=0,column=0,padx=50,pady=20)
			myButton=ttk.Button(t,text='Back',command= lambda: close(root,t))
			myButton.grid(row=1,column=0,padx=10,pady=(10,10))
			myButton.bind('<Return>',lambda ev: close(root,t))

	else:
		t=Toplevel(root)
		t.grab_set()
		t.title('Error')
		t.columnconfigure(0,minsize='150')
		t.columnconfigure(1,minsize='150')
		ttk.Label(t,text='IP address is not valid.').grid(row=0,column=0,columnspan=2,padx=50,pady=20)
		b=ttk.Button(t,text='Retry',command= lambda: [close(root,t),e.delete(0,'end'),e.focus()])
		b.grid(row=1,column=0,padx=10,pady=(10,10),sticky='e')
		b.bind('<Return>',lambda ev: [close(w,t),e.delete(0,'end')])
		b2=ttk.Button(t,text='Cancel',command= lambda: close(root,t))
		b2.grid(row=1,column=1,padx=10,pady=(10,10),sticky='w')
		b2.bind('<Return>',lambda ev: close(root,t))
		b.focus()


'''
++++++++++++++++++++++++++++++++++++++++++

Function to get the default IP of the
server from user and set it to the file

>>> configurations : A list containing
					 configurations of
					 the program.
>>> w : Popup widget asking the user if he
		wants to change default ip.

++++++++++++++++++++++++++++++++++++++++++
'''
def setDefaultIP(configurations,w):
	def setDefaultIPInner():
		if validateIP(ip):
			configurations[0]=ip.get()
			updateConf(configurations)
			t1=Toplevel(root)
			t1.grab_set()
			t1.title('Successful operation')
			t1.columnconfigure(0,minsize='150')
			ttk.Label(t1,text='Default server IP address changed sucessfully.').grid(row=0,column=0,padx=50,pady=20)
			b=ttk.Button(t1,text='OK',command= lambda: close(root,t1))
			b.grid(row=1,column=0,padx=10,pady=(10,10))
			b.bind('<Return>',lambda ev: close(root,t1))
			b.focus()
			close(t1,t)
		else:
			t1=Toplevel(t)
			t1.grab_set()
			t1.title('Error')
			t1.columnconfigure(0,minsize='150')
			t1.columnconfigure(1,minsize='150')
			ttk.Label(t1,text='IP address is not valid.').grid(row=0,column=0,columnspan=2,padx=50,pady=20)
			b=ttk.Button(t1,text='Retry',command= lambda: [close(t,t1),e.delete(0,'end'),e.focus()])
			b.grid(row=1,column=0,padx=10,pady=(10,10),sticky='e')
			b.bind('<Return>',lambda ev: [close(t,t1),e.delete(0,'end'),e.focus()])
			b2=ttk.Button(t1,text='Cancel',command= lambda: close(root,t1,t))
			b2.grid(row=1,column=1,padx=10,pady=(10,10),sticky='w')
			b2.bind('<Return>',lambda ev: close(root,t1,t))
			b.focus()
	close(root,w)
	t=Toplevel(root)
	t.grab_set() # Make parent disabled
	t.title('Default server ip address')
	ttk.Label(t,text='Please enter IP address for deafault server:').grid(row=0,column=0,columnspan=2,padx=10,pady=10)
	ip=StringVar()
	e=ttk.Entry(t,width=45,textvariable=ip)
	e.grid(row=1,column=0,columnspan=2,padx=30,pady=10)
	e.focus()
	b=ttk.Button(t,text='OK',command= setDefaultIPInner)
	b.grid(row=2,column=0,padx=10,pady=10,sticky='e')
	b.bind('<Return>',setDefaultIPInner(e))
	b2=ttk.Button(t,text='Cancel',command= lambda: close(root,t))
	b2.grid(row=2,column=1,padx=10,pady=10,sticky='w')
	b2.bind('<Return>',lambda ev: close(root,t))


'''
++++++++++++++++++++++++++++++++++++++++++

Function to toggle between two radio
buttons

>>> rbv : Radio button variable indicating
		  state of radio buttons.
>>> entry : Entry of the IP address.

++++++++++++++++++++++++++++++++++++++++++
'''
def toggleEntry(rbv,entry,ip):
	if rbv.get()=='new':
		entry.config(state='enabled')
		ip.set('')
	else:
		entry.config(state='disabled')
		with open('conf') as f:
			ip.set(f.readlines()[0].rstrip())


'''
++++++++++++++++++++++++++++++++++++++++++

Function to update the conf file

>>> configuration : List contaning
					configurations of the
					program.

++++++++++++++++++++++++++++++++++++++++++
'''
def updateConf(configurations):
	with open('conf','w') as f:
		for item in configurations:
			f.write(item+'\n')


'''
++++++++++++++++++++++++++++++++++++++++++

Function to toggle color of result tree
entries when they are selected/deselected

>>> flag : Flag indicating if the entry
		   should be disabled/enabled.
>>> l : List containing all of result tree
		entries whose colors should be
		toggled

++++++++++++++++++++++++++++++++++++++++++
'''
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


'''
++++++++++++++++++++++++++++++++++++++++++

Function to add selected result tree
entries to the database

>>> e : Event object.

++++++++++++++++++++++++++++++++++++++++++
'''
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


'''
==========================================

Main Window

==========================================
'''
root=Tk()
root.title('Print manager software - Isfahan university of technology IT center')
root.resizable(False,False)


'''
==========================================

Notebook

==========================================
'''
nb=ttk.Notebook(root)
nb.grid(row=0,column=0)


'''
==========================================

Tab to be used for adding new entries

==========================================
'''
addNewFrame=ttk.Frame(nb)
addNewFrame.grid(row=0,column=1)


'''
------------------------------------------

Connect section

------------------------------------------
'''
connectLF=ttk.Labelframe(addNewFrame,text='Connect',width=200,height=50)
connectLF.grid(row=0,column=1,padx=(0,5),pady=5,sticky='news')
connectLF.columnconfigure(0,weight=1)
ttk.Label(connectLF,text='Connection type:').grid(row=0,column=0,padx=5,pady=(0,5),sticky='w')
v=StringVar()
v.set('default')
ip=StringVar()
ttk.Radiobutton(connectLF,text='Connect to new server',variable=v,value='new',command= lambda: toggleEntry(v,e,ip)).grid(row=1,column=0,sticky='w',padx=5)
ttk.Radiobutton(connectLF,text='Connect to default server',variable=v,value='default',command= lambda: toggleEntry(v,e,ip)).grid(row=2,column=0,sticky='w',padx=5)
ttk.Label(connectLF,text='IP address:').grid(row=3,column=0,padx=5,pady=5,sticky='w')
e=ttk.Entry(connectLF,textvariable=ip)
e.grid(row=3,column=0,columnspan=2,sticky='we',padx=(75,5),pady=5)
toggleEntry(v,e,ip)
b=ttk.Button(connectLF,text='Connect',command= lambda: connect(ip,e) )
b.grid(row=4,column=0,columnspan=3,sticky='news',padx=5,pady=5)
b.bind('<Return>',lambda ev: connect(ip,e))
connectLabel=ttk.Label(connectLF,text='You are not connected to a server.',foreground='red')
connectLabel.grid(row=5,column=0,columnspan=3,padx=5,pady=5)


'''
------------------------------------------

Quota section

------------------------------------------
'''
quotaLF=ttk.Labelframe(addNewFrame,text='Credits',width=200,height=350)
quotaLF.grid(row=2,column=1,padx=(0,5),pady=5,sticky='news')
quotaLF.columnconfigure(2,weight=1)
credit=StringVar()
maxCredit=StringVar()
minCredit=StringVar()
sheetCredit=StringVar()
sheetMax=StringVar()
discount=StringVar()
ttk.Label(quotaLF,text='rials').grid(row=0,column=2,padx=5,pady=5,sticky='w')
ttk.Label(quotaLF,text='rials').grid(row=1,column=2,padx=5,pady=5,sticky='w')
ttk.Label(quotaLF,text='rials').grid(row=2,column=2,padx=5,pady=5,sticky='w')
ttk.Label(quotaLF,text='sheets').grid(row=3,column=2,padx=5,pady=5,sticky='w')
ttk.Label(quotaLF,text='sheets').grid(row=4,column=2,padx=5,pady=5,sticky='w')
ttk.Label(quotaLF,text='percent').grid(row=5,column=2,padx=5,pady=(5,10),sticky='w')
ttk.Entry(quotaLF,textvariable=credit).grid(row=0,column=1,padx=5,pady=5)
ttk.Entry(quotaLF,textvariable=maxCredit).grid(row=1,column=1,padx=5,pady=5)
ttk.Entry(quotaLF,textvariable=minCredit).grid(row=2,column=1,padx=5,pady=5)
ttk.Entry(quotaLF,textvariable=sheetCredit).grid(row=3,column=1,padx=5,pady=5)
ttk.Entry(quotaLF,textvariable=sheetMax).grid(row=4,column=1,padx=5,pady=5)
ttk.Entry(quotaLF,textvariable=discount).grid(row=5,column=1,padx=5,pady=(5,10))
ttk.Label(quotaLF,text='Credit:').grid(row=0,column=0,padx=5,pady=5,sticky='w')
ttk.Label(quotaLF,text='Max permitted credit:').grid(row=1,column=0,padx=5,pady=5,sticky='w')
ttk.Label(quotaLF,text='Min permitted credit:').grid(row=2,column=0,padx=5,pady=5,sticky='w')
ttk.Label(quotaLF,text='Sheet credit:').grid(row=3,column=0,padx=5,pady=5,sticky='w')
ttk.Label(quotaLF,text='Max permitted sheet credit:').grid(row=4,column=0,padx=5,pady=5,sticky='w')
ttk.Label(quotaLF,text='Discount:').grid(row=5,column=0,padx=5,pady=(5,10),sticky='w')


'''
------------------------------------------

Result tree section

------------------------------------------
'''
treeLF=ttk.Labelframe(addNewFrame,text='Search results')
treeLF.grid(row=0,column=0,rowspan=3,padx=5,pady=5,sticky='news')
treeLF.rowconfigure(0,weight=1)
tree=ttk.Treeview(treeLF)
tree.grid(row=0,column=0,columnspan=2,pady=(5,0),sticky='nws')
s=ttk.Scrollbar(treeLF,orient=VERTICAL,command=tree.yview)
s.grid(row=0,column=2,pady=(5,0),sticky='ns')
tree.configure(yscrollcommand=s.set)
tree.tag_configure('green',background='#88CC22')
tree.tag_configure('white',background='white')
tree.tag_configure('yellow',background='#CCEE66')
b=ttk.Button(treeLF,text='Select',command= lambda: toggleColor(1,tree.selection()))
b.grid(row=1,column=0,sticky='news',padx=5,pady=5)
b.bind('<Return>',lambda ev: toggleColor(1))
b2=ttk.Button(treeLF,text='Deselect',command= lambda: toggleColor(0,tree.selection()))
b2.grid(row=1,column=1,sticky='news',padx=5,pady=5)
b2.bind('<Return>',lambda ev: toggleColor(0))


'''
------------------------------------------

Add to database button

------------------------------------------
'''
addB=ttk.Button(addNewFrame,text='Add selected entries',command=addToDB)
addB.grid(row=3,column=1,sticky='news',padx=(0,5),pady=(0,5))
addB.bind('<Return>',addToDB)


'''
==========================================

Menubar

==========================================
'''
root.option_add('*tearOff', FALSE)
menubar=Menu(root)
root.configure(menu=menubar)
menu1 = Menu(menubar)
menubar.add_cascade(menu=menu1, label='menu')
menu1.add_command(label='settings')
menu1.add_command(label='about')


'''
==========================================

Tab to be used for updating existing
entries

==========================================
'''
updateFrame=ttk.Frame(nb)
updateFrame.grid(row=0,column=0)
updateFrame.columnconfigure(1,weight=1)


'''
------------------------------------------

Result tree section 2

------------------------------------------
'''
treeLF2=ttk.Labelframe(updateFrame,text='Search result')
treeLF2.grid(row=0,column=0,rowspan=3,padx=5,pady=5,sticky='news')
treeLF2.rowconfigure(0,weight=1)
tree2=ttk.Treeview(treeLF2,columns=['Grade','Department'])
tree2.heading('#0', text='Name')
tree2.heading('#1', text='Grade')
tree2.heading('#2', text='Department')
tree2.column('#0',minwidth=100,width=100)
tree2.column('#1',minwidth=50,width=50)
tree2.column('#2',minwidth=50,width=50)
tree2.grid(row=0,column=0,columnspan=2,pady=(5,0),sticky='nws')
s2=ttk.Scrollbar(treeLF2,orient=VERTICAL,command=tree2.yview)
s2.grid(row=0,column=2,pady=(5,0),sticky='ns')
tree2.configure(yscrollcommand=s2.set)
s3=ttk.Scrollbar(treeLF2,orient=HORIZONTAL,command=tree2.xview)
s3.grid(row=1,column=0,columnspan=2,pady=(5,0),sticky='ew')
tree2.configure(xscrollcommand=s3.set)
# tree.tag_configure('green',background='#88CC22')
# tree.tag_configure('white',background='white')
# tree.tag_configure('yellow',background='#CCEE66')
b21=ttk.Button(treeLF2,text='Select')
b21.grid(row=2,column=0,sticky='news',padx=5,pady=5)
b22=ttk.Button(treeLF2,text='Deselect')
b22.grid(row=2,column=1,sticky='news',padx=5,pady=5)


'''
------------------------------------------

Select entries section

------------------------------------------
'''
selectEntriesLF=ttk.Labelframe(updateFrame,text='Select Entries',width=200,height=50)
selectEntriesLF.grid(row=0,column=1,padx=(0,5),pady=5,sticky='news')
selectEntriesLF.columnconfigure(1,weight=1)
# b2.bind('<Return>',lambda ev: connect(ip,e))
ttk.Label(selectEntriesLF,text='Grade:').grid(row=0,column=0,padx=(50,5),pady=5,sticky='w')
ttk.Label(selectEntriesLF,text='Department:').grid(row=1,column=0,padx=(50,5),pady=5,sticky='w')
ttk.Label(selectEntriesLF,text='Entrance year:').grid(row=2,column=0,padx=(50,5),pady=5,sticky='w')
grade=StringVar()
department=StringVar()
entranceYear=StringVar()
grades=['all','bs','ms','phd']
departments=['all','Physics','Mathematics','Chemistry','Agricultural Engineering',
			'Natural Resources','Electrical & Computer Eng','Industrial Engineering',
			'Materials Engineering','Mining Engineering','Civil Engineering',
			'Mechanical Engineering','Chemical Engineering','Textile Engineering']
entranceYears=['all']
grade.set(grades[0])
department.set(departments[0])
entranceYear.set(entranceYears[0])
ttk.Combobox(selectEntriesLF,textvariable=grade,values=grades,state='readonly').grid(row=0,column=1,padx=(5,50),pady=5,sticky='we')
ttk.Combobox(selectEntriesLF,textvariable=department,values=departments,state='readonly').grid(row=1,column=1,padx=(5,50),pady=5,sticky='we')
ttk.Combobox(selectEntriesLF,textvariable=entranceYear,values=entranceYears).grid(row=2,column=1,padx=(5,50),pady=5,sticky='we')
b2=ttk.Button(selectEntriesLF,text='Select')
b2.grid(row=3,column=0,columnspan=2,sticky='ew',padx=5,pady=5)
selectLabel=ttk.Label(selectEntriesLF,text='You are not selected any entries.',foreground='red')
selectLabel.grid(row=4,column=0,columnspan=3,padx=5,pady=5)


'''
------------------------------------------

Quota section 2

------------------------------------------
'''
quotaLF2=ttk.Labelframe(updateFrame,text='Credits',width=200,height=350)
quotaLF2.grid(row=2,column=1,padx=(0,5),pady=5,sticky='news')
quotaLF2.columnconfigure(2,weight=1)
credit2=StringVar()
maxCredit2=StringVar()
minCredit2=StringVar()
sheetCredit2=StringVar()
sheetMax2=StringVar()
discount2=StringVar()
ttk.Label(quotaLF2,text='rials').grid(row=0,column=2,padx=5,pady=5,sticky='w')
ttk.Label(quotaLF2,text='rials').grid(row=1,column=2,padx=5,pady=5,sticky='w')
ttk.Label(quotaLF2,text='rials').grid(row=2,column=2,padx=5,pady=5,sticky='w')
ttk.Label(quotaLF2,text='sheets').grid(row=3,column=2,padx=5,pady=5,sticky='w')
ttk.Label(quotaLF2,text='sheets').grid(row=4,column=2,padx=5,pady=5,sticky='w')
ttk.Label(quotaLF2,text='percent').grid(row=5,column=2,padx=5,pady=(5,10),sticky='w')
ttk.Entry(quotaLF2,textvariable=credit2).grid(row=0,column=1,padx=5,pady=5)
ttk.Entry(quotaLF2,textvariable=maxCredit2).grid(row=1,column=1,padx=5,pady=5)
ttk.Entry(quotaLF2,textvariable=minCredit2).grid(row=2,column=1,padx=5,pady=5)
ttk.Entry(quotaLF2,textvariable=sheetCredit).grid(row=3,column=1,padx=5,pady=5)
ttk.Entry(quotaLF2,textvariable=sheetMax2).grid(row=4,column=1,padx=5,pady=5)
ttk.Entry(quotaLF2,textvariable=discount2).grid(row=5,column=1,padx=5,pady=(5,10))
ttk.Label(quotaLF2,text='Credit:').grid(row=0,column=0,padx=5,pady=5,sticky='w')
ttk.Label(quotaLF2,text='Max permitted credit:').grid(row=1,column=0,padx=5,pady=5,sticky='w')
ttk.Label(quotaLF2,text='Min permitted credit:').grid(row=2,column=0,padx=5,pady=5,sticky='w')
ttk.Label(quotaLF2,text='Sheet credit:').grid(row=3,column=0,padx=5,pady=5,sticky='w')
ttk.Label(quotaLF2,text='Max permitted sheet credit:').grid(row=4,column=0,padx=5,pady=5,sticky='w')
ttk.Label(quotaLF2,text='Discount:').grid(row=5,column=0,padx=5,pady=(5,10),sticky='w')


'''
------------------------------------------

Update database button

------------------------------------------
'''
addB=ttk.Button(updateFrame,text='Update selected entries')
addB.grid(row=3,column=1,sticky='news',padx=(0,5),pady=(0,5))
# addB.bind('<Return>',addToDB)


'''
------------------------------------------

Adding frames to notebook

------------------------------------------
'''
nb.add(addNewFrame,text='Add new users')
nb.add(updateFrame,text='Update existing users')


'''
==========================================

Opening file and checking whether it is
first time the program is run

==========================================
'''
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
		t.title('Default server IP address modification')
		ttk.Label(t,text='Default server IP address is set to 127.0.0.1. Do you want to change it?').grid(row=0,column=0,columnspan=2,padx=10,pady=10)
		y=ttk.Button(t,text='Yes',command= lambda: setDefaultIP(configurations,t))
		y.grid(row=2,column=0,padx=10,pady=10,sticky='e')
		y.bind('<Return>',lambda ev: setDefaultIP(configurations,t))
		n=ttk.Button(t,text='No',command= lambda: close(root,t))
		n.grid(row=2,column=1,padx=10,pady=10,sticky='w')
		n.bind('<Return>',lambda ev: close(root,t))

root.mainloop()
