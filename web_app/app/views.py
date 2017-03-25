from app import app
import os
import pyrebase

config = {
    "apiKey": os.environ['APIKEY'],
    "databaseURL": "https://samasoa-4e15a.firebaseio.com",
    "storageBucket": "samasoa-4e15a.appspot.com",
    "serviceAccount": os.environ['SERVICEACCOUNT'],
    "authDomain": "samasoa-4e15a.firebaseapp.com" 
}  

firebase = pyrebase.initialize_app(config)

@app.route('/')
@app.route('/index')
def index():
    return "Hello, World!"

@app.route('/blah')
def testedddd():
    return "Blah"
