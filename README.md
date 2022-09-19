# GE BLockchain Cybersecurity Project
</hr>

## Git Workflow

1. To clone this repository, make sure you have `git` installed to your computer. Run the following in your command line:
    - `git clone https://github.com/silvertenor/blockchain`
    - `cd blockchain`
2. Now that you are inside the repository, make changes or additions to the code by checking out a *feature branch* and pushing your changes to GitHub:
    - `git branch <feature name or username here>`
    - `git checkout <same name from above step>`
    - Make changes/additions to code; once satisfied, make sure to save all files
    - Add all files to staging and commit them so they are saved: `git add . && git commit -m "commit message here"`
    - Push changes to your branch (**not main**) in remote repository: `git push origin <branch name>:<branch name>`
3. Once you have pushed code to your branch, create a "pull request" on GitHub for collaborators to view:
    - Make sure you have notifications active to receive an email when someone creates a pull request, as shown [here](https://stackoverflow.com/questions/62421084/how-to-i-get-github-to-notify-me-of-review-requests).
    - Create the pull request and assign appropriate persons as shown [here](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request). This step allows those who are working on the project with you to test your code before it is merged into the "main" branch.
    - Once all have approved the pull request, merge it into the main branch using the GitHub website.

## Instructions for Setting Up Virtual Environment, Ganache, etc...

1. Download Anaconda (or Miniconda) for your OS and run installer
    - [Anaconda Website](https://www.anaconda.com/products/distribution)
2. Set up environment
    - ```conda env create -f environment.yml```
    - ```conda activate block```
3. Install and run Ganache
    - [Ganache Website](https://trufflesuite.com/ganache/)
    - Open app and click quickstart
    - change ```my_address``` in ```deploy.py``` to match one of the account numbers
    - change ```PRIVATE_KEY``` in ```.env``` to match corresponding private key
4. Run the code!
    - ```python deploy.py```
    

## Instructions for starting Jupyter Lab (easy development)
1. Launch
    - ```jupyter lab```


**Thank you for reading!**
