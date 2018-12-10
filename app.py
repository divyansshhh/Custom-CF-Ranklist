import requests,schedule,sqlite3,json
from operator import itemgetter
from flask import Flask,render_template,session,request,redirect,url_for,flash
import os
import multiprocessing
import time

app = Flask(__name__)
cursor = sqlite3.connect('ranklist.db',check_same_thread=False)
cursor2 = sqlite3.connect('ranklist.db',check_same_thread=False)
cursor.execute('''
    CREATE TABLE IF NOT EXISTS handles(
        handle varchar(100) PRIMARY KEY,
        solved int
    );
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS problems(
        name varchar(100) PRIMARY KEY,
        link varchar(1000),
        solved int,
        level varchar(2)
    );
''')

@app.route("/new_here")
def new_here():
    return render_template('add_handle.html')

@app.route("/add_handle",methods = ['GET','POST'])
def add():
    if request.method == 'POST':
        url = "https://codeforces.com/api/user.status?handle=%s" %(request.form['handle'])
        req = requests.get(url)
        jobj = json.loads(req.text)
        error = False
        duplicate = False
        if jobj['status'] != "OK":
            error = True
        else:
            qry = "select * from handles where handle = '%s'" %(request.form['handle'])
            tmp =  cursor.execute(qry)
            if tmp.fetchone() == None:
                cursor.execute('''insert into handles values (?,?)''',(request.form['handle'],0))
            else:
                duplicate = True
            cursor.commit()
        return render_template('add_handle.html',error=error,duplicate=duplicate)
    return home()

def update():
    print("updating")
    pset = []
    tmp3 = cursor.execute('''Select * from problems''')
    while True:
        pname = tmp3.fetchone()
        if pname == None:
            break
        pset.append(pname[0])
    #print(pset)
    tmp = cursor.execute('''SELECT * from handles''')
    while True: 
        handle = tmp.fetchone()
        if handle == None:
            break
        #print("updating %s" %(handle[0]))
        cursor2.execute('''update handles set solved = 0 where handle = '%s' '''%(handle[0]))

    tmp = cursor.execute('''Select * from problems''')
    while True:
        problem = tmp.fetchone()
        if problem == None:
            break
        cursor2.execute('''update problems set solved = 0 where name = '%s'; ''' %(problem[0]))

    tmp = cursor.execute('''SELECT handle from handles''')
    while True:
        handle = tmp.fetchone()
        probstatus = dict()
        if handle == None:
            break
        try:
            url = "https://codeforces.com/api/user.status?handle=%s" %(handle[0])
            sub1 = requests.get(url)
            sub = json.loads(sub1.text)
            if sub['status'] != "OK":
                continue
            for stat in sub['result']:
                if stat['verdict'] == "OK":
                    probstatus[stat['problem']['name']] = True
            
            for x in probstatus:
                if probstatus[x] == True and x in pset:
                    #print(x)
                    qry = '''select * from problems where name = "%s" ''' %(x)
                    tmp2 = cursor2.execute(qry)
                    if tmp2.fetchone() != None:
                        try:
                            qry = '''update handles set solved = solved+1 where handle = "%s" ''' %(handle[0])
                            cursor2.execute(qry)
                        except:
                            print("not possible here")
                        try:
                            qry = '''update problems set solved = solved+1 where name = "%s" ''' %(x)
                            cursor2.execute(qry)
                        except:
                            print("not possible here")
            print("done %s" %(handle))
        except:
            print("skipping %s" %(handle))

    cursor.commit()
    cursor2.commit()
    print("done update")
    # return render_template('home.html')

def test():
    print("hi")

@app.route("/")
def home():
    ranks = []
    tmp = cursor.execute('''select * from handles order by solved desc''')
    while True:
        handle = tmp.fetchone()
        if handle==None:
            break
        ranks.append((handle[0],handle[1]))
    return render_template('home.html',ranklist=ranks)

@app.route("/problems")
def problems():
    psolves = []
    tmp = cursor.execute('''select * from problems order by solved desc''')
    while True:
        problem = tmp.fetchone()
        if problem == None:
            break
        psolves.append((problem))
    return render_template('problems.html',pdata = psolves)
#add dynamic search

def work():
    try:
        update()
    except:
        print("update not possible")

schedule.every(10).minutes.do(work)

def run_loop():
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    p = multiprocessing.Process(target=run_loop)
    p.start()
    app.run(port=os.environ.get("PORT",5000), host='0.0.0.0')