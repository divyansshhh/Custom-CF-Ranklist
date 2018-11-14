import json,requests,schedule,time
from operator import itemgetter
from flask import Flask,render_template,session,request,redirect,url_for,flash

app = Flask(__name__)

file = open("handles.txt","r")
prob_file = open("problems.txt","r")
problems = []
solved = []
names = []
ranklist = []
for problem in prob_file:
    problems.append(problem)
print(problems)

for handle in file:
    handle=handle[:-1]
    url = 'https://codeforces.com/api/user.status?handle=%s' %(handle)
    print(url)
    user_status = requests.get(url)
    user_status.raise_for_status()
    user_submissions = json.loads(user_status.text)
    if user_submissions['status'] != "OK":
        continue
    solved_count = 0
    for result in user_submissions['result']:
        if result['verdict'] == "OK":
                if result['problem']['name'] in problems:
                    solved_count = solved_count+1
    solved.append(solved_count)
    names.append(handle)
ranklist = list(zip(names,solved))
ranklist = sorted(ranklist,key = lambda x: x[1],reverse=True)
print(ranklist)

@app.route("/")
def home():
    return render_template('home.html',ranklist = ranklist)

if __name__ == "__main__":
    app.run(debug=True)