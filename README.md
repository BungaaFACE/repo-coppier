# Repo Coppier
  
## Description
This tool helps you to sync repositories on different services, such as github-gitlab.  
Currently supports only Github and Gitlab.  
  
## Installation
1. Clone repo `git clone https://github.com/BungaaFACE/repo-coppier`
2. cd into folder and create venv `cd repo-coppier && python -m venv .venv`
3. Install requirements `pip install -r requirements.txt`
4. Rename CONFIG_template.py into CONFIG.py and enter tokens of required git-services `mv CONFIG_template.py CONFIG.py`
5. You are ready to go!
  
### Token creation
  
#### Github
Enter account settings -> Developer settings -> Personal access tokens -> Tokens (classic) -> Generate new token (classic). Enter name of token, expiration date. In scopes check only repo scope.  
![image](https://github.com/user-attachments/assets/0bfdc4d0-5ca2-4404-8699-8cadb14971aa)
  
#### Gitlab
Enter account Preferences -> Access tokens -> Add new token. Enter name of token, expiration date. In scopes check only api.  
![image](https://github.com/user-attachments/assets/66898ff2-84aa-4dd5-88c8-c7a2007745c5)

## Usage
Repo-Coppier can be started manually, automated via gl-runner or gh-action or can be triggered by cron schedule.  
  
Repo-coppier controlled by start command. Basic usage: `python repo-coppier.py sync` or if you want automated way `$project_path/.venv/bin/python $project_path/repo-copper.py sync`  
  
### Action parameters
In example sync means action to do. repo-coppier have 5 possible actions:
- ***sync*** - start to sync repositories
- ***add*** - add new repository to sync
- ***list*** - list all added repositoriees
- ***status*** - check added repositories if they need sync (analog of ***sync*** without action)
- ***-h*** - display help, can be used with action `repo-coppier -h` or `repo-coppier sync -h`
  
### Sub parameters
Actions have sub parameters that are not required but can be used for more flexible start.  
  
#### sync
Action sync has 3 non-reqired parameters.
- ***--repo*** - allows to choose one repo, even if its not added repo-coppier
- ***--origin-service*** or ***-os*** - choose origin git-service wherefrom copy repository, default: github
- ***--destination-service*** or ***-ds*** - choose destionation git-service whereto copy repository, default: gitlab
  
***Examples:***  
  `repo-coppier sync -repo repo-coppier`  
  `repo-coppier sync -os github -ds gitlab`  
  `repo-coppier sync -repo repo-coppier -os gitlab -ds github`  

#### add
Action add have 2 required positional parameters.  
repo-coppier add {service} {repo name}
- ***service*** - origin git-service where original repo locates
- ***repo*** - name of repository you want to copy. Its preferable to be only name, not link, but link might work too.

***Example:*** `repo-coppier add github repo-coppier`

#### list
Action have 1 non-required positional parameter to specify which origin git-service to show.  
  
***Example:*** `repo-coppier list github`

#### status
Action status have same parameters as ***sync***

### Development
  
#### Suggestions & issues
You can create issue with suggestion or issue and i will look into it.  

#### Open-source development
You can create new git-service by yourself.
Create another file with the name of git-service and create git-service client based on parent APIClient class.  
It is abstact class so you wont miss anything.  
One more thing to do before pull request is to add your git-service client class into SUPPORTED_SERVICES['git-service-name'] = your_client_class in main file.
