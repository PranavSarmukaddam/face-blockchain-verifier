// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * EvidenceRegistry
 * Stores a SHA-256 fingerprint (bytes32) of an evidence package,
 * together with its source URL and submission metadata.
 * Deployed on Polygon Amoy testnet (chain ID 80002).
 */
contract EvidenceRegistry {
    struct Evidence {
        bytes32 evidenceHash;
        string  sourceUrl;
        uint256 timestamp;
        address submitter;
        bool    exists;
    }

    mapping(bytes32 => Evidence) private records;

    event EvidenceRegistered(
        bytes32 indexed evidenceHash,
        string          sourceUrl,
        uint256         timestamp,
        address indexed submitter
    );

    /**
     * Register a new evidence fingerprint.
     * Reverts if the same hash has already been registered.
     */
    function registerEvidence(
        bytes32 evidenceHash,
        string calldata sourceUrl
    ) external {
        require(!records[evidenceHash].exists, "Evidence already registered");

        records[evidenceHash] = Evidence({
            evidenceHash: evidenceHash,
            sourceUrl:    sourceUrl,
            timestamp:    block.timestamp,
            submitter:    msg.sender,
            exists:       true
        });

        emit EvidenceRegistered(evidenceHash, sourceUrl, block.timestamp, msg.sender);
    }

    /**
     * Retrieve a registered evidence record.
     * Returns zero values if the hash has not been registered.
     */
    function getEvidence(bytes32 evidenceHash)
        external
        view
        returns (
            bytes32 storedHash,
            string memory sourceUrl,
            uint256 timestamp,
            address submitter,
            bool    exists
        )
    {
        Evidence memory rec = records[evidenceHash];
        return (rec.evidenceHash, rec.sourceUrl, rec.timestamp, rec.submitter, rec.exists);
    }
}
