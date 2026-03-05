// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title AuditSentinelAudit
 * @dev Minimal audit logging contract for Polygon testnet.
 *
 * Each approved high‑risk AI action can be logged on‑chain by the backend.
 * The contract stores a compact record and emits an event to make it easy
 * to index from block explorers or off‑chain indexers.
 */
contract AuditSentinelAudit {
    struct AuditEntry {
        bytes32 actionHash;
        uint256 timestamp;
        address actor;
        string description;
        string txId;
    }

    event ActionLogged(
        bytes32 indexed actionHash,
        uint256 indexed timestamp,
        address indexed actor,
        string description,
        string txId
    );

    AuditEntry[] private _entries;

    function logAction(
        bytes32 actionHash,
        string calldata description,
        string calldata txId
    ) external {
        uint256 ts = block.timestamp;
        AuditEntry memory entry = AuditEntry({
            actionHash: actionHash,
            timestamp: ts,
            actor: msg.sender,
            description: description,
            txId: txId
        });

        _entries.push(entry);
        emit ActionLogged(actionHash, ts, msg.sender, description, txId);
    }

    function getEntry(uint256 index) external view returns (AuditEntry memory) {
        require(index < _entries.length, "out of range");
        return _entries[index];
    }

    function totalEntries() external view returns (uint256) {
        return _entries.length;
    }
}

