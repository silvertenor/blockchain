# GEthereum Project

## Installation
1. Clone repository into current working directory:
    - ```git clone https://github.com/silvertenor/blockchain```
    - Can also download and extract zip file
2. Set up Conda environment
    - ```conda env create -f environment.yml```
    - Note: Conda environment was exported from MacOS Ventura machine. If using windows or a different version of MacOS, may need to manually install all required packages (web3, PyQt, etc...)
3. Activate conda environment
    - ```conda activate block```


## Running the App
1. Development mode:
    - ```python app.py```
2. Deployment mode:
    - ```pyinstaller app.spec``` builds the app.
    - Look in the ```dist``` folder for an executable version of the app.
    - If on Mac, can run ```./dmgBuilder.sh``` to build a DMG file of the application and install it to the system.

## Structure
- All relevant backend modules in the ```source/modules``` folder
- XML file being checked is located in ```source/logfiles```
- Symmetric key found in ```source/secrets```
- All environment variables and Solidity smart contract are found in the root-level of the ```source``` folder
- Front-end design and entrypoint of program found in ```app.py```. This is similar to a ```main.c``` file
- Specifications for building the distributable file (executable) are found in ```app.spec```
- Conda environment packages found in ```environment.yml```
- Logos for app icon found in root level of project

## Issues/Comments
Please email all of the following developers with any questions or issues:
    - Devin Lane: ```ddlane@g.clemson.edu```
    - Paul Cunningham: ```pcunni2@g.clemson.edu```
    - Molly Ward: ```msward@g.clemson.edu```