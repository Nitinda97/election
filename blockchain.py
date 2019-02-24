from collections import OrderedDict

from block import Block
from wallet import Wallet
from transaction import Transaction
import json
import hashlib
from Crypto.Hash import SHA256
import requests
MINING_REWARD = 10
class Blockchain:
    def __init__(self, public_key, node_id):
        genesis_block = Block(0, '', 100, [], 0)
        self.chain = []
        self.chain.append(genesis_block)
        # Unhandled transactions
        self.open_transactions = []
        self.public_key = public_key
        self.peer_nodes = set()
        self.node_id = node_id
        self.load_data()


    def get_balance(self,sender=None):
        if sender is None:
            return None
        else:
            sent = 0
            received=0
            for block in self.chain:
                for transaction in block.transactions:
                    if(sender==transaction.sender):
                        sent=sent+transaction.amount
                    elif(sender==transaction.receiver):
                        received=received+transaction.amount
            for tx in self.open_transactions:
                if (sender == tx.sender):
                    sent = sent + tx.amount
            print("balance=",received-sent)
            return received-sent

    def verify_transaction(self,transaction):
        sender_balance = self.get_balance(transaction.sender)
        print("Balance",sender_balance)
        return sender_balance >= transaction.amount and Wallet.verify_transaction(transaction)

    def load_data(self):
        # Initialize blockchain + open transactions data from a file.
        try:
            with open('blockchain-{}.txt'.format(self.node_id), mode='r') as f:
                file_content = f.readlines()
                bc = json.loads(file_content[0][:-1])
                updated_bc = []
                for block in bc:
                    converted_tx = [Transaction(
                        tx['sender'], tx['receiver'],tx['amount'], tx['scriptSig']) for tx in block['transactions']]
                    updated_block = Block(
                        block['index'], block['prev_hash'],block['proof'], converted_tx,block['timestamp'])
                    updated_bc.append(updated_block)
                self.chain = updated_bc

                # loading open transactions
                open_transactions = json.loads(file_content[1][:-1])
                updated_transactions = []
                for tx in open_transactions:
                    updated_transaction = Transaction(tx['sender'], tx['receiver'], tx['amount'], tx['scriptSig'])
                    updated_transactions.append(updated_transaction)
                self.open_transactions = updated_transactions

                # loading peer nodes
                peer_nodes = json.loads(file_content[2])
                self.peer_nodes = set(peer_nodes)
        except (IOError, IndexError):
            pass
        finally:
            print('Cleanup!')

    def save_data(self):
        """Save blockchain + open transactions snapshot to a file."""
        try:
            with open('blockchain-{}.txt'.format(self.node_id), mode='w') as f:
                saveable_chain = [block.__dict__ for block in [Block(block_el.index, block_el.prev_hash,  block_el.proof,[
                    tx.__dict__ for tx in block_el.transactions], block_el.timestamp) for block_el in
                                                               self.chain]]
                f.write(json.dumps(saveable_chain))
                f.write('\n')

                saveable_tx = [tx.__dict__ for tx in self.open_transactions]
                f.write(json.dumps(saveable_tx))
                f.write('\n')
                f.write(json.dumps(list(self.peer_nodes)))
        except IOError:
            print('Saving failed!')


    def hash_block(self,block):
        hashable_block = block.__dict__.copy()
        hashable_block['transactions'] = [tx.to_ordered_dict() for tx in hashable_block['transactions']]
        return hashlib.sha256(json.dumps(hashable_block, sort_keys=True).encode()).hexdigest()

    def add_transaction(self,transaction,is_receiving=False):
        if (self.verify_transaction(transaction)):
            self.open_transactions.append(transaction)
            self.save_data()
            if not is_receiving:
                for node in self.peer_nodes:
                    print(node)
                    url = 'http://localhost:{}/broadcast-transaction'.format(node)
                    try:
                        response = requests.post(url, json={
                            'sender': transaction.sender, 'receiver': transaction.receiver, 'amount': transaction.amount, 'signature': transaction.scriptSig['signature'],'public_key':transaction.scriptSig['public_key'],'transaction_no':transaction.transaction_no,'OP_RETURN':transaction.OP_RETURN})
                        if response.status_code == 400 or response.status_code == 500:
                            print('Transaction declined, needs resolving')
                            return False
                    except requests.exceptions.ConnectionError:
                        continue
            return True
        return False

    def valid_proof(self,transactions,prev_hash,proof):
        guess_hash= hashlib.sha256((str([tx.to_ordered_dict() for tx in transactions]) + str(prev_hash) + str(proof)).encode()).hexdigest()
        return guess_hash[0:2]=='00'

    def proof_of_work(self):
        proof=0
        while(not self.valid_proof(self.open_transactions,self.hash_block(self.chain[-1]),proof)):
            proof+=1
        return proof

    def mine_block(self):
        if self.public_key == None:
            return None

        index=len(self.chain)
        prev_hash=self.hash_block(self.chain[-1])
        print("prev hash generated:",prev_hash)
        proof=self.proof_of_work()
        print("proof generated:", proof)
        scriptSig=OrderedDict([('signature', ''), ('pubic_key', 'Mining')])
        receiver=(SHA256.new((self.public_key).encode('utf8'))).hexdigest()
        h = SHA256.new((str("Mining") + str(receiver) + str(MINING_REWARD)).encode('utf8'))
        reward_transaction=Transaction("Mining",receiver,MINING_REWARD,scriptSig,h.hexdigest(),"")
        print("reward generated",reward_transaction.__dict__)
        copied_transactions = self.open_transactions[:]
        for tx in copied_transactions:
            if not Wallet.verify_transaction(tx):
                return None
        print("Copied_transaction 1", copied_transactions)
        copied_transactions.append(reward_transaction)
        print("Copied_transaction 2",copied_transactions)
        block = Block(index, prev_hash, proof, copied_transactions)
        print("block generated",block.__dict__)
        self.chain.append(block)
        self.open_transactions = []
        self.save_data()
        return block

    def add_block(self, block):
        transactions = [Transaction(
            tx['sender'], tx['receiver'], tx['amount'], tx['scriptSig']) for tx in block['transactions']]
        proof_is_valid = self.valid_proof(
            transactions[:-1], block['prev_hash'], block['proof'])
        hashes_match = self.hash_block(self.chain[-1]) == block['prev_hash']
        if not proof_is_valid or not hashes_match:
            return False
        converted_block = Block(
            block['index'], block['prev_hash'], block['proof'],transactions, block['timestamp'])
        self.chain.append(converted_block)
        stored_transactions = self.open_transactions[:]
        for itx in block['transactions']:
            for opentx in stored_transactions:
                if opentx.sender == itx['sender'] and opentx.receiver == itx['receiver'] and opentx.amount == itx[
                    'amount'] and opentx.scriptSig == itx['scriptSig']:
                    try:
                        self.open_transactions.remove(opentx)
                    except ValueError:
                        print('Item was already removed')
        self.save_data()
        return True



