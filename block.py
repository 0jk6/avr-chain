import time
import json
import hashlib

class Block:
    def __init__(self, index, sender, receiver, amount, timestamp, previous_hash, nonce = 0):
        self.index = index
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.timestamp = timestamp
        self.nonce = nonce
        self.hash = ""
        self.previous_hash = previous_hash

    def compute_hash(self):
        #block_string = json.dumps(self.__dict__, sort_keys=True)
        #block_string = str(self.index) + (str(self.timestamp)).replace(".","") + self.previous_hash + str(self.nonce)

        block_string = self.previous_hash + str(self.nonce)

        return hashlib.sha1(block_string.encode()).hexdigest()


class Blockchain:
    difficulty = 1

    def __init__(self):
        self.chain = []
        self.create_genesis_block()

    def create_genesis_block(self):
        genesis_block = Block(0, "AVR", "GENESIS", 0, time.time(), "0"*40)
        genesis_block.hash = genesis_block.compute_hash()
        (self.chain).append(genesis_block)


    def last_block(self):
        return self.chain[-1]

    def proof_of_work(self, block):
        computed_hash = ""
        while not computed_hash.startswith("0"*Blockchain.difficulty):
            block.nonce += 1
            block.hash = computed_hash = block.compute_hash()

        print("Block mined with a nonce: " + str(block.nonce))
        return computed_hash

    def add_block(self, block, proof):
        previous_hash = self.last_block().hash

        if previous_hash != block.previous_hash:
            return False

        if not self.is_valid_proof(block, proof):
            return False

        block.hash = proof
        self.chain.append(block)
        return True


    def is_valid_proof(self, block, proof):
        return (block.hash.startswith('0'*Blockchain.difficulty)) and proof == block.compute_hash()

    def mine(self):
        print("Mining ...")
        last_block = self.last_block()
        new_block = Block(index = last_block.index+1, sender="AVR", receiver="jaychandra", amount=100, timestamp = time.time(), previous_hash = last_block.hash)
        proof = self.proof_of_work(new_block)

        self.add_block(new_block, proof)
        return new_block


b = Blockchain()

from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route("/mine", methods=['GET'])
def mine_route():
    block = b.mine()
    s = {
            "Block index" : block.index,
            "Hash " : block.hash,
            "Previous Hash " : block.previous_hash,
            "Timestamp " : block.timestamp,
            "sender" : block.sender,
            "receiver" : block.receiver,
            "amount" : block.amount
        }

    return jsonify(s)

@app.route("/chain", methods=['GET'])
def get_chain():
    chain = b.chain
    res = []

    for block in chain:
        s = {
            "Block index" : block.index,
            "Hash " : block.hash,
            "Previous Hash " : block.previous_hash,
            "Timestamp " : block.timestamp,
            "sender" : block.sender,
            "receiver" : block.receiver,
            "amount" : block.amount
        }

        res.append(s)
    return jsonify(res)


#this block will send the most recent block's data to the microcontroller
@app.route("/get_data", methods=['GET'])
def get_data():
    block = b.chain[-1]
    s = {
        "previous_hash":block.hash,
        "index" : block.index,
        "timestamp" : block.timestamp,
        "index" : block.index
    }

    return jsonify(s)


#this route will accept data from avr microcontrollers mined data and will accept or reject it
@app.route("/block", methods=['POST'])
def block_route():
    json_data = request.json
    print(json_data)
    
    last_block = b.chain[-1]

    new_block = Block(index = last_block.index+1, sender=json_data["sender"], receiver=json_data["receiver"], amount=json_data["amount"], timestamp = time.time(), previous_hash = last_block.hash, nonce = json_data["nonce"])
    new_block.hash = json_data["hash"]
    proof = json_data["hash"]

    #print(b.is_valid_proof(new_block, proof))

    if(b.add_block(new_block, proof)):
        return jsonify({"message" : "ACCEPTED"})



    return jsonify({"message" : "REJECTED"})

app.run(port=3000, debug=True)
