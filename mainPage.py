from __future__ import with_statement
from tkinter import *
from tkinter import messagebox
from tkinter import ttk
from re import match
from ldap3 import *
import pypyodbc
import time
import socket
from datetime import datetime
import sys

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
    for w in filter(lambda w: args.index(w), args):
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
    try:
        socket.inet_aton(ip.get())
        return True
    except socket.error:
        return False


'''
++++++++++++++++++++++++++++++++++++++++++

Function to see if the Domain is valid

>>> domain:  The domain to be validated.

++++++++++++++++++++++++++++++++++++++++++
'''


def validateDomain(domain):
    return re.match('^[A-Za-z0-9]+\.[A-Za-z0-9]+$', domain.get())


'''
++++++++++++++++++++++++++++++++++++++++++

Function to connect to the LDAP server and
to make the result tree

>>> ip:  The IP of the LDAP server.
>>> e:   Entry of above IP.

++++++++++++++++++++++++++++++++++++++++++
'''


def connect(ip, e):
    server = Server(ip.get(), use_ssl=True, connect_timeout=.5)
    subdomain, ldomain = domain.get().split('.')
    username_dn = 'cn=' + username.get()
    username_dn += ',cn=users,dc={},dc={}'.format(subdomain, ldomain) if username.get(
    ) == 'administrator' else ',ou=admins,ou={},dc={},dc={}'.format(subdomain, subdomain, ldomain)
    username_dn = username_dn.rstrip()
    connection = Connection(server, username_dn,
                            password.get(), read_only=True)
    global usersDictionary
    usersDictionary = {}
    try:
        connection.bind()
        tree.insert('', 0, text='{}'.format(configurations[2]),
                    iid='OU={},DC={},DC={}'.format(subdomain.lower(), subdomain.lower(), ldomain).rstrip(), tags='white')
        connection.search(search_base='ou={}, dc={}, dc={}'.format(subdomain, subdomain, ldomain).rstrip(),
                          search_filter='(objectClass=organizationalUnit)',
                          search_scope=SUBTREE
                          )
        connection.entries.sort(key=lambda s: len(str(s)))
        i = 0
        for entry in connection.entries:
            dn = entry.entry_get_dn()
            tree.insert(dn[dn.find(
                ',') + 1:], i, text=dn[dn.find('=') + 1:dn.find(',')], iid=dn, tags='white')
            i += 1

        connection.search(search_base='ou={}, dc={}, dc={}'.format(subdomain, subdomain, ldomain).rstrip(),
                          search_filter='(objectClass=user)',
                          search_scope=SUBTREE,
                          attributes=['givenName', 'sn', 'cn', 'department', 'description'])
        connection.entries.sort()
        i = 0
        for entry in connection.entries[::-1]:
            dn = entry.entry_get_dn()
            try:
                tree.insert(dn[dn.find(',') + 1:], i,
                            text=entry['cn'], iid=dn, tags='white')
                usersDictionary[
                    str(entry['cn'])] = entry.entry_get_attributes_dict()
                usersDictionary[str(entry['cn'])].update({'dn': dn})
                i += 1
            except RuntimeError as er:
                pass
        connection.unbind()
        connectLabel.configure(
            text='Successfully connected to server.', foreground='green')
        quotaLF.state(['!disabled'])
        for widget in quotaLF.winfo_children():
            widget.state(['!disabled'])
        treeLF.state(['!disabled'])
        for widget in treeLF.winfo_children():
            widget.state(['!disabled'])
        addB.state(['!disabled'])
    except RuntimeError as er:
        messagebox.showerror(title='Connection error',
                             message='Cannot connect to server')
    finally:
        connection.unbind()

'''
++++++++++++++++++++++++++++++++++++++++++

Function to get the default IP of the
server from user and set it to the file

>>> configurations:  A list containing
                     configurations of
                     the program.
>>> w:               Popup widget asking
                     the user if he wants
                     to change default ip.

++++++++++++++++++++++++++++++++++++++++++
'''


def setDefaultIP(configurations):
    def setDefaultIPInner():
        if validateIP(ip):
            configurations[0] = ip.get()
            updateConf(configurations)
            ip.set(ip.get())
            messagebox.showinfo(title='Successful operation',
                                message='Default server IP address changed sucessfully.')
            close(root, t)
            goForDomain()
        else:
            flag = messagebox.askretrycancel(
                title='IP address invalidation', message='IP address is not valid.', icon='error')
            if flag:
                e.delete(0, 'end')
                e.focus()
    def goForDomain():
        flag2 = messagebox.askyesno(
            message='Default server domain address is set to sub.domain. Do you want to change it?', icon='question', title='Default domain modification')
        if flag2:
            setDefaultDomain(configurations)
    t = Toplevel(root)
    t.resizable(False, False)
    t.grab_set()  # Make parent disabled
    t.title('Default server ip address')
    ttk.Label(t, text='Please enter IP address for deafault server:').grid(
        row=0, column=0, columnspan=2, padx=10, pady=10)
    e = ttk.Entry(t, width=45, textvariable=ip)
    e.grid(row=1, column=0, columnspan=2, padx=30, pady=10)
    e.focus()
    b = ttk.Button(t, text='OK', command=setDefaultIPInner)
    b.grid(row=2, column=0, padx=10, pady=10, sticky='e')
    # b.bind('<Return>',setDefaultIPInner(e))
    b2 = ttk.Button(t, text='Cancel', command=lambda: [close(root, t),
    goForDomain()])
    b2.grid(row=2, column=1, padx=10, pady=10, sticky='w')
    # b2.bind('<Return>',lambda ev: close(root,t))
    center(t)


'''
++++++++++++++++++++++++++++++++++++++++++

Function to get the default domain of the
server from user and set it to the file

>>> configurations:  A list containing
                     configurations of
                     the program.
>>> w:               Popup widget asking
                     the user if he wants
                     to change default
                     domain.

++++++++++++++++++++++++++++++++++++++++++
'''


def setDefaultDomain(configurations):
    def setDefaultDomainInner():
        if validateDomain(domain):
            configurations[2] = domain.get()
            updateConf(configurations)
            domain.set(domain.get())
            messagebox.showinfo(title='Successful operation',
                                message='Default server domain address changed sucessfully.')
            close(root, t)
        else:
            flag = messagebox.askretrycancel(
                title='Domain address invalidation', message='Domain address is not valid.', icon='error')
            if flag:
                e.delete(0, 'end')
                e.focus()
    t = Toplevel(root)
    t.resizable(False, False)
    t.grab_set()  # Make parent disabled
    t.title('Default server domain address')
    ttk.Label(t, text='Please enter domain address for deafault server:').grid(
        row=0, column=0, columnspan=2, padx=10, pady=10)
    e = ttk.Entry(t, width=45, textvariable=domain)
    e.grid(row=1, column=0, columnspan=2, padx=30, pady=10)
    e.focus()
    b = ttk.Button(t, text='OK', command=setDefaultDomainInner)
    b.grid(row=2, column=0, padx=10, pady=10, sticky='e')
    # b.bind('<Return>',setDefaultDomainInner(e))
    b2 = ttk.Button(t, text='Cancel', command=lambda: close(root, t))
    b2.grid(row=2, column=1, padx=10, pady=10, sticky='w')
    # b2.bind('<Return>',lambda ev: close(root,t))
    center(t)


'''
++++++++++++++++++++++++++++++++++++++++++

Function to toggle between two radio
buttons

>>> rbv:      Radio button variable
            indicating state of radio
            buttons.
>>> entry:  Entry of the IP address or
            domain name.
>>> flag:   Number indicating type of
            ip_or_domain. 0 for ip, 2 for
            domain.

++++++++++++++++++++++++++++++++++++++++++
'''


def toggleEntry(rbv, entry, ip_or_domain, flag):
    if rbv.get() == 'new':
        entry.config(state='enabled')
        ip_or_domain.set('')
        e1.focus()
    else:
        entry.config(state='disabled')
        with open('conf') as f:
            ip_or_domain.set(f.readlines()[flag].rstrip())


'''
++++++++++++++++++++++++++++++++++++++++++

Function to update the conf file

>>> configuration:  List contaning
                    configurations of the
                    program.

++++++++++++++++++++++++++++++++++++++++++
'''


def updateConf(configurations):
    with open('conf', 'w') as f:
        for item in configurations:
            f.write(item + '\n')


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


def toggleColor(type, flag, l):
    if type == 'complex':
        def toggleFatherColor(entry):
            p = tree.parent(entry)
            if p:
                tree.item(p, tags=[w.replace(state[0], 'yellow')
                                   for w in tree.item(p)['tags']])
                l = [tree.item(x)['tags'] for x in tree.get_children(p)]
                if(flag == 1):
                    for child in l:
                        if 'yellow' in child or 'white' in child:
                            break
                    else:
                        tree.item(p, tags=[w.replace('yellow', 'green')
                                           for w in tree.item(p)['tags']])
                else:
                    for child in l:
                        if 'yellow' in child or 'green' in child:
                            break
                    else:
                        tree.item(p, tags=[w.replace('yellow', 'white')
                                           for w in tree.item(p)['tags']])
                toggleFatherColor(tree.parent(entry))

        def toggleChildColor(entry):
            for e in tree.get_children(entry):
                tree.item(e, tags=[w.replace(state[0], state[1])
                                   for w in tree.item(e)['tags']])
                tree.item(e, tags=[w.replace('yellow', state[1])
                                   for w in tree.item(e)['tags']])
                toggleChildColor(e)

        state = ('white', 'green') if flag == 1 else ('green', 'white')
        for entry in l:
            tree.item(entry, tags=[w.replace(state[0], state[1])
                                   for w in tree.item(entry)['tags']])
            tree.item(entry, tags=[w.replace('yellow', state[1])
                                   for w in tree.item(entry)['tags']])
            toggleFatherColor(entry)
            toggleChildColor(entry)

        tree.selection_set(tuple())
    else:
        state = ('white', 'green') if flag == 1 else ('green', 'white')
        for entry in l:
            tree2.item(entry, tags=[w.replace(state[0], state[1])
                                    for w in tree2.item(entry)['tags']])
        tree2.selection_set(tuple())


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
    selectionIIDs = [x for x in tree.tag_has(
        'green') if not tree.get_children(x)]
    selection = [tree.item(x) for x in selectionIIDs]
    if selection:
        i = 0
        j = 0
        conn = pypyodbc.win_connect_mdb('./XLDB.mdb')
        cur = conn.cursor()
        mp = {
            'B.Sc': 'bs',
            'M.Sc': 'ms',
            'Ph.D': 'phd'
        }
        depQuery = "SELECT DepartmentName FROM Departments;"
        cur.execute(depQuery)
        dep = cur.fetchall()[0][0]
        for item in selection:
            checkQuery = "SELECT * FROM Users WHERE userName=?;"
            l = []
            l.append(str(usersDictionary[item['text']]['cn'][0]))
            cur.execute(checkQuery, l)
            if not len(cur.fetchall()):
                i += 1
                val = [
                    usersDictionary[item['text']]['givenName'][0], # firstname
                    usersDictionary[item['text']]['sn'][0], # lastname
                    dep, # department
                    mp[usersDictionary[item['text']]['dn'].split(',')[2][3:]], # grade
                    int(discount.get()), # discount
                    int(sheetCredit.get()), # paper_credit
                    int(credit.get()), # credit
                    int(minCredit.get()), # min_credit
                    True, # enabled
                    int('13' + usersDictionary[item['text']]['cn'][0][:2]), # entrance_year
                    str(usersDictionary[item['text']]['cn'][0]), # username
                    datetime.now(), # add_date
                    int(maxCredit.get()), # max_credit
                    int(sheetMax.get()) # max_paper_credit
                ]
                query = '''
                    INSERT INTO Users
                    (
                        Name,
                        Family,
                        Department,
                        Grade,
                        Discount,
                        paperCredit,
                        Credit,
                        minCredit,
                        Enabled,
                        EntranceYear,
                        userName,
                        addDate,
                        maxCredit,
                        maxPaperCredit
                    )
                    VALUES
                    (
                        ?,
                        ?,
                        ?,
                        ?,
                        ?,
                        ?,
                        ?,
                        ?,
                        ?,
                        ?,
                        ?,
                        ?,
                        ?,
                        ?
                    );
                '''
                cur.execute(query, val)
            else:
                j += 1
        cur.commit()
        cur.close()
        conn.close()
        if i == 0:
            messagebox.showinfo(title='Successful operation',
                                message='All of the selected entries exist in the database. No entry added to database.')
        elif j == 0:
            messagebox.showinfo(title='Successful operation',
                                message='All of the selected entries added to database.')
        else:
            messagebox.showinfo(title='Successful operation',
                                message=str(i) + ' entries of ' + str(i + j) + ' entry added to database.')
    else:
        messagebox.showinfo(title='Empty selection',
                            message='No one of the entries selected. Please select at least one.')


'''
++++++++++++++++++++++++++++++++++++++++++

Function to fetch data from database based
on entry values

>>> grade:         Grade of students to be
                   fetched.
>>> department:    department of students to
                   be fetched.
>>> entranceYear:  Entrance year of
                   students to be fetched.

++++++++++++++++++++++++++++++++++++++++++
'''


def fetchFromDB(grade, department, entranceYear):
    try:
        conn = pypyodbc.win_connect_mdb('./XLDB.mdb')
        cur = conn.cursor()
        tree2.delete(*tree2.get_children())
        query = 'SELECT * FROM Users'
        needsAnd = False
        vals = []
        if grade.get() != 'all' or department.get() != 'all' or entranceYear.get() != 'all':
            query += ' WHERE'
        if grade.get() != 'all':
            needsAnd = True
            query += " Grade=?"
            vals.append(grade.get())
        if department.get() != 'all':
            if needsAnd:
                query += " AND Department=?"
                vals.append(department.get())
            else:
                query += " Department=?"
                vals.append(department.get())
            needsAnd = True
        if entranceYear.get() != 'all':
            if needsAnd:
                query += " AND EntranceYear=?"
                vals.append(int(entranceYear.get()))
            else:
                query += " EntranceYear=?"
                vals.append(int(entranceYear.get()))
        query += ';'
        global usersStdnums
        usersStdnums = {}
        cur.execute(query, vals)
        data = cur.fetchall().copy()
        if data:
            selectLabel.configure(
                text='Successfully fetched data from database.', foreground='green')
            for row in data:
                tree2.insert('', 0, text=str(row[
                             0]) + ' ' + str(row[1]), iid=str(row[0]) + ' ' + str(row[1]), tag='green')
                usersStdnums[str(row[0]) + ' ' + str(row[1])] = str(row[15])
            quotaLF2.state(['!disabled'])
            for widget in quotaLF2.winfo_children():
                widget.state(['!disabled'])
            treeLF2.state(['!disabled'])
            for widget in treeLF2.winfo_children():
                widget.state(['!disabled'])
            updateB.state(['!disabled'])
        else:
            messagebox.showinfo(title='No result',
                                message='The database returned no result.')
        cur.close()
        conn.close()
    except Exception as er:
        messagebox.showinfo(title='No result',
                                message='The database returned no result.')


'''
++++++++++++++++++++++++++++++++++++++++++

Function to update selected result tree
entries

>>> e:  Event object.

++++++++++++++++++++++++++++++++++++++++++
'''


def updateDB():
    if not (credit2.get().isdigit() and maxCredit2.get().isdigit() and minCredit2.get().isdigit()
            and sheetCredit2.get().isdigit() and sheetMax2.get().isdigit() and discount2.get().isdigit()):
        messagebox.showerror(title='Invalid input',
                             message='Some of the entries of credits section are not valid.')
    else:
        selectionIIDs = [x for x in tree2.tag_has(
            'green') if not tree2.get_children(x)]
        if selectionIIDs:
            conn = pypyodbc.win_connect_mdb('./XLDB.mdb')
            cur = conn.cursor()
            for item in selectionIIDs:
                val = [
                    int(credit2.get()),
                    int(maxCredit2.get()),
                    int(minCredit2.get()),
                    int(sheetCredit2.get()),
                    int(sheetMax2.get()),
                    int(discount2.get()),
                    usersStdnums[item]
                ]
                print(usersStdnums[item], type(usersStdnums[item]))
                query = '''
                    UPDATE Users
                    SET
                    Credit=?,
                    maxCredit=?,
                    minCredit=?,
                    paperCredit=?,
                    maxPaperCredit=?,
                    Discount=?
                    WHERE
                    userName=?;
                '''
                cur.execute(query, val)
                cur.commit()
            messagebox.showinfo(title='Successful operation',
                                message='All of the selected entries updated.')
            cur.close()
            conn.close()
        else:
            messagebox.showinfo(title='Empty selection',
                                message='No one of the entries selected. Please select at least one.')


'''
++++++++++++++++++++++++++++++++++++++++++

Function to show settings window

++++++++++++++++++++++++++++++++++++++++++
'''


def showSettings():
    def changeSettings():
        if validateIP(defIP) and validateDomain(domain):
            configurations[0] = defIP.get()
            configurations[2] = defDomain.get()
            updateConf(configurations)
            ip.set(defIP.get())
            domain.set(defDomain.get())
            messagebox.showinfo(title='Successful operation',
                                message='Default server ip address and domain name changed successfully.')
            close(root, t)
        else:
            messagebox.showerror(title='Invalid input',
                                 message='IP address or domain entry inputs are not valid.')
            t.lift()
            e1.focus()
    t = Toplevel(root)
    t.resizable(False, False)
    t.grid()
    t.grab_set()
    f = ttk.Frame(t)
    f.grid(padx=10, pady=10)
    defIP = StringVar()
    defDomain = StringVar()
    ttk.Label(f, text='Default server IP address:').grid(
        row=0, column=0, padx=(0, 10), pady=(0, 10), sticky='n')
    ttk.Label(f, text='Domain:').grid(
        row=1, column=0, padx=(0, 10), sticky='nw')
    e1 = ttk.Entry(f, textvariable=defIP)
    e1.grid(row=0, column=1, pady=(0, 10))
    e1.focus()
    e2 = ttk.Entry(f, textvariable=defDomain)
    e2.grid(row=1, column=1)
    e1.bind('<Return>', lambda ev: e2.focus())
    e2.bind('<Return>', lambda ev: changeSettings())
    ttk.Button(f, text='Apply', command=changeSettings).grid(
        row=2, column=0, sticky='e', pady=(10, 0), padx=(0, 5))
    ttk.Button(f, text='Cancel', command=lambda: close(root, t)).grid(
        row=2, column=1, sticky='w', pady=(10, 0))
    center(t)


'''
++++++++++++++++++++++++++++++++++++++++++

Function to authenticate user

++++++++++++++++++++++++++++++++++++++++++
'''


def showAuthenticate():
    if validateIP(ip) and validateDomain(domain):
        def authenticate():
            subdomain, ddomain = domain.get().split('.')
            server = Server(ip.get(), use_ssl=True, connect_timeout=.5)
            username_dn = 'cn=' + username.get()
            username_dn += ',cn=users,dc={},dc={}'.format(subdomain, ddomain) if username.get(
            ) == 'administrator' else ',ou=admins,ou={},dc={},dc={}'.format(subdomain, subdomain, ddomain)
            username_dn = username_dn.rstrip()
            connection = Connection(server, username_dn,
                                    password.get(), read_only=True)
            try:
                connection.bind()
                if not connection.result['result']:
                    close(root, t)
                    messagebox.showinfo(message='Successfully authenticated.')
                    connection.unbind()
                    connect(ip, e)
                else:
                    messagebox.showerror(message='Incorrect username or password.')
                    close(root, t)
                    showAuthenticate()
                    connection.unbind()
            except LDAPException as er:
                messagebox.showerror(message='Cannot contact server: Server timeout.')
                username.set('')
                password.set('')
        t = Toplevel(root)
        t.resizable(False, False)
        t.protocol('WM_DELETE_WINDOW', lambda: [close(root, t), username.set(''), password.set('')])
        # t.geometry('300x100')
        f = ttk.Frame(t)
        f.grid(padx=10, pady=10)
        ttk.Label(f, text='Username:').grid(row=0, column=0,
                                            padx=(0, 10), pady=(0, 10), sticky='n')
        ttk.Label(f, text='Password:').grid(
            row=1, column=0, padx=(0, 10), sticky='nw')
        e = ttk.Entry(f, textvariable=username)
        e.grid(row=0, column=1, pady=(0, 10))
        e.focus()
        e.bind('<Return>', lambda ev: e2.focus())
        e2 = ttk.Entry(f, textvariable=password, show="•")
        e2.grid(row=1, column=1)
        e2.bind('<Return>', lambda ev: authenticate())
        ttk.Button(f, text='Apply', command=authenticate).grid(
            row=2, column=0, columnspan=2, sticky='w', pady=(10, 0), padx=(20, 5))
        ttk.Button(f, text='Cancel', command=lambda: [close(root, t), username.set(''), password.set('')]).grid(
            row=2, column=0, columnspan=2, sticky='e', pady=(10, 0), padx=(5, 20))
        center(t)
    else:
        flag = messagebox.showerror(
            title='Input invalidation', message='IP address or domain name is not valid.', icon='error')

'''
++++++++++++++++++++++++++++++++++++++++++

Function to center a window

++++++++++++++++++++++++++++++++++++++++++
'''


def center(toplevel):
    toplevel.update_idletasks()
    w = toplevel.winfo_screenwidth()
    h = toplevel.winfo_screenheight()
    size = tuple(int(_) for _ in toplevel.geometry().split('+')[0].split('x'))
    x = w / 2 - size[0] / 2
    y = h / 2 - size[1] / 2
    toplevel.geometry("%dx%d+%d+%d" % (size + (x, y)))


try:
    with open('conf') as f:
        '''
        ==========================================

        Main Window

        ==========================================
        '''
        root = Tk()
        root.title('Print manager software - Isfahan university of technology IT center')
        root.resizable(False, False)


        '''
        ==========================================

        Authentication variables

        ==========================================
        '''
        username = StringVar()
        password = StringVar()


        '''
        ==========================================

        Notebook

        ==========================================
        '''
        nb = ttk.Notebook(root)
        nb.grid(row=0, column=0)


        '''
        ==========================================

        Tab to be used for adding new entries

        ==========================================
        '''
        addNewFrame = ttk.Frame(nb)
        addNewFrame.grid(row=0, column=1)


        '''
        ------------------------------------------

        Connect section

        ------------------------------------------
        '''
        connectLF = ttk.Labelframe(addNewFrame, text='Connect', width=200, height=50)
        connectLF.grid(row=0, column=1, padx=(0, 5), pady=5, sticky='news')
        connectLF.columnconfigure(0, weight=1)
        ttk.Label(connectLF, text='Connection type:').grid(
            row=0, column=0, padx=5, pady=(0, 5), sticky='w')
        v = StringVar()
        v.set('default')
        ip = StringVar()
        domain = StringVar()
        rb = ttk.Radiobutton(connectLF, text='Connect to new server', variable=v, value='new',
                        command=lambda: [toggleEntry(v, e1, ip, 0), toggleEntry(v, e2, domain, 2)])
        rb.grid(row=1, column=0, sticky='w', padx=5)
        rb2 = ttk.Radiobutton(connectLF, text='Connect to default server', variable=v, value='default',
                        command=lambda: [toggleEntry(v, e1, ip, 0), toggleEntry(v, e2, domain, 2)])
        rb2.grid(row=2, column=0, sticky='w', padx=5)
        rb2.bind('<ButtonRelease>', lambda ev: bc.focus())
        ttk.Label(connectLF, text='IP address:').grid(
            row=3, column=0, padx=5, pady=5, sticky='w')
        ttk.Label(connectLF, text='Domain name:').grid(
            row=4, column=0, padx=5, pady=5, sticky='w')
        e1 = ttk.Entry(connectLF, textvariable=ip)
        e1.grid(row=3, column=0, columnspan=2, sticky='we', padx=(100, 5), pady=5)
        e2 = ttk.Entry(connectLF, textvariable=domain)
        e2.grid(row=4, column=0, columnspan=2, sticky='we', padx=(100, 5), pady=5)
        toggleEntry(v, e1, ip, 0)
        toggleEntry(v, e2, domain, 2)
        bc = ttk.Button(connectLF, text='Connect', command=showAuthenticate)
        bc.grid(row=5, column=0, columnspan=3, sticky='news', padx=5, pady=5)
        bc.focus()
        connectLabel = ttk.Label(
            connectLF, text='You are not connected to any server.', foreground='red')
        connectLabel.grid(row=6, column=0, columnspan=3, padx=5, pady=5)

        '''
        ------------------------------------------

        Quota section

        ------------------------------------------
        '''
        quotaLF = ttk.Labelframe(addNewFrame, text='Credits', width=200, height=350)
        quotaLF.grid(row=2, column=1, padx=(0, 5), pady=5, sticky='news')
        quotaLF.columnconfigure(2, weight=1)
        credit = StringVar()
        maxCredit = StringVar()
        minCredit = StringVar()
        sheetCredit = StringVar()
        sheetMax = StringVar()
        discount = StringVar()
        credit.set(0)
        maxCredit.set(1000000)
        minCredit.set(0)
        sheetCredit.set(0)
        sheetMax.set(1000)
        discount.set(0)
        ttk.Label(quotaLF, text='rials').grid(
            row=0, column=2, padx=5, pady=5, sticky='w')
        ttk.Label(quotaLF, text='rials').grid(
            row=1, column=2, padx=5, pady=5, sticky='w')
        ttk.Label(quotaLF, text='rials').grid(
            row=2, column=2, padx=5, pady=5, sticky='w')
        ttk.Label(quotaLF, text='sheets').grid(
            row=3, column=2, padx=5, pady=5, sticky='w')
        ttk.Label(quotaLF, text='sheets').grid(
            row=4, column=2, padx=5, pady=5, sticky='w')
        ttk.Label(quotaLF, text='percent').grid(
            row=5, column=2, padx=5, pady=(5, 10), sticky='w')
        ttk.Entry(quotaLF, textvariable=credit).grid(row=0, column=1, padx=5, pady=5)
        ttk.Entry(quotaLF, textvariable=maxCredit).grid(
            row=1, column=1, padx=5, pady=5)
        ttk.Entry(quotaLF, textvariable=minCredit).grid(
            row=2, column=1, padx=5, pady=5)
        ttk.Entry(quotaLF, textvariable=sheetCredit).grid(
            row=3, column=1, padx=5, pady=5)
        ttk.Entry(quotaLF, textvariable=sheetMax).grid(row=4, column=1, padx=5, pady=5)
        ttk.Entry(quotaLF, textvariable=discount).grid(
            row=5, column=1, padx=5, pady=(5, 10))
        ttk.Label(quotaLF, text='Credit:').grid(
            row=0, column=0, padx=5, pady=5, sticky='w')
        ttk.Label(quotaLF, text='Max permitted credit:').grid(
            row=1, column=0, padx=5, pady=5, sticky='w')
        ttk.Label(quotaLF, text='Min permitted credit:').grid(
            row=2, column=0, padx=5, pady=5, sticky='w')
        ttk.Label(quotaLF, text='Sheet credit:').grid(
            row=3, column=0, padx=5, pady=5, sticky='w')
        ttk.Label(quotaLF, text='Max permitted sheet credit:').grid(
            row=4, column=0, padx=5, pady=5, sticky='w')
        ttk.Label(quotaLF, text='Discount:').grid(
            row=5, column=0, padx=5, pady=(5, 10), sticky='w')
        quotaLF.state(['disabled'])
        for widget in quotaLF.winfo_children():
            widget.state(['disabled'])


        '''
        ------------------------------------------

        Result tree section

        ------------------------------------------
        '''
        treeLF = ttk.Labelframe(addNewFrame, text='Search results')
        treeLF.grid(row=0, column=0, rowspan=3, padx=5, pady=5, sticky='news')
        treeLF.rowconfigure(0, weight=1)
        tree = ttk.Treeview(treeLF, show='tree')
        tree.grid(row=0, column=0, columnspan=2, pady=(5, 0), sticky='nws')
        s = ttk.Scrollbar(treeLF, orient=VERTICAL, command=tree.yview)
        s.grid(row=0, column=2, pady=(5, 0), sticky='ns')
        tree.configure(yscrollcommand=s.set)
        tree.tag_configure('green', background='#88CC22')
        tree.tag_configure('white', background='white')
        tree.tag_configure('yellow', background='#CCEE66')
        b = ttk.Button(treeLF, text='Select', command=lambda: toggleColor(
            'complex', 1, tree.selection()))
        b.grid(row=1, column=0, sticky='news', padx=5, pady=5)
        b2 = ttk.Button(treeLF, text='Deselect', command=lambda: toggleColor(
            'complex', 0, tree.selection()))
        b2.grid(row=1, column=1, sticky='news', padx=5, pady=5)
        treeLF.state(['disabled'])
        for widget in treeLF.winfo_children():
            widget.state(['disabled'])


        '''
        ------------------------------------------

        Add to database button

        ------------------------------------------
        '''
        addB = ttk.Button(addNewFrame, text='Add selected entries', command=addToDB)
        addB.grid(row=3, column=1, sticky='news', padx=(0, 5), pady=(0, 5))
        addB.bind('<Return>', addToDB)
        addB.state(['disabled'])


        '''
        ==========================================

        Menubar

        ==========================================
        '''
        root.option_add('*tearOff', FALSE)
        menubar = Menu(root)
        root.configure(menu=menubar)
        menu1 = Menu(menubar)
        menubar.add_cascade(menu=menu1, label='menu')
        menu1.add_command(label='settings', command=showSettings)
        menu1.add_command(
            label='about',
            command= lambda: messagebox.showinfo(
                title='About',
                message='<> with ♥ by Mohammad Kermani at Linux lab.\n \
                        Copyright 2016, IUT.'
        ))

        '''
        ==========================================
        Tab to be used for updating existing
        entries
        ==========================================
        '''
        updateFrame = ttk.Frame(nb)
        updateFrame.grid(row=0, column=0)
        updateFrame.columnconfigure(1, weight=1)


        '''
        ------------------------------------------
        Result tree section 2
        ------------------------------------------
        '''
        treeLF2 = ttk.Labelframe(updateFrame, text='Search result')
        treeLF2.grid(row=0, column=0, rowspan=3, padx=5, pady=5, sticky='news')
        treeLF2.rowconfigure(0, weight=1)
        tree2 = ttk.Treeview(treeLF2, show='tree')
        tree2.grid(row=0, column=0, columnspan=2, pady=(5, 0), sticky='nws')
        tree2.tag_configure('green', background='#88CC22')
        tree2.tag_configure('white', background='white')
        s2 = ttk.Scrollbar(treeLF2, orient=VERTICAL, command=tree2.yview)
        s2.grid(row=0, column=2, pady=(5, 0), sticky='ns')
        tree2.configure(yscrollcommand=s2.set)
        # tree.tag_configure('green',background='#88CC22')
        # tree.tag_configure('white',background='white')
        # tree.tag_configure('yellow',background='#CCEE66')
        b21 = ttk.Button(treeLF2, text='Select', command=lambda: toggleColor(
            'simple', 1, tree2.selection()))
        b21.grid(row=2, column=0, sticky='news', padx=5, pady=5)
        b22 = ttk.Button(treeLF2, text='Deselect',
                         command=lambda: toggleColor('simple', 0, tree2.selection()))
        b22.grid(row=2, column=1, sticky='news', padx=5, pady=5)
        treeLF2.state(['disabled'])
        for widget in treeLF2.winfo_children():
            widget.state(['disabled'])


        '''
        ------------------------------------------
        Select entries section
        ------------------------------------------
        '''
        selectEntriesLF = ttk.Labelframe(
            updateFrame, text='Select Entries', width=200, height=50)
        selectEntriesLF.grid(row=0, column=1, padx=(0, 5), pady=5, sticky='news')
        selectEntriesLF.columnconfigure(1, weight=1)
        # b2.bind('<Return>',lambda ev: connect(ip,e))
        ttk.Label(selectEntriesLF, text='Grade:').grid(
            row=0, column=0, padx=(50, 5), pady=5, sticky='w')
        ttk.Label(selectEntriesLF, text='Department:').grid(
            row=1, column=0, padx=(50, 5), pady=5, sticky='w')
        ttk.Label(selectEntriesLF, text='Entrance year:').grid(
            row=2, column=0, padx=(50, 5), pady=5, sticky='w')
        grade = StringVar()
        department = StringVar()
        entranceYear = StringVar()
        grades = ['all', 'bs', 'ms', 'phd']
        departments = ['all']
        entranceYears = ['all']
        grade.set(grades[0])
        department.set(departments[0])
        entranceYear.set(entranceYears[0])
        ttk.Combobox(selectEntriesLF, textvariable=grade, values=grades, state='readonly').grid(
            row=0, column=1, padx=(5, 50), pady=5, sticky='we')
        ttk.Combobox(selectEntriesLF, textvariable=department, values=departments,
                     state='readonly').grid(row=1, column=1, padx=(5, 50), pady=5, sticky='we')
        ttk.Combobox(selectEntriesLF, textvariable=entranceYear, values=entranceYears).grid(
            row=2, column=1, padx=(5, 50), pady=5, sticky='we')
        b2 = ttk.Button(selectEntriesLF, text='Fetch',
                        command=lambda: fetchFromDB(grade, department, entranceYear))
        b2.grid(row=3, column=0, columnspan=2, sticky='ew', padx=5, pady=5)
        selectLabel = ttk.Label(
            selectEntriesLF, text='You have not fetched any entries.', foreground='red')
        selectLabel.grid(row=4, column=0, columnspan=3, padx=5, pady=5)


        '''
        ------------------------------------------
        Quota section 2
        ------------------------------------------
        '''
        quotaLF2 = ttk.Labelframe(updateFrame, text='Credits', width=200, height=350)
        quotaLF2.grid(row=2, column=1, padx=(0, 5), pady=5, sticky='news')
        quotaLF2.columnconfigure(2, weight=1)
        credit2 = StringVar()
        maxCredit2 = StringVar()
        minCredit2 = StringVar()
        sheetCredit2 = StringVar()
        sheetMax2 = StringVar()
        discount2 = StringVar()
        ttk.Label(quotaLF2, text='rials').grid(
            row=0, column=2, padx=5, pady=5, sticky='w')
        ttk.Label(quotaLF2, text='rials').grid(
            row=1, column=2, padx=5, pady=5, sticky='w')
        ttk.Label(quotaLF2, text='rials').grid(
            row=2, column=2, padx=5, pady=5, sticky='w')
        ttk.Label(quotaLF2, text='sheets').grid(
            row=3, column=2, padx=5, pady=5, sticky='w')
        ttk.Label(quotaLF2, text='sheets').grid(
            row=4, column=2, padx=5, pady=5, sticky='w')
        ttk.Label(quotaLF2, text='percent').grid(
            row=5, column=2, padx=5, pady=(5, 10), sticky='w')
        ttk.Entry(quotaLF2, textvariable=credit2).grid(row=0, column=1, padx=5, pady=5)
        ttk.Entry(quotaLF2, textvariable=maxCredit2).grid(
            row=1, column=1, padx=5, pady=5)
        ttk.Entry(quotaLF2, textvariable=minCredit2).grid(
            row=2, column=1, padx=5, pady=5)
        ttk.Entry(quotaLF2, textvariable=sheetCredit2).grid(
            row=3, column=1, padx=5, pady=5)
        ttk.Entry(quotaLF2, textvariable=sheetMax2).grid(
            row=4, column=1, padx=5, pady=5)
        ttk.Entry(quotaLF2, textvariable=discount2).grid(
            row=5, column=1, padx=5, pady=(5, 10))
        ttk.Label(quotaLF2, text='Credit:').grid(
            row=0, column=0, padx=5, pady=5, sticky='w')
        ttk.Label(quotaLF2, text='Max permitted credit:').grid(
            row=1, column=0, padx=5, pady=5, sticky='w')
        ttk.Label(quotaLF2, text='Min permitted credit:').grid(
            row=2, column=0, padx=5, pady=5, sticky='w')
        ttk.Label(quotaLF2, text='Sheet credit:').grid(
            row=3, column=0, padx=5, pady=5, sticky='w')
        ttk.Label(quotaLF2, text='Max permitted sheet credit:').grid(
            row=4, column=0, padx=5, pady=5, sticky='w')
        ttk.Label(quotaLF2, text='Discount:').grid(
            row=5, column=0, padx=5, pady=(5, 10), sticky='w')
        quotaLF2.state(['disabled'])
        for widget in quotaLF2.winfo_children():
            widget.state(['disabled'])


        '''
        ------------------------------------------
        Update database button
        ------------------------------------------
        '''
        updateB = ttk.Button(
            updateFrame, text='Update selected entries', command=updateDB)
        updateB.grid(row=3, column=1, sticky='news', padx=(0, 5), pady=(0, 5))
        updateB.state(['disabled'])
        # addB.bind('<Return>',addToDB)



        '''
        ------------------------------------------

        Adding frames to notebook

        ------------------------------------------
        '''
        nb.add(addNewFrame, text=' Add new users ')
        nb.add(updateFrame, text=' Update existing users ')


        '''
        ==========================================

        Opening file and checking whether it is
        first time the program is run

        ==========================================
        '''
        with open('conf') as f:
            configurations = f.readlines()
            configurations[0] = configurations[0].strip()
            configurations[1] = configurations[1].strip()
            if(configurations[1] == '1'):
                configurations[1] = '0'
                updateConf(configurations)
                flag = messagebox.askyesno(
                    message='Default server IP address is set to 127.0.0.1. Do you want to change it?', icon='question', title='Default IP modification')
                if flag:
                    setDefaultIP(configurations)
                else:
                    flag2 = messagebox.askyesno(
                        message='Default server domain address is set to sub.domain. Do you want to change it?', icon='question', title='Default domain modification')
                    if flag2:
                        setDefaultDomain(configurations)

        center(root)
        root.bind_all('<Return>', lambda ev: ev.widget.invoke() if hasattr(ev.widget, 'invoke') else False)
        root.mainloop()
except EnvironmentError:
    messagebox.showerror(title="Missed configurations file",
                        message="No configurations file found. Exiting.")
    sys.exit()
