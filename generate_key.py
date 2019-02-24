from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
import Crypto.Random
import binascii
from transaction import Transaction
from collections import OrderedDict
class Keys:
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
        print("hello")
        #now save these keys in a file called wallet-node_id.txt for each node

        if self.public_key != None and self.private_key != None:
            try:
                with open('keys-{}.txt'.format(self.node_id), mode='w') as f:
                    f.write(self.public_key)
                    f.write('\n')
                    f.write(self.private_key)
                print("keys generated")
                return True
            except (IOError, IndexError):
                print('Saving keys failed...')
                return False