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
        rating int,
        solved int
    );
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS problems(
        ProblemID varchar(10) PRIMARY KEY,
        name varchar(255),
        rating int,
        points int,
        link varchar(255),
        solved int
    );
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS tags(
        ProblemID varchar(10),
        tags varchar(255)
    );
''')

cursor1 = sqlite3.connect('all_problems.db', check_same_thread=False)

cursor1.execute('''
    CREATE TABLE IF NOT EXISTS problems(
        ProblemID varchar(10) PRIMARY KEY,
        problemsetName varchar(255),
        name varchar(255),
        rating int,
        points int,
        link varchar(255)
    );
''')

cursor1.execute('''
    CREATE TABLE IF NOT EXISTS tags(
        ProblemID varchar(10),
        tags varchar(255)
    );
''')

@app.route("/all_problems", methods = ['GET','POST'])
def all_problems():
    print(request.method)
    print(1)
    url = "https://codeforces.com/api/problemset.problems?"
    print(url)
    temp = requests.get(url)
    obj = json.loads(temp.text)
    problems = []
    for problem in obj['result']['problems']:
        problems.append(problem)
    pdata = []    

    print(len(problems))

    url1 = "https://codeforces.com/problemset/problem/"

    for data in problems:
        block = []
        block.append(data['name'])
        if 'rating' not in data:
            block.append(0)
        else:
            block.append(data['rating'])
        if 'points' not in data:
            block.append(0)
        else:
            block.append(data['points'])
        block.append(data['tags'])
        code = ""
        if 'contestId' in data and 'index' in data:
            link = url1 + str(data['contestId']) + "/" + str(data['index'])
            block.append(link)
        pdata.append(block)

    return render_template('problem.html', pdata = pdata)

@app.route("/new_here")
def new_here():
    print("new here")
    return render_template('add_handle.html')

@app.route("/add_handle", methods = ['GET','POST'])
def add():
    print("adding")
    if request.method == 'POST':
        handle = (request.form['handle'])
        url = "https://codeforces.com/api/user.info?handles=%s" %handle
        print(url)
        temp = requests.get(url)
        obj = json.loads(temp.text)
        error = "OK"
        # print(obj)
        if obj['status'] != "OK":
            error = "Error : Account not found"
        else:
            handle = handle.replace("'", "/'")
            qry = "select * from handles where handle = '%s'" %handle
            tmp = cursor.execute(qry)
            if tmp.fetchone() != None:
                error = "Account is already registered"
            else:
                data = obj['result'][0]
                print(data)
                if 'country' not in data:
                    error = "Add Country = India"
                elif data['country'] != "India":
                    error = "Set Country = India in codeforces Profile"
                elif 'organization' not in data:
                    error = "Add Organization = IIT Indore"
                elif data['organization'] != "IIT Indore": 
                    error = "Set Organization = IIT Indore in Codeforces Profile"
                else:
                    qry = "insert into handles values ('%s',%d,0)" %(handle, data['rating'])
                    print(qry)
                    cursor.execute(qry)
                    print(1)
                    cursor.commit()
        print(error)
        return render_template('add_handle.html', error=error)
    return render_template('home.html')

@app.route("/home")
@app.route("/")
@app.route("/ranklist", methods = ['GET', 'POST'])
def show_handles():
    tmp = cursor.execute('''select * from handles''')
    ranklist = []
    while True:
        data = tmp.fetchone()
        if data == None:
            break
        print(data)
        block = []
        block.append(data[0])
        block.append(data[1])
        block.append(data[2])
        link = "https://codeforces.com/profile/" + data[0]
        block.append(link)
        ranklist.append(block)
    return render_template('home.html', ranklist = ranklist)

@app.route("/add_problem")
def new_problem():
    print("new here")
    return render_template('add_problems.html')

@app.route("/add_problem", methods = ['GET','POST'])
def add_problem():
    print("adding")
    if request.method == 'POST':
        name = (request.form['problemName'])
        error = "OK"
        name = name.replace("'", "/'")
        qry = "select * from problems where name = '%s'" %name
        tmp = cursor1.execute(qry)
        data = tmp.fetchone()
        if data == None:
            error = "Question Not Found"
        else:
            qry = "insert into problems values ('%s','%s',%d,%d,'%s',0)" %(data[0], data[2], data[3], data[4], data[5])
            print(qry)
            cursor.execute(qry)
            qry1 = "select * from tags where problemID = '%s'"%(data[0])
            tmp = cursor1.execute(qry1)
            while True:
                data = tmp.fetchone()
                if data == None:
                    break
                qry2 = "insert into tags values ('%s','%s')"%(data[0], data[1])
                print(qry2)
                cursor.execute(qry2)
            print(1)
            cursor.commit()
        print(error)
        return render_template('add_handle.html', error=error)
    return render_template('home.html')

@app.route("/problems", methods = ['GET', 'POST'])
def show_problems():
    tmp = cursor.execute('''select * from problems''')
    pdata = []
    while True:
        data = tmp.fetchone()
        block = []
        if data == None:
            break
        print(data)
        block.append(data[1])
        block.append(data[2])
        block.append(data[3])
        tags = []
        qry = "select tags from tags where ProblemID = '%s'" %data[0]
        tmp1 = cursor.execute(qry)
        while True:
            tag = tmp1.fetchone()
            if tag == None:
                break
            tags.append(tag[0])
        block.append(tags)
        block.append(data[4])
        block.append(data[5])
        pdata.append(block)
    return render_template('problems.html', pdata = pdata)

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
    app.secret_key = 'sec key'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run(debug=True)
