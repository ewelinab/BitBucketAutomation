# BitBucketAutomation


## Build project

```bash
python -m venv venv
source .venv/bin/activate
pip install -r requirements.txt
```


## Prerequsite

Need to add env variable either as system env, or into .env file

```bash
BITBUCKET_USERNAME=""
BITBUCKET_APP_PASSWORD=""
BITBUCKET_PASSWORD=""
BITBUCKET_USERNAME_EMAIL=""
BITBUCKET_WORKSPACE=""
```



## API testing1

We will use docs from 
https://developer.atlassian.com/cloud/bitbucket/rest/api-group-repositories/#api-repositories-workspace-repo-slug-post


## Git operations

Those test require git to be installed into os.

```bash
apt install git
```

Those test will create intermediate directories in git_operation/.tmp file (which is specified in .gitignore)


## UI testing

I will use API calls to test some assumptions or test correctness of some operation.
So our assumption is that API working correctly is mandatory for those tests.
