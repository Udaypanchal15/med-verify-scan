# Blockchain Integration Guide

## Overview

The blockchain integration provides immutability and auditability for QR code issuances by anchoring issuance hashes on the Ethereum/Polygon blockchain. This ensures that QR codes cannot be tampered with and provides a permanent record of all issuances.

## Features

- **Hash Anchoring**: Anchor QR code issuance hashes on blockchain
- **Transaction Verification**: Verify that hashes are anchored on blockchain
- **Smart Contract Support**: Use smart contracts for efficient hash storage
- **Multiple Networks**: Support for Polygon Mumbai, Goerli, Sepolia, and mainnet
- **Explorer Integration**: Generate blockchain explorer URLs for transactions

## Setup

### 1. Environment Variables

Add to your `.env` file:

```env
# Blockchain Configuration
ETH_RPC_URL=https://polygon-mumbai.g.alchemy.com/v2/YOUR_API_KEY
BLOCKCHAIN_PRIVATE_KEY=your-private-key-for-anchoring
BLOCKCHAIN_CONTRACT_ADDRESS=0x...  # Optional: Smart contract address
BLOCKCHAIN_NETWORK=polygon-mumbai
```

### 2. Get RPC URL

#### Polygon Mumbai (Recommended for testing)
1. Sign up at [Alchemy](https://www.alchemy.com/) or [Infura](https://www.infura.io/)
2. Create a new app
3. Select "Polygon" network and "Mumbai" testnet
4. Copy the HTTP URL

#### Goerli/Sepolia (Ethereum testnets)
1. Similar process but select "Ethereum" network
2. Choose "Goerli" or "Sepolia" testnet

### 3. Get Testnet Tokens

#### Polygon Mumbai
- Use [Polygon Faucet](https://faucet.polygon.technology/)
- Request MATIC tokens for gas fees

#### Goerli/Sepolia
- Use [Goerli Faucet](https://goerlifaucet.com/) or [Sepolia Faucet](https://sepoliafaucet.com/)
- Request ETH tokens for gas fees

### 4. Generate Wallet

```python
from eth_account import Account

# Generate new account
account = Account.create()
private_key = account.key.hex()
address = account.address

print(f"Private Key: {private_key}")
print(f"Address: {address}")
```

**⚠️ IMPORTANT**: Store private key securely. Never commit to version control.

## Smart Contract Deployment

### 1. Compile Contract

```bash
# Install Solidity compiler
npm install -g solc

# Compile contract
solc --abi --bin contracts/HashAnchor.sol -o build/
```

### 2. Deploy Contract

Using Remix IDE:
1. Go to [Remix IDE](https://remix.ethereum.org/)
2. Create new file `HashAnchor.sol`
3. Paste contract code
4. Compile contract
5. Deploy to testnet (Mumbai, Goerli, etc.)
6. Copy contract address

Using Hardhat/Truffle:
```javascript
// deployment script
const HashAnchor = artifacts.require("HashAnchor");

module.exports = function(deployer) {
  deployer.deploy(HashAnchor);
};
```

### 3. Update Environment

After deployment, update `.env`:
```env
BLOCKCHAIN_CONTRACT_ADDRESS=0xYourDeployedContractAddress
```

## Usage

### 1. Anchor QR Code

```python
from services.qr_service import QRCodeService

# Initialize service
qr_service = QRCodeService(seller_private_key_path='./keys/private_key.pem')

# Create signed QR code (automatically anchored if blockchain available)
qr_code = qr_service.create_signed_qr(
    medicine_id="med-123",
    seller_id="seller-123",
    issued_by="user-123"
)

# QR code includes blockchain transaction hash
print(f"Blockchain TX: {qr_code['blockchain_tx']}")
print(f"Explorer URL: {qr_code['blockchain_explorer_url']}")
```

### 2. Verify QR Code

```python
# Verify QR code (includes blockchain verification)
verification_result = qr_service.verify_qr_code(
    qr_data=qr_data,
    public_key_pem=public_key_pem
)

# Check blockchain anchoring
if verification_result['blockchain_anchored']:
    print("✅ QR code is anchored on blockchain")
    print(f"Explorer URL: {verification_result['details']['blockchain_explorer_url']}")
else:
    print("❌ QR code not found on blockchain")
```

### 3. Manual Hash Anchoring

```python
from services.blockchain import BlockchainService, create_qr_hash

# Initialize blockchain service
blockchain = BlockchainService(
    rpc_url="https://polygon-mumbai.g.alchemy.com/v2/YOUR_API_KEY",
    private_key="your-private-key",
    contract_address="0x...",
    network="polygon-mumbai"
)

# Create hash from payload and signature
hash_value = create_qr_hash(payload, signature)

# Anchor hash
result = blockchain.anchor_hash(hash_value)

if result:
    print(f"Transaction Hash: {result['tx_hash']}")
    print(f"Block Number: {result['block_number']}")
    print(f"Explorer URL: {blockchain.get_transaction_url(result['tx_hash'])}")
```

### 4. Verify Hash

```python
# Verify hash is anchored
is_anchored = blockchain.verify_hash_anchored(hash_value, tx_hash)

if is_anchored:
    print("✅ Hash is anchored on blockchain")
else:
    print("❌ Hash not found on blockchain")
```

## API Endpoints

### GET /blockchain/info
Get blockchain network information.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "message": "Blockchain information retrieved successfully",
  "data": {
    "available": true,
    "connected": true,
    "chain_id": 80001,
    "network": "polygon-mumbai",
    "account": "0x...",
    "balance": 1000000000000000000
  }
}
```

### POST /blockchain/verify
Verify if a hash is anchored on blockchain.

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "hash": "0x...",
  "tx_hash": "0x..."  // Optional
}
```

**Response:**
```json
{
  "message": "Hash verification completed",
  "data": {
    "hash": "0x...",
    "anchored": true,
    "tx_hash": "0x..."
  }
}
```

## Smart Contract

### HashAnchor Contract

The `HashAnchor.sol` contract provides:
- `anchorHash(bytes32)`: Anchor a hash on blockchain
- `isAnchored(bytes32)`: Check if hash is anchored
- `getHashTimestamp(bytes32)`: Get timestamp when hash was anchored
- `anchorHashesBatch(bytes32[])`: Batch anchor multiple hashes
- `verifyHashes(bytes32[])`: Verify multiple hashes

### Events

- `HashAnchored(bytes32 indexed hash, uint256 timestamp)`: Emitted when hash is anchored
- `HashVerified(bytes32 indexed hash, bool exists)`: Emitted when hash is verified

## Gas Costs

### Polygon Mumbai (Testnet)
- Simple transaction: ~21,000 gas
- Contract transaction: ~50,000-100,000 gas
- Gas price: ~30-100 gwei
- Cost: Very low (testnet tokens free)

### Mainnet
- Gas price varies with network congestion
- Monitor gas prices before anchoring
- Consider batch operations for efficiency

## Best Practices

### 1. Gas Management
- Monitor gas prices before anchoring
- Use batch operations when possible
- Consider using Layer 2 solutions (Polygon) for lower costs

### 2. Error Handling
- Always handle blockchain errors gracefully
- Provide fallback mechanisms if blockchain is unavailable
- Log all blockchain operations for audit

### 3. Security
- Never expose private keys
- Use environment variables for sensitive data
- Implement rate limiting for blockchain operations
- Monitor for suspicious activity

### 4. Cost Optimization
- Batch multiple hashes in single transaction
- Use efficient gas pricing strategies
- Consider off-chain solutions for high-volume operations

## Troubleshooting

### Connection Issues
- Verify RPC URL is correct
- Check network connectivity
- Ensure testnet tokens are available for gas

### Transaction Failures
- Check account has sufficient balance for gas
- Verify gas limit is sufficient
- Check contract address is correct

### Verification Failures
- Ensure transaction hash is correct
- Verify hash format matches
- Check if transaction is confirmed (wait for blocks)

## Network Information

### Polygon Mumbai
- Chain ID: 80001
- RPC URL: https://polygon-mumbai.g.alchemy.com/v2/YOUR_API_KEY
- Explorer: https://mumbai.polygonscan.com
- Faucet: https://faucet.polygon.technology/

### Goerli
- Chain ID: 5
- RPC URL: https://goerli.infura.io/v3/YOUR_API_KEY
- Explorer: https://goerli.etherscan.io
- Faucet: https://goerlifaucet.com/

### Sepolia
- Chain ID: 11155111
- RPC URL: https://sepolia.infura.io/v3/YOUR_API_KEY
- Explorer: https://sepolia.etherscan.io
- Faucet: https://sepoliafaucet.com/

## References

- [Web3.py Documentation](https://web3py.readthedocs.io/)
- [Polygon Documentation](https://docs.polygon.technology/)
- [Ethereum Documentation](https://ethereum.org/en/developers/)
- [Smart Contract Security](https://consensys.github.io/smart-contract-best-practices/)



