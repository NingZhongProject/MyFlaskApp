import logging
from logging.handlers import RotatingFileHandler

import hashlib

import json

from flask import Flask, request, jsonify, render_template

from flask.ext.pymongo import PyMongo
from pymongo import MongoClient

from datetime import datetime

app = Flask(__name__)
mongo = PyMongo(app)

@app.route('/hello')
def hello():
    return "hello!" 

@app.route('/idx')
def idx():
    # Render template
    return render_template('index.html')

@app.route('/home_page')
def home_page():
    online_users = mongo.db.users.find({'online': True})
    return render_template('index.html',
        online_users=online_users)

@app.route('/post', methods = ['POST'])
def post():
    # Get the parsed contents of the form data
    jsonObj = request.get_json()
    print(jsonObj)

    #connecting to mongoDB
    client = MongoClient()
    db = client.test #database name.

    uslist = jsonObj['users']
    for uVal in uslist:
        oriCheckSum = uVal['md5checksum']
        print("original:" + oriCheckSum)
        del uVal['md5checksum']
        newMD5 = hashlib.md5(str(uVal)).hexdigest()
        print(newMD5)
        print(uVal)
        print("inserting one ...")
        result = db.userinfo.insert_one(uVal)
        print(result)

    # Render template
    app.logger.error('about to return')
    #return jsonify(results=jsonObj) 
    return("done post.")

@app.route('/get', methods = ['GET'])
def get():
    uid = request.args.get('uid')
    date = request.args.get('date')
    print(uid)
    print(date)
    print("====")

    #connecting to mongoDB
    client = MongoClient()
    db = client.test #database name.

    qDate =  datetime.strptime(date, "%Y-%m-%d").date()
    print(qDate)
    print("====---")
    count = 0

    cursor = db.userinfo.find()

    for itemc in cursor:
        currUID = itemc['uid']
        print(currUID)
        currDateT = itemc['date']
        currD = datetime.strptime(currDateT, "%Y-%m-%dT%H:%M:%S.%f").date()
        print(currD)
        if qDate == currD and currUID == uid:
            count += 1
            print("cnt=" + str(count))

    cursor.close()

    return(str(count))


if __name__ == "__main__":
    handler = RotatingFileHandler('foo.log', maxBytes=10000, backupCount=1)
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)
    app.run(port=8080, debug=True)
