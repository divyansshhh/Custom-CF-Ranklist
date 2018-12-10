import requests, bs4
import os,subprocess
import sqlite3,schedule,time

cursor = sqlite3.connect('ranklist.db',check_same_thread=False)


def work():
    response = requests.get('http://iitiranklist.herokuapp.com/?')
    souped = bs4.BeautifulSoup(response.text)


    handle_elements = souped.select('#handle')
    handles = []


    for element in handle_elements:
        handles.append(element.getText())

    for handle in handles:
        qry = '''insert into handles values('%s',0)''' %(handle)
        try:
            cursor.execute(qry)
        except:
            print("%s already exists"%(handle))
        cursor.commit()
    print(handles)
    print(len(handles))

work()