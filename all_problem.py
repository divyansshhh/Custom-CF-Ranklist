import requests,schedule,sqlite3,json
from operator import itemgetter
from flask import Flask,render_template,session,request,redirect,url_for,flash
import os
import multiprocessing
import time

app = Flask(__name__)

cursor = sqlite3.connect('all_problems.db',check_same_thread=False)

cursor.execute('''
    CREATE TABLE IF NOT EXISTS problems(
        ProblemID varchar(10) PRIMARY KEY,
        problemsetName varchar(255),
        name varchar(255),
        rating int,
        points int,
        link varchar(255)
    );
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS tags(
        ProblemID varchar(10),
        tags varchar(255)
    );
''')

@app.route("/all_problems", methods = ['GET','POST'])
def home():
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

    url1 = "https://codeforces.com/problemset/problem/"

    for data in problems:
        qry1 = "insert into problems values ("
        qry2 = "insert into tags values ("
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
            code = str(data['contestId']) + str(data['index'])
            qry1 = qry1 + "'" + code + "'"
            qry2 = qry2 + "'" + code + "'"
        pdata.append(block)
        name = block[0]
        name = name.replace("'", "''")
        qry1 = qry1 + ",'" + "main" + "','"+ name + "'," + str(block[1]) + "," + str(block[2]) + ",'" + block[4] + "')"
        cursor.execute(qry1)
        for tag in block[3]:
            qry3 = qry2 + ",'" + tag +"')"
            cursor.execute(qry3)   

    qry = "select * from problems"
    tmp = cursor.execute(qry)

    for i in range(0, 10):
        problem = tmp.fetchone()
        print(problem)
    
    cursor.commit()

    return render_template('problem.html', pdata = pdata)

if __name__ == "__main__":
    app.secret_key = 'sec key'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run(debug=True)
