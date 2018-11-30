import mysql.connector
from flask import Blueprint
from flask import render_template, session, redirect, url_for, flash

mod = Blueprint('mod', __name__)


# voter list
@mod.route("/voterList")
def voterList():
    if 'username' in session:
        username = session['username']
        return render_template("voterList.html", username=username)
    flash("please Login first")
    return redirect(url_for('login'))


# voterListBackend
@mod.route("/voterListBackend")
def voterListBackend():
    try:
        mydb = mysql.connector.connect(host="localhost", user="root", password="nitin", database="bees")
        print("error")
        mycursor = mydb.cursor()
        print("error222")
        mycursor.execute("Select * from voter")
        rs = mycursor.fetchall()
        session['data'] = rs
        return redirect(url_for('voterList'))
    except mysql.connector.Error as error:
        flash("Records failed to be retrieved")
        return redirect(url_for('voterList'))
    finally:
        # closing database connection.
        if (mydb.is_connected()):
            mydb.close()
