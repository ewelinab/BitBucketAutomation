# Bitbucket Automation


## Build project

To build the project, follow the steps below to set up a Python virtual environment and install the dependencies:

```bash
python -m venv venv
source .venv/bin/activate
pip install -r requirements.txt
```


## How to run

### Prerequisites

Before running the tests, ensure the following environment variables are added either as system environment variables or in the .env file:

```bash
BITBUCKET_USERNAME=""
BITBUCKET_APP_PASSWORD=""
BITBUCKET_PASSWORD=""
BITBUCKET_USERNAME_EMAIL=""
BITBUCKET_WORKSPACE=""
```

### Commands
To run the tests, use the following command:

```bash
pytest -n 4 --alluredir .tmp/allure-results
allure serve .tmp/allure-results
```


## Details about sections

### API Testing

The official Atlassian Bitbucket API documentation is used for testing the repository API.
API documentation: [Bitbucket API Docs](https://developer.atlassian.com/cloud/bitbucket/rest/api-group-repositories/#api-repositories-workspace-repo-slug-post)



### Git Operations

These tests require Git to be installed on your operating system. To install Git on Ubuntu, run:

```bash
apt install git
```

The tests create intermediate directories in the git_operation/.tmp folder (which is specified in .gitignore).



### UI Testing

Some UI tests are performed using API calls to test assumptions or verify the correctness of operations. 
It is mandatory that the API works correctly for these tests.



### Parallel run

`pytest-xdist` is used to run multiple tests in parallel.
Current parallel test streams allow the following: 
- API tests
- GIT operation tests
- UI tests (UI tests can also be run in parallel internally, as the logic is made orthogonal, 
allowing for concurrent execution within the same scope function.

To run tests in parallel, use the following command:

```bash
pytest -n 4
```


### Reporting

To generate and view reports using Allure, follow these steps:
1. Install Allure by following the official installation guide: [Allure Installation](https://allurereport.org/docs/install/).
2. Run the tests with Allure report output:

```bash
pytest --alluredir .tmp/allure-results
allure serve .tmp/allure-results
```



