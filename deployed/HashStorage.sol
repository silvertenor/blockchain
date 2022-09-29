// SPDX-License-Identifier: MIT

pragma solidity 0.6.0;

contract HashStorage {
    // pull in hash number;
    string hashNumber;
    struct Hash {
        // assosiate date/time with hash number
        string time;
        string hashNumber;
    }
    Hash[] public hash; //array for list of hashes
    mapping(string => string) public dateToHash; //used to map time to hash, so you can get hash using time

    function store(string memory _hashNumber) public {
        hashNumber = _hashNumber;
    }

    function retrieve() public view returns (string memory) {
        return hashNumber;
    }

    function addHash(string memory _time, string memory _hashNumber) public {
        hash.push(Hash(_time, _hashNumber)); //append to  Hash[] array
        dateToHash[_time] = _hashNumber; //use time to get hash
    }
}
