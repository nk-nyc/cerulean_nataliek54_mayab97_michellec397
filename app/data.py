# cerulean (Natalie Kieger, Michelle Chen, Maya Berchin)
# SoftDev pd 5
# P02: Makers Makin' It, Act I
# 2025-01-11
# Time spent: ~3 hrs

import sqlite3                      # enable control of an sqlite database
import hashlib                      # for consistent hashes
import secrets                      # to generate ids

DB_FILE="data.db"


# users INVITE PERMS (who can invite this user to join their tasks?): "no one", "friends", or "everyone"
# tasks VISIBILITY (who can see this task on their homepage?): "no one", "friends", "everyone"
# tasks JOIN PERMS (who can join this task without an invite?): "no one", "friends", "everyone"

#=============================MAKE=TABLES=============================#


# make the database tables we need if they don't already exist

# users
def create_users_table():

    contents =  """
                CREATE TABLE IF NOT EXISTS users (
                    username        TEXT    NOT NULL    PRIMARY KEY,
                    password        TEXT    NOT NULL,
                    friends         TEXT,
                    friend_reqs     TEXT,
                    pfp             TEXT,
                    invite_perms    TEXT    NOT NULL,
                    pending_invites TEXT
                )"""
    create_table(contents)

# tasks
def create_tasks_table():
    contents =  """
                CREATE TABLE IF NOT EXISTS tasks (
                    name            TEXT    NOT NULL,
                    id              TEXT    NOT NULL    PRIMARY KEY,
                    description     TEXT,
                    deadline        DATE    NOT NULL,
                    status          TEXT    NOT NULL,
                    category        TEXT    NOT NULL,
                    users           TEXT    NOT NULL,
                    visibility      TEXT    NOT NULL,
                    join_perms      TEXT    NOT NULL,
                    owner           TEXT    NOT NULL
                )"""
    create_table(contents)


#=============================USERS=============================#


#----------USERS-ACCESSORS----------#


# returns a list of usernames
def get_all_users():

    db = sqlite3.connect(DB_FILE)
    c = db.cursor()

    data = c.execute('SELECT username FROM users').fetchall()

    db.commit()
    db.close()

    return clean_list(data)


# returns a list of the user's friends
def get_friends(username):
    # friends stored by their usernames space separated
    friends = get_field("users", "username", username, "friends")
    friend_list = friends.split()
    return rm_empty(friend_list)


# returns a list of the friend requests a user may accept or reject
def get_friend_reqs(username):
    # friend reqa stored by usernames space separated
    friend_reqs = get_field("users", "username", username, "friend_reqs")
    friend_req_list = friend_reqs.split()
    return rm_empty(friend_req_list)


# maybe for a notification icon w num unresponded to fr_reqs?
def count_fr_reqs(username):
    fr_reqs = get_friend_reqs(username)
    fr_list =fr_reqs.split()
    return len(rm_empty(fr_list))


def get_pfp(username):
    link = get_field("users", "username", username, "pfp")
    # handle none/redirect to default
    return link


# users INVITE PERMS (who can invite this user to join their tasks?): "no one", "friends", or "everyone"
def get_invite_perms(username):
    return get_field("users", "username", username, "invite_perms")


def get_pending_task_invites(username):
    invites = get_field("users", "username", username, "pending_invites")
    return rm_empty(invites.split())


# get users who set invite perms to "everyone"
def get_public_users():
    users = get_all_users()
    return [user for user in users if get_field("users", "username", user, "invite_perms") == "everyone"]


#----------USERS-MUTATORS----------#


def change_password(username, old_passwd, new_passwd):

    if not auth(username, old_passwd):
        return "Incorrect old password"

    if new_passwd == "":
        return "Password cannot be empty"

    new_passwd = new_passwd.encode('utf-8')
    new_passwd = str(hashlib.sha256(new_passwd).hexdigest())

    modify_field("users", "username", username, "password", new_passwd)
    return "success"


# only call this function if the receiver does not currently have a pending req from the sender
def send_friend_req(sender, receiver):
    fr_reqs = get_friend_reqs(receiver)
    fr_reqs += [sender]
    friend_reqs = " " + " ".join(fr_reqs)
    modify_field("users", "username", receiver, "friend_reqs", friend_reqs)


def accept_fr(sender, receiver):
    # remove sender from fr_reqs
    remove_fr(sender, receiver)
    # add to friends
    r_friends = get_friends(receiver)
    r_friends += [sender]
    r_friends_str = " " + " ".join(r_friends)
    modify_field("users", "username", receiver, "friends", r_friends_str)
    s_friends = get_friends(sender)
    s_friends += [receiver]
    s_friends_str = " " + " ".join(s_friends)
    modify_field("users", "username", sender, "friends", s_friends_str)


# aka deny fr (unless called as a helper)
def remove_fr(sender, receiver):
    # remove sender from fr_reqs
    fr_reqs = get_friend_reqs(receiver)
    fr_reqs.remove(sender)
    friend_reqs = " " + " ".join(fr_reqs)
    modify_field("users", "username", receiver, "friend_reqs", friend_reqs)


def edit_pfp(username, newval):
    modify_field("users", "username", username, "pfp", newval)


# users INVITE PERMS (who can invite this user to join their tasks?): "no one", "friends", or "everyone"
def set_invite_perms(username, newval):
    modify_field("users", "username", username, "invite_perms", newval)


def invite_user(username, task):
    if not username == '':
        p_task_invs = get_pending_task_invites(username)
        p_task_invs += [task]
        pending_invites = " " + " ".join(p_task_invs)
        modify_field("users", "username", username, "pending_invites", pending_invites)


def accept_task_invite(username, task_id):
    rm_task_invite(username, task_id)
    add_user(task_id, username)


# aka deny task invite (unless called as a helper function)
def rm_task_invite(username, task_id):
    p_task_invs = get_pending_task_invites(username)
    p_task_invs.remove(task_id)
    pending_invites = " " + " ".join(p_task_invs)
    modify_field("users", "username", username, "pending_invites", pending_invites)


#----------LOGIN-REGISTER-AUTH----------#


# returns whether or not a user exists
def user_exists(username):
    all_users = get_all_users()
    for user in all_users:
        if (user == username):
            return True
    return False


# checks if provided password in login attempt matches user password
def auth(username, password):

    db = sqlite3.connect(DB_FILE)
    c = db.cursor()

    if not user_exists(username):
        db.commit()
        db.close()

        #raise ValueError("Username does not exist")
        return False

    # use ? for unsafe/user provided variables
    passpointer = c.execute('SELECT password FROM users WHERE username = ?', (username,))
    real_pass = passpointer.fetchone()[0]

    db.commit()
    db.close()

    password = password.encode('utf-8')

    # hash password here
    if real_pass != str(hashlib.sha256(password).hexdigest()):
        #raise ValueError("Incorrect password")
        return False

    return True


# adds a new user's data to user table
def register_user(username, password):

    if user_exists(username):
        #raise ValueError("Username already exists")
        return "Username already exists"

    if password == "":
        #raise ValueError("You must enter a non-empty password")
        return "Password cannot be empty"

    db = sqlite3.connect(DB_FILE)
    c = db.cursor()

    # hash password here
    password = password.encode('utf-8')
    password = str(hashlib.sha256(password).hexdigest())

    # use ? for unsafe/user provided variables
    c.execute('INSERT INTO users VALUES (?, ?, "","","","no one","")', (username, password,))

    db.commit()
    db.close()

    return "success"


#=============================TASKS=============================#

#----------TASKS-ACCESSORS----------#


# return a list of all tasks in the DB
def all_tasks():

    db = sqlite3.connect(DB_FILE)
    c = db.cursor()

    data = c.execute('SELECT id FROM tasks').fetchall()

    db.commit()
    db.close()

    return clean_list(data)


# all tasks a user is involved with (not necessarily owner)
def get_all_tasks(username):
    tasks = all_tasks()
    user_tasks = []
    for task in tasks:
        users = get_task_users(task)
        if username in users:
            user_tasks += [task]
    return user_tasks


# all tasks by friends if friends set the right visibility
def get_friend_tasks(username):
    tasks = all_tasks()
    friends = get_friends(username)
    friend_tasks = []
    for task in tasks:
        if get_task_visibility(task) != "no one":
            users = get_task_users(task)
            for friend in friends:
                if friend in users:
                    friend_tasks += [task]
    return friend_tasks


def get_public_tasks():
    tasks = all_tasks()
    return [task for task in tasks if get_field("tasks", "id", task, "visibility") == "everyone"]


def get_all_tasks_owned(username):
    tasks = all_tasks()
    return [task for task in tasks if get_field("tasks", "id", task, "owner") == username]


def get_task_name(id):
    return get_field("tasks", "id", id, "name")


def get_task_desc(id):
    return get_field("tasks", "id", id, "description")


# YYYY-MM-DD
def get_task_deadline(id):
    return get_field("tasks", "id", id, "deadline")


def get_task_status(id):
    return get_field("tasks", "id", id, "status")


def get_task_category(id):
    return get_field("tasks", "id", id, "category")


def get_task_users(id):
    users = get_field("tasks", "id", id, "users")
    return rm_empty(users.split())


# tasks VISIBILITY (who can see this task on their homepage?): "no one", "friends", or "everyone"
def get_task_visibility(id):
    return get_field("tasks", "id", id, "visibility")


# tasks JOIN PERMS (who can join this task without an invite?): "no one", "friends", or "everyone"
def get_task_join_perms(id):
    return get_field("tasks", "id", id, "join_perms")


def get_task_owner(id):
    return get_field("tasks", "id", id, "owner")


def get_task_info(id):
    info = []
    info += [get_task_name(id)]
    info += [id]
    info += [get_task_desc(id)]
    info += [get_task_deadline(id)]
    info += [get_task_users(id)]
    info += [get_task_visibility(id)]
    info += [get_task_join_perms(id)]
    info += [get_task_owner(id)]
    return info



#----------TASKS-MUTATORS----------#


def create_task(name, description, deadline, category, users_to_inv, visibility, join_perms, owner):

    id = gen_id()
    status = "Not started"

    # add to db
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    c.execute('INSERT INTO tasks VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                                        (name, id, description, deadline, status, category, " " + owner, visibility, join_perms, owner,))
    db.commit()
    db.close()

    # invite other users
    for user in users_to_inv:
        invite_user(user, id)

    return id


# only show this option for users who own the task
def delete_task(id):
    delete_row("tasks", "id", id)


# only show this option for user who don't own the task
def leave_task(task_id, username):
    users = get_task_users(task_id)
    users.remove(username)
    task_users = " " + " ".join(users)
    modify_field("tasks", "id", task_id, "users", task_users)


def add_user(task_id, username):
    users = get_task_users(task_id)
    users += [username]
    task_users = " " + " ".join(users)
    modify_field("tasks", "id", task_id, "users", task_users)


def set_task_name(task_id, name):
    modify_field("tasks", "id", task_id, "name", name)


def set_task_description(task_id, desc):
    modify_field("tasks", "id", task_id, "description", desc)


# YYYY-MM-DD
def set_task_deadline(task_id, deadline):
    modify_field("tasks", "id", task_id, "deadline", deadline)


def set_task_status(task_id, status):
    modify_field("tasks", "id", task_id, "status", status)


def set_task_category(task_id, category):
    modify_field("tasks", "id", task_id, "category", category)


# tasks VISIBILITY (who can see this task on their homepage?): "no one", "friends", or "everyone"
def set_task_visibility(task_id, vis):
    modify_field("tasks", "id", task_id, "visibility", vis)


# tasks JOIN PERMS (who can join this task without an invite?): "no one", "friends", or "everyone"
def set_task_join_perms(task_id, perms):
    modify_field("tasks", "id", task_id, "join_perms", perms)


def set_task_owner(task_id, username):
    modify_field("tasks", "id", task_id, "owner", username)


#=============================GENERAL=HELPERS=============================#


def create_table(contents):
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    c.execute(contents)
    db.commit()
    db.close()

# wrapper method
# used for a bunch of accessor methods; used when only 1 item should be returned
def get_field(table, ID_fieldname, ID, field):
    lst = get_field_list(table, ID_fieldname, ID, field)
    if (len(lst) == 0):
        return 'None'
    return lst[0]


# used for a bunch of accessor methods; used when a list of items in a certain field should be returned
def get_field_list(table, ID_fieldname, ID, field):

    db = sqlite3.connect(DB_FILE)
    c = db.cursor()

    # use ? for unsafe/user provided variables
    data = c.execute(f'SELECT {field} FROM {table} WHERE {ID_fieldname} = ?', (ID,)).fetchall()

    db.commit()
    db.close()

    return clean_list(data)


# turn a list of tuples (returned by .fetchall()) into a 1d list
def clean_list(raw_output):

    clean_output = []

    for lst in raw_output:
        for item in lst:
            if str(item) != 'None' and item != "":
                clean_output += [item]

    return clean_output


def rm_empty(lst):
    return [item for item in lst if item and str(item) != "None"]


def modify_field(table, ID_fieldname, ID, field, new_val):

    db = sqlite3.connect(DB_FILE)
    c = db.cursor()

    # use ? for unsafe/user provided variables
    c.execute(f'UPDATE {table} SET {field} = ? WHERE {ID_fieldname} = ?', (new_val, ID,))

    db.commit()
    db.close()


def delete_row(table, ID_fieldname, id):
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()

    # use ? for unsafe/user provided variables
    c.execute(f'DELETE FROM {table} WHERE {ID_fieldname} = ?', (id,))

    db.commit()
    db.close()


# generate an id
def gen_id():
    # use secrets module to generate a random 32-byte string
    return secrets.token_hex(32)


#=============================MAIN=============================#

# run this if this program was called directly, not as a dependency for another thing
if __name__ == '__main__':
    create_users_table()
    create_tasks_table()
    register_user("Maya", "hi")
    register_user("Ethan", "test")
