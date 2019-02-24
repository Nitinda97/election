from collections import OrderedDict

from flask import Flask,jsonify,request,render_template
from wallet import Wallet
from blockchain import Blockchain
from Crypto.Hash import SHA256
from transaction import Transaction
app=Flask(__name__)

@app.route('/')
def index():
    return render_template('Node.html')

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

@app.route('/transaction', methods=['POST'])
def add_transaction():
    if wallet.public_key == None:
        response = {
            'message': 'No wallet set up.'
        }
        return jsonify(response), 400
    values = request.get_json()
    if not values:
        response = {
            'message': 'No data found.'
        }
        return jsonify(response), 400
    required_fields = ['receiver', 'amount']
    if not all(field in values for field in required_fields):
        response = {
            'message': 'Required data is missing.'
        }
        return jsonify(response), 400
    receiver = values['receiver']
    amount = values['amount']
    transaction=wallet.create_transaction(receiver,amount)
    print("transaction_created",transaction.__dict__)
    success = blockchain.add_transaction(transaction)
    if success:
        address = SHA256.new((wallet.public_key).encode('utf8')).hexdigest()
        response = {
            'message': 'Successfully added transaction.',
            'transaction': {
                'sender': address,
                'recipient': receiver,
                'amount': amount,
                'scriptSig': transaction.scriptSig,
                'transaction_no':transaction.transaction_no,
                'OP_RETURN':transaction.OP_RETURN
            },
            'funds': blockchain.get_balance(address)
        }
        return jsonify(response), 201
    else:
        response = {
            'message': 'Creating a transaction failed.'
        }
        return jsonify(response), 500

@app.route('/balance', methods=['GET'])
def get_balance():
    address = SHA256.new((wallet.public_key).encode('utf8')).hexdigest()
    balance = blockchain.get_balance(address)
    if balance is not None:
        response = {
            'message': 'Fetched balance successfully.',
            'funds': balance
        }
        return jsonify(response), 200
    else:
        response = {
            'messsage': 'Loading balance failed.',
            'wallet_set_up': wallet.public_key is not None
        }
        return jsonify(response), 500

@app.route('/transactions', methods=['GET'])
def get_open_transaction():
    transactions = blockchain.open_transactions
    dict_transactions = [tx.__dict__ for tx in transactions]
    return jsonify(dict_transactions), 200


@app.route('/chain', methods=['GET'])
def get_chain():
    chain_snapshot = blockchain.chain
    dict_chain = [block.__dict__.copy() for block in chain_snapshot]
    for dict_block in dict_chain:
        dict_block['transactions'] = [
            tx.__dict__ for tx in dict_block['transactions']]
    return jsonify(dict_chain), 200

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
    blockchain.peer_nodes.add(node)
    blockchain.save_data()
    response = {
        'message': 'Node added successfully.',
        'all_nodes': list(blockchain.peer_nodes)
    }
    return jsonify(response), 201


@app.route('/node/<node_url>', methods=['DELETE'])
def remove_node(node_url):
    if node_url == '' or node_url == None:
        response = {
            'message': 'No node found.'
        }
        return jsonify(response), 400
    blockchain.peer_nodes.remove(node_url)
    response = {
        'message': 'Node removed',
        'all_nodes': list(blockchain.peer_nodes)
    }
    return jsonify(response), 200


@app.route('/nodes', methods=['GET'])
def get_nodes():
    nodes = list(blockchain.peer_nodes)
    response = {
        'all_nodes': nodes
    }
    return jsonify(response), 200

@app.route('/broadcast-transaction', methods=['POST'])
def broadcast_transaction():
    values = request.get_json()
    if not values:
        response = {'message': 'No data found.'}
        return jsonify(response), 400
    required = ['sender', 'receiver', 'amount', 'signature','public_key','transaction_no','OP_RETURN']
    if not all(key in values for key in required):
        response = {'message': 'Some data is missing.'}
        return jsonify(response), 400
    scriptSig = OrderedDict([('signature', values['signature']), ('public_key', values['public_key'])])
    transaction=Transaction(values['sender'], values['receiver'], values['amount'], scriptSig,values['transaction_no'],values['OP_RETURN'])
    success = blockchain.add_transaction(transaction,is_receiving=True)
    if success:
        response = {
            'message': 'Successfully added transaction.',
            'transaction': {
                'sender': values['sender'],
                'receiver': values['receiver'],
                'amount': values['amount'],
                'scriptSig': values['scriptSig'],
                'transaction_no': values['transaction_no'],
                'OP_RETURN': values['OP_RETURN']
            }
        }
        return jsonify(response), 201
    else:
        response = {
            'message': 'Creating a transaction failed.'
        }
        return jsonify(response), 500

@app.route('/broadcast-block', methods=['POST'])
def broadcast_block():
    values = request.get_json()
    if not values:
        response = {'message': 'No data found.'}
        return jsonify(response), 400
    if 'block' not in values:
        response = {'message': 'Some data is missing.'}
        return jsonify(response), 400
    block = values['block']
    if block['index'] == blockchain.chain[-1].index + 1:
        if blockchain.add_block(block):
            response = {'message': 'Block added'}
            return jsonify(response), 201
        else:
            response = {'message': 'Block seems invalid.'}
            return jsonify(response), 500
    elif block['index'] > blockchain.chain[-1].index:
        pass
    else:
        response = {'message': 'Blockchain seems to be shorter, block not added'}
        return jsonify(response), 409

if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('-p', '--port', type=int, default=5000)
    args = parser.parse_args()
    port = args.port
    wallet = Wallet(port)
    blockchain = Blockchain(wallet.public_key, port)
    app.run(host='localhost', port=port)
