# Smart Contracts

## HashAnchor.sol

Smart contract for anchoring QR code issuance hashes on the blockchain.

### Features

- Anchor individual hashes
- Batch anchor multiple hashes
- Verify if hash is anchored
- Get timestamp when hash was anchored
- Events for hash anchoring and verification

### Deployment

1. Compile the contract using Solidity compiler (0.8.0+)
2. Deploy to your preferred network (Polygon Mumbai recommended for testing)
3. Update `BLOCKCHAIN_CONTRACT_ADDRESS` in `.env` file

### Usage

```solidity
// Anchor a hash
hashAnchor.anchorHash(keccak256("your-data"));

// Check if hash is anchored
bool anchored = hashAnchor.isAnchored(keccak256("your-data"));

// Get timestamp
uint256 timestamp = hashAnchor.getHashTimestamp(keccak256("your-data"));
```

### Gas Costs

- `anchorHash`: ~50,000 gas
- `isAnchored`: ~2,100 gas (view function)
- `getHashTimestamp`: ~2,100 gas (view function)
- `anchorHashesBatch`: ~50,000 gas per hash (more efficient for multiple hashes)

### Security

- Contract is non-upgradeable (immutable)
- No admin functions (fully decentralized)
- Prevents duplicate hash anchoring
- Events for audit trail

### Testing

Test the contract using Remix IDE or Hardhat/Truffle:

```javascript
// Hardhat test example
const HashAnchor = await ethers.getContractFactory("HashAnchor");
const hashAnchor = await HashAnchor.deploy();
await hashAnchor.deployed();

const hash = ethers.utils.keccak256(ethers.utils.toUtf8Bytes("test"));
await hashAnchor.anchorHash(hash);
const isAnchored = await hashAnchor.isAnchored(hash);
expect(isAnchored).to.be.true;
```



