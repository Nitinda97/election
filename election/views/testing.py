from flask import render_template, request, json, session, redirect, url_for, flash
# from flask_mail import Mail, Message
import mysql.connector
from views import app
# from flask_mail import Mail, Message
import mysql.connector
from flask import render_template, request, json, session, redirect, url_for, flash

from views import app

# Settings
# mail = Mail(app)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'nitinkhare97@gmail.com'
app.config['MAIL_PASSWORD'] = 'Madhukhare97'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
# mail = Mail(app)
app.secret_key = "any random string"


@app.route('/')
def index():
    return render_template('BEES.html')


# Add a Voter in RA Dashboard
@app.route("/addVoter")
def addVoter():
    if 'username' in session:
        username = session['username']
        return render_template("addVote.html", username=username)
    flash("please Login first")
    return redirect(url_for('login'))


@app.route("/addVoterBackend", methods=["POST", "GET"])
def addVoterBackend():
    if request.method == 'POST':
        firstname = request.form['first_name']
        lastname = request.form['last_name']
        email = request.form['email']
        uid = request.form['uid']
        try:
            mydb = mysql.connector.connect(host="localhost", user="root", password="nitin", database="bees")
            print("error")
            mycursor = mydb.cursor()
            print("error222")
            mycursor.execute("Insert into voter(first_name,last_name,email,uid) values(%s,%s,%s,%s)",
                             (firstname, lastname, email, uid))
            print("error33")
            mydb.commit()
            '''msg = Message('Hello', sender='nitinkhare97@gmail.com', recipients=['nitinda97@gmail.com'])
            msg.body = "Hello Flask message sent from Flask-Mail"
            mail.send(msg)'''
            flash("Records Added Successfully")
            return redirect(url_for('addVoter'))
        except mysql.connector.Error as error:
            mydb.rollback()  # rollback if any exception occured
            flash("Records failed to be added")
            return redirect(url_for('addVoter'))
        finally:
            # closing database connection.
            if (mydb.is_connected()):
                mydb.close()


# Add a Candidate in RA Dashboard
@app.route("/addCandidate")
def addCandidate():
    if 'username' in session:
        username = session['username']
        return render_template("addCandidate.html", username=username)
    flash("please Login first")
    return redirect(url_for('login'))


@app.route("/addCandidateBackend", methods=["POST", "GET"])
def addCandidateBackend():
    if request.method == 'POST':
        firstname = request.form['first_name']
        lastname = request.form['last_name']
        email = request.form['email']
        uid = request.form['uid']
        party = request.form['party']
        try:
            mydb = mysql.connector.connect(host="localhost", user="root", password="nitin", database="bees")
            print("error")
            mycursor = mydb.cursor()
            print("error222")
            mycursor.execute("Insert into candidate(first_name,last_name,email,uid,party) values(%s,%s,%s,%s,%s)",
                             (firstname, lastname, email, uid, party))
            print("error33")
            mydb.commit()
            flash("Records Added Successfully")
            return redirect(url_for('addCandidate'))
        except mysql.connector.Error as error:
            mydb.rollback()  # rollback if any exception occured
            flash("Records failed to be added")
            return redirect(url_for('addCandidate'))
        finally:
            # closing database connection.
            if (mydb.is_connected()):
                mydb.close()


# voter list
@app.route("/candidateList")
def candidateList():
    if 'username' in session:
        username = session['username']
        return render_template("candidateList.html", username=username)
    flash("please Login first")
    return redirect(url_for('login'))


# voterListBackend
@app.route("/candidateListBackend")
def candidateListBackend():
    try:
        mydb = mysql.connector.connect(host="localhost", user="root", password="nitin", database="bees")
        print("error")
        mycursor = mydb.cursor()
        print("error222")
        mycursor.execute("Select * from candidate")
        rs = mycursor.fetchall()
        session['data'] = rs
        return redirect(url_for('candidateList'))
    except mysql.connector.Error as error:
        flash("Records failed to be retrieved")
        return redirect(url_for('candidateList'))
    finally:
        # closing database connection.
        if (mydb.is_connected()):
            mydb.close()


# RA Dashboard
@app.route("/dashboard")
def dashboard():
    if 'username' in session:
        username = session['username']
        return render_template("dashboard.html", username=username)
    flash("please Login first")
    return redirect(url_for('login'))


@app.route("/login", methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        mydb = mysql.connector.connect(host="localhost", user="root", passwd="nitin", database="bees")
        mycursor = mydb.cursor()
        mycursor.execute("Select * from login")
        rs = mycursor.fetchone()
        while (rs is not None):
            if (username == rs[1] and password == rs[2]):
                session['username'] = username
                if username == "ea":
                    return json.dumps({'name': 'ea'})  # "EA"
                else:
                    return json.dumps({'name': 'ra'})  # redirect(url_for('dashboard'))
            rs = mycursor.fetchone()
        return json.dumps({'error': 'YES'})
    return redirect(url_for('index'))


@app.route('/logout')
def logout():
    # remove the username from the session if it is there
    session.pop('username', None)
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
