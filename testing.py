#to upload on github first commit then do push
from flask import Flask,render_template, request, json, session, redirect, url_for, flash
import mysql.connector
from flask_mail import Mail,Message
import hashlib
import random
import requests
import os
from collections import OrderedDict

from flask import Flask,jsonify,request,render_template
from generate_key import Keys
from wallet import Wallet
from blockchain import Blockchain
from Crypto.Hash import SHA256
import Crypto.Random
import binascii
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from transaction import Transaction

app = Flask(__name__)
# Settings

mail = Mail(app)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = "iamnitinkhare@gmail.com"
app.config['MAIL_PASSWORD'] = "peaceout@97"
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)
app.secret_key = "any random string"


@app.route('/')
def index():
    return render_template('BEES.html')

#LINK FOR VOTER
"""
@app.route("/user")
def user():
    '''try:
        mydb = mysql.connector.connect(host="localhost", user="root", password="nitin", database="bees")
        print("error")
        mycursor = mydb.cursor()
        print("error222")
        print(post)
        mycursor.execute("Select * from link WHERE id="+"1")
        print("000")
        rs = mycursor.fetchall()
        if(rs):
            return "success"
    except mysql.connector.Error as error:
        return "error"
    finally:
        # closing database connection.
        if (mydb.is_connected()):
            mydb.close()'''
    return render_template("generate_key.html")

@app.route('/generate_keys', methods=['POST'])
def create_keys():
    if keys.create_keys():
        #global blockchain
        #blockchain = Blockchain(keys.public_key, port)

        #try:
           # mydb = mysql.connector.connect(host="localhost", user="root", password="nitin", database="bees")
            #print("error")
            #mycursor = mydb.cursor()
            #print("error222")
            #mycursor.execute("Insert into keystorage(publickey) values(%s)",keys.public_key)
            #print("error33")
            #mydb.commit()
            response = {
                'public_key': keys.public_key,
                'private_key': keys.private_key
            }
            return jsonify(response), 201
        #except mysql.connector.Error as error:
            #mydb.rollback()  # rollback if any exception occured
            #response = {
             #   'message': 'Saving the keys failed.'
            #}
            #return jsonify(response), 500
        #finally:
            # closing database connection.
            #if (mydb.is_connected()):
                #mydb.close()
    else:
        response = {
            'message': 'Saving the keys failed.'
        }
        return jsonify(response), 500
"""
# EA SAVE PUBLIC KEY IN DATABASE
@app.route('/broadcast-key', methods=['POST'])
def broadcast_transaction():
    values = request.get_json()
    if not values:
        response = {'message': 'No data found.'}
        return jsonify(response), 400
    required = ['public_key']
    if not all(key in values for key in required):
        response = {'message': 'Some data is missing.'}
        return jsonify(response), 400
    key=values['public_key']
    success=addKey(key)
    if success:
        response = {
            'message': 'Success',
        }
        return jsonify(response), 201
    else:
        response = {
            'message': 'Fail'
        }
        return jsonify(response), 500


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
            t=email+str(random.randint(1, 101))
            h = hashlib.md5(t.encode())
            h2 = h.hexdigest()
            mycursor.execute("Insert into voter(first_name,last_name,email,uid,redirect) values(%s,%s,%s,%s,%s)",
                             (firstname, lastname, email, uid, h2))
            print("error33")
            #UNIQUE LINK FOR THE VOTER
            s="http://127.0.0.1:5000/user/"+h2

            mydb.commit()
            msg = Message('Hello', sender='nitinkhare97@gmail.com', recipients=['nitinda97@gmail.com'])
            msg.body = s
            mail.send(msg)
            flash("Email has been sent to the voter")
            return redirect(url_for('addVoter'))
        except mysql.connector.Error as error:
            mydb.rollback()  # rollback if any exception occured
            flash("Records failed to be added")
            return redirect(url_for('addVoter'))
        finally:
            # closing database connection.
            if (mydb.is_connected()):
                mydb.close()

# voter list
@app.route("/voterList")
def voterList():
    if 'username' in session:
        username = session['username']
        return render_template("voterList.html", username=username)
    flash("please Login first")
    return redirect(url_for('login'))


# voterListBackend
@app.route("/voterListBackend")
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

# EA DASHBOARD
@app.route("/EAdashboard")
def EAdashboard():
    if 'username' in session:
        username = session['username']
        return render_template("EAdashboard.html", username=username)
    flash("please Login first")
    return redirect(url_for('login'))

# EA WALLET
@app.route('/wallet', methods=['POST'])
def create_keys():
    if wallet.create_keys():
        global blockchain
        blockchain = Blockchain(wallet.public_key, port)
        address = SHA256.new((wallet.public_key).encode('utf8')).hexdigest()
        response = {
            'Nitcoin Address':address,
            'private_key': wallet.private_key,
            'funds': blockchain.get_balance()
        }
        return jsonify(response), 201
    else:
        response = {
            'message': 'Saving the keys failed.'
        }
        return jsonify(response), 500

@app.route('/wallet', methods=['GET'])
def load_keys():
    if wallet.load_keys():
        global blockchain
        blockchain = Blockchain(wallet.public_key, port)
        address = SHA256.new((wallet.public_key).encode('utf8')).hexdigest()
        response = {
            'Nitcoin Address': address,
            'private_key': wallet.private_key,
            'funds': blockchain.get_balance()
        }
        return jsonify(response), 201
    else:
        response = {
            'message': 'Loading the keys failed.'
        }
        return jsonify(response), 500

# sent bitcoins to addresses
@app.route("/transaction",methods=['POST'])
def transaction():
    if wallet.public_key == None:
        response = {
            'message': 'No wallet set up.'
        }
        return jsonify(response), 400
    try:
        mydb = mysql.connector.connect(host="localhost", user="root", password="nitin", database="bees")
        print("error")
        mycursor = mydb.cursor()
        print("error222")
        mycursor.execute("Select COUNT(id) from keystorage")
        rs = mycursor.fetchone()
        count,= rs
        print(count)
        mycursor.execute("Select publickey from keystorage")
        rs_new = mycursor.fetchall()
        for (i,) in rs_new:
            address = SHA256.new(i.encode('utf8')).hexdigest()
            amt=1
            transaction = wallet.create_transaction(address, amt)
            print("transaction_created", transaction.__dict__)
            success = blockchain.add_transaction(transaction)
            if(success):
                continue
            else:
                response = {
                    'message': 'Creating a transaction failed.'
                }
                return jsonify(response), 500
        mydb.commit()
    except mysql.connector.Error as error:
        mydb.rollback()
        print("failure:{}".format(error))# rollback if any exception occured
    finally:
        # closing database connection.
        if (mydb.is_connected()):
            mydb.close()


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

def addKey(key):
    try:
        mydb = mysql.connector.connect(host="localhost", user="root", password="nitin", database="bees")
        print("error")
        mycursor = mydb.cursor()
        print("error222")
        mycursor.execute("Insert into keystorage(publickey) values(%s)",(key,))
        print("error33")
        mydb.commit()
        return True
    except mysql.connector.Error as error:
        mydb.rollback()
        print("failure:{}".format(error))# rollback if any exception occured
        return False
    finally:
        # closing database connection.
        if (mydb.is_connected()):
            mydb.close()

@app.route('/node', methods=['POST'])
def add_node():
    values = request.get_json()
    if not values:
        response = {
            'message': 'No data attached.'
        }
        return jsonify(response), 400
    if 'node' not in values:
        response = {
            'message': 'No node data found.'
        }
        return jsonify(response), 400
    node = values['node']
    for i in blockchain.peer_nodes:
        print(node)
        url = 'http://localhost:{}/node'.format(i)
        try:
            response = requests.post(url, json={
                'node': node})
            print("reached-adding node")
            if response.status_code == 400 or response.status_code == 500:
                print('Saving Node Failed')
        except requests.exceptions.ConnectionError:
            pass

    blockchain.peer_nodes.add(node)
    blockchain.save_data()
    response = {
        'message': 'Node added successfully.',
        'all_nodes': list(blockchain.peer_nodes)
    }
    return jsonify(response), 201

@app.route('/nodes', methods=['GET'])
def get_nodes():
    nodes = list(blockchain.peer_nodes)
    response = {
        'all_nodes': nodes
    }
    return jsonify(response), 200

@app.route('/mine', methods=['POST'])
def mine():
    block = blockchain.mine_block()
    address = SHA256.new((wallet.public_key).encode('utf8')).hexdigest()
    if block is not None:
        dict_block = block.__dict__.copy()
        dict_block['transactions'] = [
            tx.__dict__ for tx in dict_block['transactions']]
        response = {
            'message': 'Block added successfully.',
            'block': dict_block,
            'funds': blockchain.get_balance(address)
        }
        return jsonify(response), 201
    else:
        response = {
            'message': 'Adding a block failed.',
            'wallet_set_up': wallet.public_key is not None
        }
        return jsonify(response), 500

if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('-p', '--port', type=int, default=5000)
    args = parser.parse_args()
    port = args.port
    keys = Keys(port)
    wallet = Wallet(port)
    blockchain = Blockchain(wallet.public_key, port)
    #blockchain = Blockchain(wallet.public_key, port)
    app.run(host='localhost', port=port)
