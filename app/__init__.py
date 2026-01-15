# cerulean (Natalie Kieger, Michelle Chen, Maya Berchin)
# SoftDev pd 5
# P02: Makers Makin' It, Act I
# 2025-01-11
# Time spent:

from flask import Flask, render_template, send_file
from flask import session, request, redirect, url_for
from datetime import datetime
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

edit_task = ""

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

    all_tasks = data.get_all_tasks(session['username'])
    
    for task in all_tasks:
        if f'join {task}' in request.form:
            data.add_user(task, session['username'])
        elif f'leave {task}' in request.form:
            data.leave_task(task, session['username'])
        elif f'edit {task}' in request.form:
            global edit_task
            edit_task = task
            return redirect(url_for("edit"))

    # list of tasks done
    tasks_done_unsorted = [task for task in all_tasks if data.get_task_status(task).lower() == "done"]
    tasks_done_sorted = sort_by_deadline(tasks_done_unsorted)
    tasks_done = [data.get_task_info(task) for task in tasks_done_sorted]

    # list of tasks in progress
    tasks_ip_unsorted = [task for task in all_tasks if data.get_task_status(task).lower() == "in progress"]
    tasks_ip_sorted = sort_by_deadline(tasks_ip_unsorted)
    tasks_ip = [data.get_task_info(task) for task in tasks_ip_sorted]

    # list of tasks not started
    tasks_ns_unsorted = [task for task in all_tasks if data.get_task_status(task).lower() == "not started"]
    tasks_ns_sorted = sort_by_deadline(tasks_ns_unsorted)
    tasks_ns = [data.get_task_info(task) for task in tasks_ns_sorted]

    # tasks friends are up to
    friend_task_ids = data.get_friend_tasks(session['username'])
    friend_tasks = [data.get_task_info(task) for task in friend_task_ids]

    return render_template("home.html", user=session['username'], tasks_done=tasks_done, tasks_ip=tasks_ip, tasks_ns=tasks_ns, friend_tasks=friend_tasks)


# helper for home
def sort_by_deadline(task_lst):
    s_list = sorted(task_lst, key=lambda item: datetime.strptime(data.get_task_deadline(item), '%Y-%m-%d'))
    return s_list


@app.route("/edit", methods=["GET", "POST"])
def edit():
    global edit_task
    to_edit = edit_task
    edit_task = ""
    task_info = data.get_task_info(to_edit)
    return render_template("edit.html", task_name=task_info[0])


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/calendar', methods=["GET", "POST"])
def calendar():
    if not 'username' in session:
        return redirect(url_for('login'))
    user_tasks = data.get_all_tasks(session['username'])
    tasks = []
    for task in user_tasks:
        tasks.append(data.get_task_name(task))
    if request.method == 'POST' and (not request.form.get('title') in tasks):
        task = request.form.get('title')
        description = request.form.get('description')
        deadline = request.form.get('deadline')
        cat = request.form.get('category')
        perms = request.form.get('join_perms')
        vis = request.form.get('visibility')
        data.create_task(task, description, deadline, cat, "not started", vis, perms, session['username'])
    #send tasks to js
    return render_template('calendar.html')

@app.route('/gettasks', methods=['POST'])
def get_tasks():
    tasks = data.get_all_tasks(session['username'])
    #print(tasks)
    task_list = []
    for task in tasks:
        #format: deadline, name, status
        if not [data.get_task_deadline(task), data.get_task_name(task), data.get_task_status(task)] in task_list:
            task_list.append([data.get_task_deadline(task), data.get_task_name(task), data.get_task_status(task)])
    print(task_list)
    return task_list


@app.route('/profile', methods=["GET", "POST"])
def profile():

    # redirect to login if not logged in
    if not 'username' in session:
        return redirect(url_for('login'))

    # set up vars for settings changes
    invite_options = ["no one", "friends", "everyone"]
    fr_list = data.get_friends(session['username'])
    if len(fr_list) == 0:
        fr_list = ['None yet!']
    fr_reqs = data.get_friend_reqs(session['username'])
    perms = data.get_invite_perms(session['username'])
    pfp_dict = {"happy_cat": "https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fi.pinimg.com%2Foriginals%2F00%2Ff6%2Fe0%2F00f6e04b05b731670e13a1347c32d64c.jpg&f=1&nofb=1&ipt=0d2b6923a92fe59721e0029d8c45198857c993b9fb72ed3a396b9d75a3b1b515",
                "toast_cat": "https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fi.pinimg.com%2Foriginals%2Fdf%2Fb1%2F76%2Fdfb176eedc5fcae081e2ad767a52ed01.jpg&f=1&nofb=1&ipt=5ae127651458ee89055e8f474d668acb6a99346a84d9201d0a5035a3f069b840",
                "hungry_cat": "https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fi.pinimg.com%2Foriginals%2F0f%2F5b%2F17%2F0f5b1779b42e7c161182cb01f2282039.jpg&f=1&nofb=1&ipt=c61418d2fa1866be7fc04661862085b45006d524694d4caf10f8d63862e1505c",
                "sad_cat": "https://i.pinimg.com/736x/46/93/da/4693dae1401e7ab161a57817d37251f8.jpg",
                "loafing_cat": "https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fi.pinimg.com%2Foriginals%2Fb0%2F7c%2F1c%2Fb07c1c7681bc75929166cdf84fe1cb48.jpg&f=1&nofb=1&ipt=50eefac65b2c9dd538044503780868d211ed88a5a781f5c051bf8d4a3e9bf443",
                "sleeping_cat": "https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fi.pinimg.com%2Foriginals%2F5d%2F9b%2F97%2F5d9b9763364a80ba2c041c38cdf0217a.jpg&f=1&nofb=1&ipt=5cb8c60608e2e1e64c45eeb03f49e9c822b974931f73d8ea305f05ef749a1151",
                "corporate_cat": "https://i.pinimg.com/736x/a2/6f/76/a26f7650b87a782f64e4589acce1cd69.jpg",
                "productive_cat": "https://i.pinimg.com/1200x/68/2d/fc/682dfc61e70730de01a2ca9c21212b06.jpg",
                "truce_cat": "https://i.pinimg.com/1200x/bb/11/15/bb11151a75a247a45225e571e2de5ae7.jpg",
                "annoyed_cat": "https://i.pinimg.com/736x/5d/8b/d9/5d8bd9e48344509fa6cc50caa057ce56.jpg"
              }
    pfp = data.get_pfp(session['username'])
    if pfp == 'None':
        pfp = "happy cat"

    # change password
    if 'password_form' in request.form:
        if request.form['old_pass'] == request.form['new_pass']:
            return render_template('profile.html', user=session['username'], msg="New password cannot be the same as the old password.", invite_options=invite_options, perms=perms, fr_reqs=fr_reqs, fr_list=fr_list, pfp_dict=pfp_dict, pfp=pfp)
        if data.auth(session['username'], request.form['old_pass']):
            data.change_password(session['username'], request.form['old_pass'], request.form['new_pass'])
            return render_template('profile.html', user=session['username'], msg="Password updated successfully!", invite_options=invite_options, perms=perms, fr_reqs=fr_reqs, fr_list=fr_list, pfp_dict=pfp_dict, pfp=pfp)
        else:
            return render_template('profile.html', user=session['username'], msg="Wrong password--password not changed.", invite_options=invite_options, perms=perms, fr_reqs=fr_reqs, fr_list=fr_list, pfp_dict=pfp_dict, pfp=pfp)

    # change pfp
    if 'pfp_form' in request.form:
        data.edit_pfp(session['username'], request.form.get('pfp'))
        pfp = request.form.get('pfp')
        return render_template('profile.html', user=session['username'], msg="Profile picture updated!", invite_options=invite_options, perms=perms, fr_reqs=fr_reqs, fr_list=fr_list, pfp_dict=pfp_dict, pfp=pfp)

    # change who can invite you to tasks
    if 'invite_form' in request.form:
        perms=request.form.get('invite')
        data.set_invite_perms(session['username'], perms)
        return render_template('profile.html', user=session['username'], msg="Settings updated!", invite_options=invite_options, perms=perms, fr_reqs=fr_reqs, fr_list=fr_list, pfp_dict=pfp_dict, pfp=pfp)

    # check if accepted a pending friend request
    for friend in fr_reqs:
        if f'accept {friend}' in request.form:
            data.accept_fr(friend, session['username'])
            return render_template('profile.html', user=session['username'], msg="Friend request accepted!", invite_options=invite_options, perms=perms, fr_reqs=fr_reqs, fr_list=fr_list, pfp_dict=pfp_dict, pfp=pfp)
        elif f'decline {friend}' in request.form:
            data.remove_fr(friend, session['username'])
            return render_template('profile.html', user=session['username'], msg="Friend request declined.", invite_options=invite_options, perms=perms, fr_reqs=fr_reqs, fr_list=fr_list, pfp_dict=pfp_dict, pfp=pfp)

    # send a friend request
    if 'fr_form' in request.form:
        user = request.form.get('fr_user')
        if data.user_exists(user):
            if user == session['username']:
                return render_template('profile.html', user=session['username'], msg="You can't send a friend request to yourself.", invite_options=invite_options, perms=perms, fr_reqs=fr_reqs, fr_list=fr_list, pfp_dict=pfp_dict, pfp=pfp)
            elif user in fr_list:
                return render_template('profile.html', user=session['username'], msg="User is already your friend!", invite_options=invite_options, perms=perms, fr_reqs=fr_reqs, fr_list=fr_list, pfp_dict=pfp_dict, pfp=pfp)
            elif user in fr_reqs:
                return render_template('profile.html', user=session['username'], msg="This user has already sent you a friend request!", invite_options=invite_options, perms=perms, fr_reqs=fr_reqs, fr_list=fr_list, pfp_dict=pfp_dict, pfp=pfp)
            elif session['username'] in data.get_friend_reqs(user):
                return render_template('profile.html', user=session['username'], msg="You have already sent a friend request to this user!", invite_options=invite_options, perms=perms, fr_reqs=fr_reqs, fr_list=fr_list, pfp_dict=pfp_dict, pfp=pfp)
            else:
                data.send_friend_req(session['username'], user)
                return render_template('profile.html', user=session['username'], msg="Friend request sent!", invite_options=invite_options, perms=perms, fr_reqs=fr_reqs, fr_list=fr_list, pfp_dict=pfp_dict, pfp=pfp)
        # username doesn't exist
        else:
            return render_template('profile.html', user=session['username'], msg="Username does not exist.", invite_options=invite_options, perms=perms, fr_reqs=fr_reqs, fr_list=fr_list, pfp_dict=pfp_dict, pfp=pfp)

    # nothing happened, just display page
    return render_template('profile.html', user=session['username'], msg="", invite_options=invite_options, perms=perms, fr_reqs=fr_reqs, fr_list=fr_list, pfp_dict=pfp_dict, pfp=pfp)


if __name__=='__main__':
    app.debug = True
    app.run()
