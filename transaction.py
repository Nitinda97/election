from collections import OrderedDict
class Transaction:
    def __init__(self,sender,receiver,amount,scriptSig,transaction_no,OP_RETURN):
        self.sender=sender
        self.receiver=receiver
        self.amount=amount
        self.scriptSig=scriptSig
        self.transaction_no=transaction_no
        self.OP_RETURN=OP_RETURN

    def to_ordered_dict(self):
        return OrderedDict([('sender', self.sender), ('receiver', self.receiver), ('amount', self.amount), ('scriptSig', self.scriptSig),('transaction_no',self.transaction_no),('OP_RETURN',self.OP_RETURN)])