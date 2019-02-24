from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
import Crypto.Random
import binascii
from transaction import Transaction
from collections import OrderedDict
class Wallet:
    def __init__(self, node_id):
        self.private_key = None
        self.public_key = None
        self.node_id = node_id

    def create_keys(self):
        # it creates as well as save the keys in a text file
        private_key = RSA.generate(1024, Crypto.Random.new().read)
        public_key = private_key.publickey()
        self.private_key=binascii.hexlify(private_key.exportKey(format='DER')).decode('ascii')
        self.public_key=binascii.hexlify(public_key.exportKey(format='DER')).decode('ascii')

        #now save these keys in a file called wallet-node_id.txt for each node

        if self.public_key != None and self.private_key != None:
            try:
                with open('wallet-{}.txt'.format(self.node_id), mode='w') as f:
                    f.write(self.public_key)
                    f.write('\n')
                    f.write(self.private_key)
                return True
            except (IOError, IndexError):
                print('Saving wallet failed...')
                return False

    def load_keys(self):
        """Loads the keys from the wallet.txt file into memory."""
        try:
            with open('wallet-{}.txt'.format(self.node_id), mode='r') as f:
                keys = f.readlines()
                public_key = keys[0][:-1]
                private_key = keys[1]
                self.public_key = public_key
                self.private_key = private_key
            return True
        except (IOError, IndexError):
            print('Loading wallet failed...')
            return False

    def create_transaction(self,receiver,amount,OP_RETURN=""):

        sender_address=SHA256.new((self.public_key).encode('utf8')).hexdigest()
        signer = PKCS1_v1_5.new(RSA.importKey(binascii.unhexlify(self.private_key)))
        h = SHA256.new((str(sender_address) + str(receiver) + str(amount)).encode('utf8'))
        sign = signer.sign(h)
        signature=binascii.hexlify(sign).decode('ascii')
        scriptSig=OrderedDict([('signature', signature), ('public_key', self.public_key)])


        return Transaction(sender_address,receiver,amount,scriptSig,h.hexdigest(),OP_RETURN)

    @staticmethod
    def verify_transaction(transaction):
        print("hello")
        public_key = RSA.importKey(binascii.unhexlify(transaction.scriptSig['public_key']))
        verifier = PKCS1_v1_5.new(public_key)
        h = SHA256.new((str(transaction.sender) + str(transaction.receiver) + str(transaction.amount)).encode('utf8'))
        print("hash",h.hexdigest())
        return verifier.verify(h, binascii.unhexlify(transaction.scriptSig['signature']))
