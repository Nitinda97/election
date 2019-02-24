from time import time
class Block:
    def __init__(self,index,prev_hash,proof,transactions,timestamp=time()):
        self.index=index
        self.prev_hash=prev_hash
        self.proof=proof
        self.transactions=transactions
        self.timestamp = timestamp
