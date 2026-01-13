import sqlite3
import random
import urllib.request
import json
from flask import Flask, render_template, send_file
from flask import session, request, redirect

app = Flask(__name__)
app.secret_key = 'supersecre'

DB_FILE = "data.db"

db = sqlite3.connect(DB_FILE) #open if file exists, otherwise create
c = db.cursor()

c.execute("CREATE TABLE IF NOT EXISTS users(username TEXT, password TEXT, friends TEXT, friend_reqs TEXT, pfp TEXT, invite_perms TEXT);")
c.execute("CREATE TABLE IF NOT EXISTS tasks(name TEXT, id TEXT, description TEXT, deadline TEXT, status TEXT, category TEXT, users TEXT, visibility TEXT, join_perms TEXT)")

#join perms can be 'open', 'closed'
#invite_perms can be 'open', 'closed'
#visibility can be 'public', 'private'

@app.route('/')
def homepage():
    return render_template('home.html')

if __name__=='__main__':
    app.debug = True
    app.run()
