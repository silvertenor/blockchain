// SPDX-License-Identifier: MIT

pragma solidity 0.6.0;

contract HashStorage {
    struct Hash {
        // assosiate date/time with hash number
        string time;
        string hashNumber;
        string userID;
        string previousTx;
    }

    Hash hash;

    mapping(string => string) public idToHash; //used to map id to hash, so you can get hash using time
    mapping(string => string) public idToTime;

    function addHash(
        string memory _time,
        string memory _hashNumber,
        string memory _userID,
        string memory _previousTx
    ) public {
        hash = Hash(_time, _hashNumber, _userID, _previousTx);
        idToHash[_userID] = _hashNumber; //use time to get hash
        idToTime[_userID] = _time;
    }

    function retrieve()
        public
        view
        returns (
            string memory,
            string memory,
            string memory,
            string memory
        )
    {
        return (hash.hashNumber, hash.time, hash.userID, hash.previousTx);
    }
}
