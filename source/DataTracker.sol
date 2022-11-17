// SPDX-License-Identifier: MIT

pragma solidity 0.6.0;

/**
 * Library for managing addresses assigned to a Role.
 */
library Roles {
    struct Role {
        mapping(address => bool) bearer;
    }

    /**
     * Give an account access to this role.
     */
    function add(Role storage role, address account) internal {
        require(!has(role, account), "Roles: account already has role");
        role.bearer[account] = true;
    }

    /**
     * Remove an account's access to this role.
     */
    function remove(Role storage role, address account) internal {
        require(has(role, account), "Roles: account does not have role");
        role.bearer[account] = false;
    }

    /**
     * Check if an account has this role.
     */
    function has(Role storage role, address account)
        internal
        view
        returns (bool)
    {
        require(account != address(0), "Roles: account is the zero address");
        return role.bearer[account];
    }
}

contract DataTracker {
    using Roles for Roles.Role;

    Roles.Role private users;
    Roles.Role private admins;

    address[] private allAdmins;
    address[] private allUsers;

    constructor() public {
        admins.add(msg.sender);
        users.add(msg.sender);
        allAdmins.push(msg.sender);
        allUsers.push(msg.sender);
    }

    function addUser(address _newUser) external onlyAdmins {
        users.add(_newUser);
        allUsers.push(_newUser);
    }

    function addAdmin(address _newAdmin) external onlyAdmins {
        admins.add(_newAdmin);
        allAdmins.push(_newAdmin);
    }

    function removeAdmin(address _oldAdmin) external onlyAdmins {
        admins.remove(_oldAdmin);
        uint256 i = 0;
        while (allAdmins[i] != _oldAdmin) {
            i++;
        }
        while (i < allAdmins.length - 1) {
            allAdmins[i] = allAdmins[i + 1];
            i++;
        }
        allAdmins.pop();
    }

    function removeUser(address _oldUser) external onlyAdmins {
        users.remove(_oldUser);
        uint256 i = 0;
        while (allUsers[i] != _oldUser) {
            i++;
        }
        while (i < allUsers.length - 1) {
            allUsers[i] = allUsers[i + 1];
            i++;
        }
        allUsers.pop();
    }

    function viewAdmins() public view onlyAdmins returns (address[] memory) {
        return (allAdmins);
    }

    function viewUsers() public view onlyAdmins returns (address[] memory) {
        return (allUsers);
    }

    modifier onlyUsers() {
        require(users.has(msg.sender) == true, "Must have user title");
        _;
    }

    modifier onlyAdmins() {
        require(admins.has(msg.sender) == true, "Must have admin title");
        _;
    }

    struct ControllerData {
        // assosiate date/time with hash number
        string configChanged;
        string hashNumber;
        string fileDiff;
        string userID;
        string domain;
        string previousTx;
    }

    ControllerData config;

    mapping(string => string) public idToHash; //used to map id to hash, so you can get hash using time
    mapping(string => string) public idToTime;

    function addConfig(
        string memory _configChanged,
        string memory _hashNumber,
        string memory _fileDiff,
        string memory _userID,
        string memory _domain,
        string memory _previousTx
    ) public onlyAdmins {
        config = ControllerData(
            _configChanged,
            _hashNumber,
            _fileDiff,
            _userID,
            _domain,
            _previousTx
        );
        // Will be used in the future to find hash of configuration file
        // and time of change from a specific user
        idToHash[_userID] = _hashNumber;
        idToTime[_userID] = _configChanged;
    }

    // Retrieves the hash number and time of change when called within Python script
    function retrieve()
        public
        view
        onlyAdmins
        returns (
            string memory,
            string memory,
            string memory,
            string memory,
            string memory
        )
    {
        return (
            config.hashNumber,
            config.configChanged,
            config.userID,
            config.domain,
            config.previousTx
        );
    }
}
