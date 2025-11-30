// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title HashAnchor
 * @dev Smart contract for anchoring QR code issuance hashes on blockchain
 * Provides immutability and auditability for medicine QR codes
 */
contract HashAnchor {
    // Mapping to store anchored hashes
    mapping(bytes32 => bool) private anchoredHashes;
    
    // Mapping to store hash timestamps
    mapping(bytes32 => uint256) private hashTimestamps;
    
    // Event emitted when a hash is anchored
    event HashAnchored(bytes32 indexed hash, uint256 timestamp);
    
    // Event emitted when hash is verified
    event HashVerified(bytes32 indexed hash, bool exists);
    
    /**
     * @dev Anchor a hash on the blockchain
     * @param _hash The hash to anchor (bytes32)
     */
    function anchorHash(bytes32 _hash) public {
        require(_hash != bytes32(0), "Hash cannot be zero");
        require(!anchoredHashes[_hash], "Hash already anchored");
        
        anchoredHashes[_hash] = true;
        hashTimestamps[_hash] = block.timestamp;
        
        emit HashAnchored(_hash, block.timestamp);
    }
    
    /**
     * @dev Check if a hash is anchored
     * @param _hash The hash to check
     * @return true if hash is anchored, false otherwise
     */
    function isAnchored(bytes32 _hash) public view returns (bool) {
        return anchoredHashes[_hash];
    }
    
    /**
     * @dev Get the timestamp when a hash was anchored
     * @param _hash The hash to check
     * @return timestamp when hash was anchored, or 0 if not anchored
     */
    function getHashTimestamp(bytes32 _hash) public view returns (uint256) {
        return hashTimestamps[_hash];
    }
    
    /**
     * @dev Batch anchor multiple hashes (gas efficient)
     * @param _hashes Array of hashes to anchor
     */
    function anchorHashesBatch(bytes32[] memory _hashes) public {
        for (uint256 i = 0; i < _hashes.length; i++) {
            if (_hashes[i] != bytes32(0) && !anchoredHashes[_hashes[i]]) {
                anchoredHashes[_hashes[i]] = true;
                hashTimestamps[_hashes[i]] = block.timestamp;
                emit HashAnchored(_hashes[i], block.timestamp);
            }
        }
    }
    
    /**
     * @dev Verify multiple hashes at once
     * @param _hashes Array of hashes to verify
     * @return Array of booleans indicating if each hash is anchored
     */
    function verifyHashes(bytes32[] memory _hashes) public view returns (bool[] memory) {
        bool[] memory results = new bool[](_hashes.length);
        for (uint256 i = 0; i < _hashes.length; i++) {
            results[i] = anchoredHashes[_hashes[i]];
        }
        return results;
    }
}



