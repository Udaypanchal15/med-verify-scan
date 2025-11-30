# """
# Blockchain Service for anchoring QR code issuance hashes
# Supports Ethereum and Polygon testnets
# """
# import os
# import hashlib
# from typing import Optional, Dict, Any
# from web3 import Web3
# from web3.middleware import geth_poa_middleware
# from eth_account import Account
# import json

# class BlockchainService:
#     """Service for blockchain operations"""
    
#     def __init__(self, rpc_url: Optional[str] = None, private_key: Optional[str] = None,
#                  contract_address: Optional[str] = None, network: str = 'polygon-mumbai'):
#         """
#         Initialize blockchain service
#         rpc_url: Ethereum/Polygon RPC URL
#         private_key: Private key for signing transactions (for anchoring)
#         contract_address: Smart contract address for anchoring
#         network: Network name ('polygon-mumbai', 'goerli', etc.)
#         """
#         self.rpc_url = rpc_url or os.getenv('ETH_RPC_URL')
#         self.private_key = private_key or os.getenv('BLOCKCHAIN_PRIVATE_KEY')
#         self.contract_address = contract_address or os.getenv('BLOCKCHAIN_CONTRACT_ADDRESS')
#         self.network = network
        
#         if not self.rpc_url:
#             raise ValueError("RPC URL not provided. Set ETH_RPC_URL in environment.")
        
#         # Initialize Web3
#         self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
        
#         # Add POA middleware for Polygon and other POA networks
#         if 'mumbai' in network.lower() or 'polygon' in network.lower():
#             self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        
#         # Set up account if private key is provided
#         self.account = None
#         if self.private_key:
#             try:
#                 self.account = Account.from_key(self.private_key)
#                 self.w3.eth.default_account = self.account.address
#             except Exception as e:
#                 print(f"Warning: Failed to load account from private key: {e}")
    
#     def is_connected(self) -> bool:
#         """Check if connected to blockchain"""
#         try:
#             return self.w3.is_connected()
#         except Exception:
#             return False
    
#     def get_chain_id(self) -> Optional[int]:
#         """Get chain ID"""
#         try:
#             return self.w3.eth.chain_id
#         except Exception:
#             return None
    
#     def get_account_address(self) -> Optional[str]:
#         """Get account address"""
#         if self.account:
#             return self.account.address
#         return None
    
#     def get_balance(self, address: Optional[str] = None) -> Optional[int]:
#         """Get account balance in wei"""
#         try:
#             addr = address or self.account.address if self.account else None
#             if not addr:
#                 return None
#             return self.w3.eth.get_balance(addr)
#         except Exception:
#             return None
    
#     def hash_data(self, data: str) -> str:
#         """
#         Hash data using keccak256 (SHA-3)
#         Returns hex string of hash
#         """
#         if isinstance(data, str):
#             data = data.encode('utf-8')
#         return Web3.keccak(data).hex()
    
#     def anchor_hash(self, hash_value: str, gas_price: Optional[int] = None,
#                    gas_limit: int = 100000) -> Optional[Dict[str, Any]]:
#         """
#         Anchor a hash on the blockchain using smart contract
#         Returns transaction receipt or None if failed
#         """
#         if not self.contract_address:
#             # If no contract, we can still create a transaction with hash in data
#             return self._anchor_hash_simple(hash_value, gas_price, gas_limit)
        
#         # Use smart contract to anchor hash
#         return self._anchor_hash_contract(hash_value, gas_price, gas_limit)
    
#     def _anchor_hash_simple(self, hash_value: str, gas_price: Optional[int] = None,
#                            gas_limit: int = 100000) -> Optional[Dict[str, Any]]:
#         """
#         Anchor hash using a simple transaction (fallback if no contract)
#         Stores hash in transaction data
#         """
#         if not self.account:
#             raise ValueError("Account not available. Private key required for anchoring.")
        
#         try:
#             # Prepare transaction
#             nonce = self.w3.eth.get_transaction_count(self.account.address)
            
#             # Create transaction with hash in data field
#             transaction = {
#                 'to': self.account.address,  # Send to self (for demo)
#                 'value': 0,
#                 'gas': gas_limit,
#                 'gasPrice': gas_price or self.w3.eth.gas_price,
#                 'nonce': nonce,
#                 'data': '0x' + hash_value.replace('0x', '')[:64]  # Store hash in data
#             }
            
#             # Sign transaction
#             signed_txn = self.w3.eth.account.sign_transaction(transaction, self.private_key)
            
#             # Send transaction
#             tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
#             # Wait for receipt
#             receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
            
#             return {
#                 'tx_hash': receipt['transactionHash'].hex(),
#                 'block_number': receipt['blockNumber'],
#                 'gas_used': receipt['gasUsed'],
#                 'status': receipt['status'],
#                 'hash_anchored': hash_value
#             }
#         except Exception as e:
#             print(f"Error anchoring hash: {e}")
#             return None
    
#     def _anchor_hash_contract(self, hash_value: str, gas_price: Optional[int] = None,
#                              gas_limit: int = 100000) -> Optional[Dict[str, Any]]:
#         """
#         Anchor hash using smart contract
#         Requires contract ABI and address
#         """
#         if not self.contract_address:
#             return self._anchor_hash_simple(hash_value, gas_price, gas_limit)
        
#         # Load contract ABI (simplified version)
#         # In production, load from file or deployment
#         contract_abi = self._get_contract_abi()
        
#         try:
#             # Get contract instance
#             contract = self.w3.eth.contract(
#                 address=Web3.to_checksum_address(self.contract_address),
#                 abi=contract_abi
#             )
            
#             # Prepare transaction
#             nonce = self.w3.eth.get_transaction_count(self.account.address)
            
#             # Call contract function to anchor hash
#             function = contract.functions.anchorHash(hash_value)
#             transaction = function.build_transaction({
#                 'chainId': self.w3.eth.chain_id,
#                 'gas': gas_limit,
#                 'gasPrice': gas_price or self.w3.eth.gas_price,
#                 'nonce': nonce,
#             })
            
#             # Sign transaction
#             signed_txn = self.w3.eth.account.sign_transaction(transaction, self.private_key)
            
#             # Send transaction
#             tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
#             # Wait for receipt
#             receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
            
#             return {
#                 'tx_hash': receipt['transactionHash'].hex(),
#                 'block_number': receipt['blockNumber'],
#                 'gas_used': receipt['gasUsed'],
#                 'status': receipt['status'],
#                 'hash_anchored': hash_value
#             }
#         except Exception as e:
#             print(f"Error anchoring hash with contract: {e}")
#             # Fallback to simple transaction
#             return self._anchor_hash_simple(hash_value, gas_price, gas_limit)
    
#     def verify_hash_anchored(self, hash_value: str, tx_hash: Optional[str] = None) -> bool:
#         """
#         Verify if a hash is anchored on the blockchain
#         If tx_hash is provided, verify the transaction contains the hash
#         """
#         if tx_hash:
#             try:
#                 # Get transaction receipt
#                 receipt = self.w3.eth.get_transaction_receipt(tx_hash)
                
#                 # Check if transaction was successful
#                 if receipt['status'] != 1:
#                     return False
                
#                 # For simple transactions, check data field
#                 tx = self.w3.eth.get_transaction(tx_hash)
#                 if tx['input']:
#                     # Check if hash is in transaction data
#                     hash_in_data = hash_value.replace('0x', '').lower() in tx['input'].hex().lower()
#                     if hash_in_data:
#                         return True
                
#                 # For contract transactions, check events
#                 if self.contract_address:
#                     return self._verify_hash_in_contract(hash_value, receipt)
                
#                 return True
#             except Exception as e:
#                 print(f"Error verifying hash: {e}")
#                 return False
        
#         # Without tx_hash, we can't verify (would need to scan blockchain)
#         return False
    
#     def _verify_hash_in_contract(self, hash_value: str, receipt: Dict) -> bool:
#         """Verify hash in smart contract events"""
#         try:
#             contract_abi = self._get_contract_abi()
#             contract = self.w3.eth.contract(
#                 address=Web3.to_checksum_address(self.contract_address),
#                 abi=contract_abi
#             )
            
#             # Parse events from receipt
#             events = contract.events.HashAnchored().process_receipt(receipt)
            
#             for event in events:
#                 if event['args']['hash'] == hash_value:
#                     return True
            
#             return False
#         except Exception as e:
#             print(f"Error verifying hash in contract: {e}")
#             return False
    
#     def _get_contract_abi(self) -> list:
#         """
#         Get smart contract ABI
#         Simplified version - in production, load from file
#         """
#         return [
#             {
#                 "inputs": [{"internalType": "bytes32", "name": "_hash", "type": "bytes32"}],
#                 "name": "anchorHash",
#                 "outputs": [],
#                 "stateMutability": "nonpayable",
#                 "type": "function"
#             },
#             {
#                 "anonymous": False,
#                 "inputs": [
#                     {"indexed": True, "internalType": "bytes32", "name": "hash", "type": "bytes32"},
#                     {"indexed": False, "internalType": "uint256", "name": "timestamp", "type": "uint256"}
#                 ],
#                 "name": "HashAnchored",
#                 "type": "event"
#             },
#             {
#                 "inputs": [{"internalType": "bytes32", "name": "_hash", "type": "bytes32"}],
#                 "name": "isAnchored",
#                 "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
#                 "stateMutability": "view",
#                 "type": "function"
#             }
#         ]
    
#     def get_transaction_url(self, tx_hash: str) -> str:
#         """Get blockchain explorer URL for transaction"""
#         explorers = {
#             'polygon-mumbai': f'https://mumbai.polygonscan.com/tx/{tx_hash}',
#             'polygon': f'https://polygonscan.com/tx/{tx_hash}',
#             'goerli': f'https://goerli.etherscan.io/tx/{tx_hash}',
#             'sepolia': f'https://sepolia.etherscan.io/tx/{tx_hash}',
#             'mainnet': f'https://etherscan.io/tx/{tx_hash}'
#         }
        
#         return explorers.get(self.network, f'https://etherscan.io/tx/{tx_hash}')

# def create_qr_hash(payload: Dict[str, Any], signature: str) -> str:
#     """
#     Create a hash for QR code anchoring
#     Combines payload and signature
#     """
#     import json
#     # Create canonical JSON of payload
#     payload_str = json.dumps(payload, sort_keys=True, separators=(',', ':'))
#     # Combine payload and signature
#     combined = f"{payload_str}:{signature}"
#     # Hash using keccak256
#     return Web3.keccak(text=combined).hex()

# def anchor_qr_code(blockchain_service: BlockchainService, payload: Dict[str, Any],
#                   signature: str) -> Optional[Dict[str, Any]]:
#     """
#     Anchor a QR code on the blockchain
#     Returns transaction details or None
#     """
#     # Create hash for anchoring
#     hash_value = create_qr_hash(payload, signature)
    
#     # Anchor hash on blockchain
#     result = blockchain_service.anchor_hash(hash_value)
    
#     if result:
#         result['qr_hash'] = hash_value
#         result['explorer_url'] = blockchain_service.get_transaction_url(result['tx_hash'])
    
#     return result

