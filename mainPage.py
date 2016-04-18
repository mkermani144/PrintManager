from tkinter import *
from tkinter import messagebox
from tkinter import ttk
from re import match
from ldap3 import *
import pypyodbc
import time


'''
++++++++++++++++++++++++++++++++++++++++++

Function to destroy widgets passed to it
excluding the first one

>>> *args:  All of the widgets to be
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

>>> ip:  The IP to be validated.

++++++++++++++++++++++++++++++++++++++++++
'''
def validateIP(ip):
	return re.match('^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$',ip.get())


'''
++++++++++++++++++++++++++++++++++++++++++

Function to connect to the LDAP server and
to make the result tree

>>> ip:  The IP of the LDAP server.
>>> e:   Entry of above IP.

++++++++++++++++++++++++++++++++++++++++++
'''
def connect(ip,e):
	if validateIP(ip):
		server=Server(ip.get(),use_ssl=True,connect_timeout=.5)
		username='cn=administrator,cn=users,dc=salon,dc=iut'
		password='Server2014'
		connection=Connection(server,username,password,read_only=True)
		usersDictionary={}
		try:
			connection.bind()
			tree.insert('',0,text='salon.iut',iid='DC=salon,DC=iut',tags='white')
			connection.search(search_base='dc=salon,dc=iut',
				search_filter='(objectClass=organizationalUnit)',
				search_scope=SUBTREE)
			connection.entries.sort()
			i=0
			for entry in connection.entries:
				dn=entry.entry_get_dn()
				tree.insert(dn[dn.find(',')+1:],i,text=dn[dn.find('=')+1:dn.find(',')],iid=dn,tags='white')
				i+=1

			connection.search(search_base='dc=salon,dc=iut',
				search_filter='(objectClass=user)',
				search_scope=SUBTREE,
				attributes=['givenName','sn','cn','department','description'])
			connection.entries.sort()
			i=0
			for entry in connection.entries:
				dn=entry.entry_get_dn()
				try:
					tree.insert(dn[dn.find(',')+1:],i,text=entry['cn'],iid=dn,tags='white')
					usersDictionary[entry['cn']]=entry.entry_get_attributes_dict()
					i+=1
				except:
					pass
			connection.unbind()
			connectLabel.configure(text='Successfully connected to server.',foreground='green')
			quotaLF.state(['!disabled'])
			for widget in quotaLF.winfo_children():
				widget.state(['!disabled'])
			treeLF.state(['!disabled'])
			for widget in treeLF.winfo_children():
				widget.state(['!disabled'])
			addB.state(['!disabled'])
		except:
			messagebox.showerror(title='Connection error',message='Cannot connect to server')

	else:
		flag=messagebox.askretrycancel(title='IP address invalidation',message='IP address is not valid.',icon='error')
		if flag:
			e.delete(0,'end')
			e.focus()


'''
++++++++++++++++++++++++++++++++++++++++++

Function to get the default IP of the
server from user and set it to the file

>>> configurations:  A list containing
					 configurations of
					 the program.
>>> w:  			 Popup widget asking
					 the user if he wants
					 to change default ip.

++++++++++++++++++++++++++++++++++++++++++
'''
def setDefaultIP(configurations):
	def setDefaultIPInner():
		if validateIP(ip):
			configurations[0]=ip.get()
			updateConf(configurations)
			messagebox.showinfo(title='Successful operation',message='Default server IP address changed sucessfully.')
		else:
			flag=messagebox.askretrycancel(title='IP address invalidation',message='IP address is not valid.',icon='error')
			if flag:
				e.delete(0,'end')
				e.focus()
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
	# b.bind('<Return>',setDefaultIPInner(e))
	b2=ttk.Button(t,text='Cancel',command= lambda: close(root,t))
	b2.grid(row=2,column=1,padx=10,pady=10,sticky='w')
	# b2.bind('<Return>',lambda ev: close(root,t))


'''
++++++++++++++++++++++++++++++++++++++++++

Function to toggle between two radio
buttons

>>> rbv:  	Radio button variable
			indicating state of radio
			buttons.
>>> entry:  Entry of the IP address.

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

>>> configuration:  List contaning
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

>>> type:  String indicating if function
		   call type should be simple or
		   complex.
>>> flag:  Flag indicating if the entry
		   should be disabled/enabled.
>>> l:     List containing all of result
		   tree entries whose colors
		   should be toggled.

++++++++++++++++++++++++++++++++++++++++++
'''
def toggleColor(type,flag,l):
	if type=='complex':
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
	else:
		state=('white','green') if flag==1 else ('green','white')
		for entry in l:
			tree.item(entry,tags=[w.replace(state[0],state[1]) for w in tree.item(entry)['tags']])


'''
++++++++++++++++++++++++++++++++++++++++++

Function to add selected result tree
entries to the database

++++++++++++++++++++++++++++++++++++++++++
'''
def addToDB():
	if not (credit.get().isdigit() and maxCredit.get().isdigit() and minCredit.get().isdigit()
			and sheetCredit.get().isdigit() and sheetMax.get().isdigit() and discount.get().isdigit()):
			messagebox.showerror(title='Invalid input',
			message='Some of the entries of credits section are not valid.')
	selectionIIDs=[x for x in tree.tag_has('green') if not tree.get_children(x)]
	selection=[tree.item(x,text) for x in selectionIIDs]
	i=0
	j=0
	for item in selection:
		query='''
			INSERT INTO credits
			VALUES
			("%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s")
		''' % usersDictionary[item]['givenName'],usersDictionary[item]['sn'],usersDictionary[item]['cn'][:2],
		usersDictionary[item]['cn'],usersDictionary[item]['description'].split()[2],
		usersDictionary[item]['department'],usersDictionary[item]['description'].split()[1],
		credit,maxCredit,minCredit,sheetCredit,sheetMax,discount
		checkQuery='SELECT * FROM credits WHERE student_number=%s' % item['cn']
		conn=pypyodbc.win_connect_mdb('C:\database.mdb')
		cur=conn.cursor()
		cur.execute(checkQuery)
		if not len(cur.description):
			i+=1
			cur.execute(query)
		else:
			j+=1
		if i==0:
			messagebox.showinfo(title='Successful operation',
								message='All of the selected entries exist in the database. No entry added to database.')
		elif j==0:
			messagebox.showinfo(title='Successful operation',
								message='All of the selected entries added to database.')
		else:
			messagebox.showinfo(title='Successful operation',
								message=str(i)+' entries of '+str(i+j)+' entry added to database.')


'''
++++++++++++++++++++++++++++++++++++++++++

Function to fetch data from database based
on entry values

>>> grade:  	   Grade of students to be
				   fetched.
>>> department:    department of students to
				   be fetched.
>>> entranceYear:  Entrance year of
				   students to be fetched.

++++++++++++++++++++++++++++++++++++++++++
'''
def fetchFromDB(grade,department,entranceYear):
	try:
		conn=pypyodbc.win_connect_mdb('C:\database.mdb')
		cur=conn.cursor()
		query='SELECT * FROM credits'
		if grade!='all' or department!='all' or entranceYear!='all':
			query+=' WHERE'
		if grade!='all':
			query+=' grade=%s' % grade
		if department!='all':
			query+=' AND department=%s' % department
		if entranceYear!='all':
			query+=' AND entrance_year=%s' % entranceYear
		cur.execute(query)
		for row in cur.description:
			tree.insert('',0,text=row[0]+row[1],iid=row[0]+column[0],tag='white')
		quotaLF2.state(['!disabled'])
		for widget in quotaLF.winfo_children():
			widget.state(['!disabled'])
		treeLF2.state(['!disabled'])
		for widget in treeLF.winfo_children():
			widget.state(['!disabled'])
		updateB.state(['!disabled'])
	except:
		pass



'''
++++++++++++++++++++++++++++++++++++++++++

Function to update selected result tree
entries

>>> e:  Event object.

++++++++++++++++++++++++++++++++++++++++++
'''
def updateDB(e):
	if not (credit2.get().isdigit() and maxCredit2.get().isdigit() and minCredit2.get().isdigit()
			and sheetCredit2.get().isdigit() and sheetMax2.get().isdigit() and discount2.get().isdigit()):
			messagebox.showerror(title='Invalid input',
			message='Some of the entries of credits section are not valid.')


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
connectLabel=ttk.Label(connectLF,text='You are not connected to any server.',foreground='red')
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
quotaLF.state(['disabled'])
for widget in quotaLF.winfo_children():
	widget.state(['disabled'])


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
b=ttk.Button(treeLF,text='Select',command= lambda: toggleColor('complex',1,tree.selection()))
b.grid(row=1,column=0,sticky='news',padx=5,pady=5)
b2=ttk.Button(treeLF,text='Deselect',command= lambda: toggleColor('complex',0,tree.selection()))
b2.grid(row=1,column=1,sticky='news',padx=5,pady=5)
treeLF.state(['disabled'])
for widget in treeLF.winfo_children():
	widget.state(['disabled'])


'''
------------------------------------------

Add to database button

------------------------------------------
'''
addB=ttk.Button(addNewFrame,text='Add selected entries',command=addToDB)
addB.grid(row=3,column=1,sticky='news',padx=(0,5),pady=(0,5))
addB.bind('<Return>',addToDB)
addB.state(['disabled'])


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
b21=ttk.Button(treeLF2,text='Select',command= lambda: toggleColor('simple',1,tree2.selection()))
b21.grid(row=2,column=0,sticky='news',padx=5,pady=5)
b22=ttk.Button(treeLF2,text='Deselect',command= lambda: toggleColor('simple',0,tree2.selection()))
b22.grid(row=2,column=1,sticky='news',padx=5,pady=5)
treeLF2.state(['disabled'])
for widget in treeLF2.winfo_children():
	widget.state(['disabled'])


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
b2=ttk.Button(selectEntriesLF,text='Fetch',command= lambda: fetchFromDB(grade,department,entranceYear))
b2.grid(row=3,column=0,columnspan=2,sticky='ew',padx=5,pady=5)
selectLabel=ttk.Label(selectEntriesLF,text='You have not fetched any entries.',foreground='red')
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
quotaLF2.state(['disabled'])
for widget in quotaLF2.winfo_children():
	widget.state(['disabled'])


'''
------------------------------------------

Update database button

------------------------------------------
'''
updateB=ttk.Button(updateFrame,text='Update selected entries')
updateB.grid(row=3,column=1,sticky='news',padx=(0,5),pady=(0,5))
updateB.state(['disabled'])
# addB.bind('<Return>',addToDB)


'''
------------------------------------------

Adding frames to notebook

------------------------------------------
'''
nb.add(addNewFrame,text=' Add new users ')
nb.add(updateFrame,text=' Update existing users ')


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
				entrance_year VARCHAR(2),
				student_number VARCHAR(7),
				grade VARCHAR(3),
				department VARCHAR(15),
				field VARCHAR(15),
				credit VARCHAR(7),
				max_credit VARCHAR(10),
				min_credit VARCHAR(10),
				paper_credit VARCHAR(6),
				paper_max_credit VARCHAR(6),
				discount VARCHAR(3)
			)
		'''
		cur.execute(query)
		cur.close()
		conn.commit()
		conn.close()
		flag=messagebox.askyesno(message='Default server IP address is set to 127.0.0.1. Do you want to change it?',
									icon='question',title='Default IP modification')
		if flag:
			setDefaultIP(configurations)

root.mainloop()
