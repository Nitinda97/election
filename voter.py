from collections import OrderedDict

from flask import Flask,jsonify,request,render_template
import requests
from wallet import Wallet
from blockchain import Blockchain
from Crypto.Hash import SHA256
from transaction import Transaction
app=Flask(__name__)


@app.route('/wallet', methods=['POST'])
def create_keys():
    if wallet.create_keys():
        global blockchain
        blockchain = Blockchain(wallet.public_key, port)
        address = SHA256.new((wallet.public_key).encode('utf8')).hexdigest()
        url = 'http://localhost:{}/broadcast-key'.format("5000")
        try:
            response = requests.post(url, json={
                'public_key': wallet.public_key})
            print("reached")
            if response.status_code == 400 or response.status_code == 500:
                print('Saving Keys Failed')
                response={'message':"Saving Keys Failed"}
                return jsonify(response), 500
        except requests.exceptions.ConnectionError:
            pass
        response = {
            'Nitcoin Address':address,
            'private_key': wallet.private_key,
            'public_key': wallet.public_key,
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

@app.route("/user")
def user():
    return render_template('generate_key.html')


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
    if(node not in blockchain.peer_nodes):
        blockchain.peer_nodes.add(node)
        blockchain.save_data()
        try:
            url = 'http://localhost:{}/node'.format(node)
            response = requests.post(url, json={
                'node': port})
            print("reached-adding node")
            if response.status_code == 400 or response.status_code == 500:
                print('Saving Node Failed')
        except requests.exceptions.ConnectionError:
            pass
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
















if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('-p', '--port', type=int, default=5001)
    args = parser.parse_args()
    port = args.port
    wallet = Wallet(port)
    blockchain = Blockchain(wallet.public_key, port)
    blockchain.peer_nodes.add(5000)
    blockchain.save_data()
    url = 'http://localhost:{}/node'.format(5000)
    try:
        response = requests.post(url, json={
            'node': port})
        print("reached-adding node")
        if response.status_code == 400 or response.status_code == 500:
            print('Saving Node Failed')
    except requests.exceptions.ConnectionError:
        pass
    app.run(host='localhost', port=port)