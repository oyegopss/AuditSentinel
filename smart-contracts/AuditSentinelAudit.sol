// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title AuditSentinelAudit
 * @dev Stores audit log hashes and timestamps for AI actions on Polygon testnet.
 *
 * The backend hashes each high-risk AI action (SHA256 of action + timestamp + user)
 * and records the hash and timestamp on-chain for immutability and verification.
 */
contract AuditSentinelAudit {
    struct AIActionAuditLog {
        bytes32 actionHash;   // SHA256 hash of the AI action (action|timestamp|user)
        uint256 timestamp;    // When the action was logged (block.timestamp)
        address logger;       // Address that submitted the log (backend relayer)
    }

    event AIActionLogged(
        bytes32 indexed actionHash,
        uint256 indexed timestamp,
        address indexed logger
    );

    AIActionAuditLog[] private _auditLogs;

    /**
     * @notice Store an audit log hash and timestamp for an AI action.
     * @param actionHash The SHA256 hash of the action (32 bytes); pass as bytes32.
     * @param timestamp Optional off-chain timestamp; stored for reference (on-chain ts used in event).
     */
    function logAIAction(bytes32 actionHash, uint256 timestamp) external {
        uint256 ts = timestamp > 0 ? timestamp : block.timestamp;
        _auditLogs.push(AIActionAuditLog({
            actionHash: actionHash,
            timestamp: ts,
            logger: msg.sender
        }));
        emit AIActionLogged(actionHash, ts, msg.sender);
    }

    /**
     * @notice Get a single audit log entry by index.
     */
    function getAuditLog(uint256 index) external view returns (AIActionAuditLog memory) {
        require(index < _auditLogs.length, "AuditSentinel: index out of range");
        return _auditLogs[index];
    }

    /**
     * @notice Total number of audit log entries stored.
     */
    function totalAuditLogs() external view returns (uint256) {
        return _auditLogs.length;
    }
}
