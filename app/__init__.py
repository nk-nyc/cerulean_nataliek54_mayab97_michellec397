# cerulean (Natalie Kieger, Michelle Chen, Maya Berchin)
# SoftDev pd 5
# P02: Makers Makin' It, Act I
# 2025-01-11
# Time spent:

from flask import Flask, render_template, send_file
from flask import session, request, redirect, url_for
import random
import urllib.request
import json
import data
import sqlite3

# initialize tables
data.create_users_table()
data.create_tasks_table()

app = Flask(__name__)
app.secret_key = 'supersecre'


@app.route('/', methods=["GET", "POST"])
def login():

    # stored active session, take user to response page
    if 'username' in session:
        return redirect(url_for("home"))

    if 'username' in request.form:
        username = request.form.get('username').strip().lower()
        password = request.form.get('password').strip()

        # check if password is correct, if not then reload page
        if not data.auth(username, password):
            return render_template("login.html", error="Username or password is incorrect")

        # if password is correct redirect home
        session["username"] = username
        return redirect(url_for("home"))

    else:
        return render_template("login.html")


@app.route('/register', methods=["GET", "POST"])
def register():

    if request.method == 'POST':
        username = request.form.get('username').strip().lower()
        password = request.form.get('password').strip()

        # reload page if no username or password was entered
        if not username or not password:
            return render_template("register.html", error="No username or password inputted")

        # puts user into database unless if there's an error
        execute_register = data.register_user(username, password)
        if execute_register == "success":
            session['username'] = username
            return redirect(url_for("home"))
        else:
            return render_template("register.html", error = execute_register)
    return render_template("register.html")


@app.route("/home", methods=["GET", "POST"])
def home():
    if not 'username' in session:
        return redirect(url_for("login"))
    return render_template("home.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/calendar')
def calendar():
    if not 'username' in session:
        return redirect(url_for('login'))
    return render_template('calendar.html')

@app.route('/gettasks')
def get_tasks():
    db = sqlite3.connect('data.db')
    c = db.cursor()
    username = session['username']
    c.execute("SELECT FROM tasks * WHERE instr(users, {username})")
    data = c.fetchall()
    db.commit()
    db.close()
    return data


@app.route('/profile', methods=["GET", "POST"])
def profile():
    if not 'username' in session:
        return redirect(url_for('login'))
    
    if 'password_form' in request.form:
        if request.form['old_pass'] == request.form['new_pass']:
            return render_template('profile.html', user=session['username'], msg="New password cannot be the same as the old password.")
        if data.auth(session['username'], request.form['old_pass']):
            data.change_password(session['username'], request.form['old_pass'], request.form['new_pass'])
            return render_template('profile.html', user=session['username'], msg="Password updated successfully!")
        else:
            return render_template('profile.html', user=session['username'], msg="Wrong password--password not changed.")
    
    return render_template('profile.html', user=session['username'], msg="")


if __name__=='__main__':
    app.debug = True
    app.run()
