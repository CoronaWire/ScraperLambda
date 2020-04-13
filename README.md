# ScraperLambda
Scraper and AWS Aurora Storage Writer - AWS Lambda Instance
Language: python3.7

### Environment Setup
Google Cloud Auth API requires a Service account when gaining access to the cloud instances via local scripts. This environment variable will allow you to run and debug the python scripts locally with google cloud sdk. You might not need this.

`$ export GOOGLE_APPLICATION_CREDENTIALS="/Users/sitefeng/Documents/COVID/GCP_MasterDataManagerServicePrivateKey.json"`

Ping Si Te for GCP_MasterDataManagerServicePrivateKey.json


### To run all crawlers
`pipenv install --skip-lock`
`pipenv run python lambda_function.py`
`python3 lambda_function.py`

This is the file that AWS Lambda instance will run

### To run a crawler individually
`$ pipenv shell`
`$ scrapy runspider whoCrawler.py -o whoCrawler.json`



### Connecting to Google Cloud PostgreSQL Database
First, put your local machines public IP address into Google Cloud SQL web console

#### CLI Command for connection debugging
`$ gcloud sql connect <database-name> --user=postgres`

eg:
`$ gcloud sql connect stagingdb --user=postgres`

Pwd is posted on our team Notion page, under Engineering

[More info](https://cloud.google.com/sdk/gcloud/reference/sql/databases/list)


### Commonly used SQL Commands
Show all tables
```
SELECT * FROM pg_catalog.pg_tables
WHERE
   schemaname != 'pg_catalog'
AND schemaname != 'information_schema';
```

Show all records in ModerationTable
`SELECT * FROM ModerationTable;`

Delete Records
`DELETE FROM ModerationTable WHERE ARTICLE_ID='article1';`

Force Delete Table
`DROP TABLE ModerationTable`

Show how many records are there
`SELECT COUNT(ARTICLE_ID) FROM ModerationTable;`

### When modifying the AWS Lambda instance (Deprecated)
Note: AWS Lambda instances do not contain python packages that are installed locally. Therefore, python scripts cannot be zipped and uploaded directly.

Instead, the most robust way is to use `virtualenv`, with the follwing steps. Inspired by [AWS Lambda Doc](https://docs.aws.amazon.com/lambda/latest/dg/python-package.html)

Unfortunately virtualenv doesnt work with `datetime` component, so we must setup an EC2 instance, use `scp` to transfer files to it, setup the environment, and scp back the installed python packages. It must be done with pure determination along with trial and error. Here are relevant commands:

Ask Si Te Feng for ScraperKey.pem

First, copy the project to the new EC2 instance:
`scp -i ~/Documents/COVID/ScraperKey.pem -r ~/Documents/COVID/ScraperLambda/ ec2-user@ec2-3-15-32-244.us-east-2.compute.amazonaws.com:/home/ec2-user/ScraperLambda/`

`ssh -i ~/Documents/COVID/ScraperKey.pem ec2-user@ec2-3-15-32-244.us-east-2.compute.amazonaws.com`

Then, install pip
`aws$ curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py`
`aws$ python get-pip.py`

Then, install all `virtualenv` and
`aws$ python -m pip install --user virtualenv`

Then, activate virtualenv
https://docs.aws.amazon.com/lambda/latest/dg/python-package.html
(With a Virtual Environment) section
`virtualenv v-env`
`source v-env/bin/activate` | `deactivate`

Now, install all project dependencies in the virtual environment
`aws$ pip install --user scrapy` ...

try running the lambda function in EC2 to see if it works,
pip install all the missing packages as errors show up  
`pip install --upgrade pyasn1-modules`  
`pip list`

Then, zip the v-env folder and send it back to your local computer
`aws$ zip -r9 v-env.zip ./v-env`

`$ scp -i ~/Documents/COVID/ScraperKey.pem -r ec2-user@ec2-3-15-32-244.us-east-2.compute.amazonaws.com:/home/ec2-user/ScraperLambda/v-env.zip ~/Documents/COVID/ScraperLambda/v-env.zip`

Finally, run `sh generateAWSZip.sh` to create a new zip file containing all py scripts in the parent directory. Upload that to AWS Lambda webb console


Reference:
https://davidhamann.de/2017/01/27/import-issues-running-python-aws-lambda/

### Out-dated `virtualenv` instructions

- If adding a new dependency (import) to a file, the dependency must be updated and rezipped from `virtualenv`. Follow the instruction in the link.

- Do `sudo pip install --target ./package <MODULE_NAME>` as well, so locally it still works the same way

- Use `sh generateAWSZip.sh` to create a new zip file containing all py scripts in the parent directory.

- Upload the Zip file to the AWS Lambda web console


#### Other Commands
Troubleshooting when installing virtualenv using pip3

```
pip install -U pip
sudo pip3 install virtualenv --user
sudo /usr/bin/easy_install --install-dir /Users/sitefeng/Library/Python/3.7/lib/python/site-packages/ virtualenv
```

virtualenv should be in /Users/<username>/Library/Python/3.7/lib/python/site-packages (20.0.16)

In python, print out all class properties and methods

```
print(dir(service))
```

Switching between OpenSSL 1.0.2 and 1.1.0 `brew switch openssl 1.0.2s`. It's causing a lot of issues with pip recently
