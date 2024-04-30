import json
import os
import hashlib

# Constants
MEMPOOL_DIR = 'mempool'
OUTPUT_FILE = 'output.txt'
DIFFICULTY_TARGET = '0000ffff00000000000000000000000000000000000000000000000000000000'
MAX_BLOCK_SIZE = 1000000  # Maximum block size in bytes

# Function to read transactions from the mempool directory
def read_transactions_from_mempool():
    transactions = []
    for filename in os.listdir(MEMPOOL_DIR):
        if filename.endswith('.json'):
            file_path = os.path.join(MEMPOOL_DIR, filename)
            with open(file_path, 'r') as file:
                try:
                    transaction_data = json.load(file)
                    transactions.append(transaction_data)
                except json.JSONDecodeError:
                    continue  # Skip invalid JSON files
    return transactions

# Function to validate a transaction
def validate_transaction(transaction):
    # Check if the transaction has required fields
    required_fields = ['version', 'vin', 'vout']
    if not all(field in transaction for field in required_fields):
        return False

    # Check if the transaction fee is reasonable
    total_input_value = transaction['vin'][0]["prevout"]['value']
    total_output_value = transaction['vout'][0]['value']
    transaction_fee = total_input_value - total_output_value

    if transaction_fee < 0 or transaction_fee > 0.1 * total_output_value:
        return False

    return True

# Function to construct the block header
def construct_block_header(previous_block_hash, merkle_root_hash, timestamp, difficulty_target, nonce):
    return {
        'version': 1,
        'previous_block_hash': previous_block_hash,
        'merkle_root_hash': merkle_root_hash,
        'timestamp': timestamp,
        'difficulty_target': difficulty_target,
        'nonce': nonce
    }

# Function to serialize the block header
def serialize_block_header(block_header):
    return ''.join(f"{key}:{value}\n" for key, value in block_header.items())

# Function to mine a block
def mine_block(block_header):
    nonce = 0
    while True:
        block_header['nonce'] = nonce
        serialized_block_header = serialize_block_header(block_header)
        block_hash = hashlib.sha256(serialized_block_header.encode()).hexdigest()
        if block_hash < DIFFICULTY_TARGET:
            return nonce, block_hash
        nonce += 1

# Function to serialize a transaction
def serialize_transaction(transaction):
    return json.dumps(transaction) + '\n'

# Function to get the size of a transaction (for block size calculation)
def get_transaction_size(transaction):
    return len(serialize_transaction(transaction))

# Function to output the results to output.txt
def output_results(block_header, coinbase_transaction, mined_transactions):
    with open(OUTPUT_FILE, 'w') as file:
        file.write(serialize_block_header(block_header))
        file.write(serialize_transaction(coinbase_transaction))
        for tx in mined_transactions:
            if 'txid' in tx:
                file.write(f"{tx['txid']}\n")

# Main function to orchestrate the mining process
def main():
    transactions = read_transactions_from_mempool()
    valid_transactions = [tx for tx in transactions if validate_transaction(tx)]

    # Construct the block header
    previous_block_hash = '0000000000000000000000000000000000000000000000000000000000000000'
    merkle_root_hash = '1a2b3c4d5e6f7g8h9i0j'
    timestamp = 1631450725
    nonce = 0
    block_header = construct_block_header(previous_block_hash, merkle_root_hash, timestamp, DIFFICULTY_TARGET, nonce)

    # Mine the block
    nonce, block_hash = mine_block(block_header)
    block_header['nonce'] = nonce

    # Construct the coinbase transaction
    block_reward = 6.25
    coinbase_transaction = {
        "txid": "coinbase_txid",
        "inputs": [],
        "outputs": [{"value": block_reward, "scriptpubkey": "coinbase_scriptpubkey"}]
    }

    # Select transactions to include in the block
    current_block_size = get_transaction_size(coinbase_transaction)
    selected_transactions = [coinbase_transaction]

    for transaction in valid_transactions:
        transaction_size = get_transaction_size(transaction)
        if current_block_size + transaction_size <= MAX_BLOCK_SIZE:
            selected_transactions.append(transaction)
            current_block_size += transaction_size

    # Output the results
    output_results(block_header, coinbase_transaction, selected_transactions[1:])  # Exclude coinbase transaction from txid list
    print("Mining completed. Block hash:", block_hash)

if __name__ == "__main__":
    main()
