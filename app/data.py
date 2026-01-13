# cerulean (Natalie Kieger, Michelle Chen, Maya Berchin)
# SoftDev pd 5
# P02: Makers Makin' It, Act I
# 2025-01-11
# Time spent: not that much on this file tbh, mostly recycling. ~40 mins?

import sqlite3                      # enable control of an sqlite database
import hashlib                      # for consistent hashes
import secrets                      # to generate ids

DB_FILE="data.db"


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
                    invite_perms    TEXT
                )"""
    create_table(contents)

# tasks
def create_tasks_table():
    contents =  """
                CREATE TABLE IF NOT EXISTS users (
                    name            TEXT    NOT NULL,
                    id              TEXT    NOT NULL    PRIMARY KEY,
                    description     TEXT,
                    deadline        TEXT,
                    status          TEXT    NOT NULL,
                    category        TEXT    NOT NULL,
                    users           TEXT    NOT NULL,
                    visibility      TEXT,
                    join_perms      TEXT,
                    owner           TEXT    NOT NULL
                )"""
    create_table(contents)


#=============================USERS=============================#


#----------USERS-ACCESSORS----------#


# returns a list of usernames
def get_all_users():
    
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()

    data = c.execute('SELECT username FROM userdata').fetchall()

    db.commit()
    db.close()

    return clean_list(data)


# returns a list of the user's friends
def get_friends(username):
    # friends stored by their usernames space separated
    friends = get_field("users", "username", username, "friends")
    friend_list = friends.split(" ").clear("")
    return friend_list


# returns a list of the friend requests a user may accept or reject
def get_friend_reqs(username):
    # friend reqa stored by usernames space separated
    friend_reqs = get_field("users", "username", username, "friend_reqs")
    friend_req_list = friend_reqs.split(" ").clear("")
    return friend_req_list


def count_fr_reqs(username):
    fr_reqs = get_friend_reqs(username)
    fr_list = fr_reqs.split(" ").clear("")
    return len(fr_list)
    

def get_pfp(username):
    return get_field("users", "username", username, "pfp")


def get_invite_perms(username):
    return get_field("users", "username", username, "invite_perms")


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
    fr_reqs += " " + sender
    modify_field("users", "username", receiver, "friend_reqs", fr_reqs)


def accept_fr(sender, receiver):
    
    # remove sender from fr_reqs
    remove_fr(sender, receiver)
    
    # add to friends
    r_friends = get_friends(receiver)
    r_friends += " " + sender
    modify_field("users", "username", receiver, "friends", r_friends)
    s_friends = get_friends(sender)
    s_friends += " " + receiver
    modify_field("users", "username", sender, "friends", s_friends)
    

def remove_fr(sender, receiver):
    
    # remove sender from fr_reqs
    fr_reqs = get_friend_reqs(receiver)
    fr_reqs.replace(" " + sender, "")
    modify_field("users", "username", receiver, "friend_reqs", fr_reqs)


def edit_pfp(username):
    return "tba"


def set_invite_perms(username, newval):
    
    valid_options = ["", "friends", "anyone"]
    if not newval in valid_options:
        return "invalid option for invite_perms"
    
    modify_field("users", "username", username, "invite_perms", newval)
    return "success"


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
    c.execute(f'INSERT INTO users VALUES (?, ?, "","","","")', (username, password,))

    db.commit()
    db.close()

    return "success"


#=============================TASKS=============================#

#----------TASKS-ACCESSORS----------#

#----------TASKS-MUTATORS----------#


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
            if str(item) != 'None':
                clean_output += [item]

    return clean_output


def modify_field(table, ID_fieldname, ID, field, new_val):

    db = sqlite3.connect(DB_FILE)
    c = db.cursor()

    # use ? for unsafe/user provided variables
    c.execute(f'UPDATE {table} SET {field} = ? WHERE {ID_fieldname} = ?', (new_val, ID,))

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
    # other tests