// SPDX-License-Identifier: MIT

pragma solidity 0.6.0;

contract HashStorage {
    // Creates structure to hold information from configuration (xml) file
    struct Hash {
        string time;
        string hashNumber;
        string userID;
        string previousTx;
    }

    Hash hash; // Creates a structure Hash called hash

    // Initiate mapping to use computer ID to find date/time and configuration hash
    mapping(string => string) public idToHash;
    mapping(string => string) public idToTime;

    // This function adds values to a structure hash,
    // that includes time of change, hash of configuration file, and computer ID
    function addHash(
        string memory _time,
        string memory _hashNumber,
        string memory _userID,
        string memory _previousTx
    ) public {
        hash = Hash(_time, _hashNumber, _userID, _previousTx);
        // Will be used in the future to find hash of configuration file
        // and time of change from a specific user
        idToHash[_userID] = _hashNumber;
        idToTime[_userID] = _time;
    }

    // Retrieves the hash number and time of change when called within Python script
    function retrieve()
        public
        view
        returns (
            string memory,
            string memory,
            string memory
        )
    {
        return (hash.hashNumber, hash.time, hash.userID);
    }
}
