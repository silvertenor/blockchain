// SPDX-License-Identifier: MIT

pragma solidity 0.6.0;

contract HashStorage {
    struct Hash {
        // assosiate date/time with hash number
        string time;
        string hashNumber;
        // string Signature;
    }

    Hash hash;

    mapping(string => string) public dateToHash; //used to map time to hash, so you can get hash using time

    function addHash(string memory _time, string memory _hashNumber) public {
        hash = Hash(_time, _hashNumber);
        dateToHash[_time] = _hashNumber; //use time to get hash
    }

    function store(string memory _hashNumber) public {
        hash.hashNumber = _hashNumber;
    }

    function retrieve() public view returns (string memory) {
        return hash.hashNumber;
    }
}
