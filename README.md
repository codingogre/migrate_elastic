# Overview
This script is meant to be a one stop shop to migrate *EVERYTHING* from one Elastic cluster to another.  The initial version migrates native users, roles, and role mappings.  Passwords are generated using the XKCD-style (https://xkcd.com/936/) passphrase.  If a word dictionary file doesn't exist a random 12 digit one is generated.

# Installation
pip -r requirements.txt

#### .env file
There is an .env file to put the source cluster API key, the source cluster URL, the target cluster API key, and the target cluster URL.  Put the .env file in the same directory as the python script.  Here is an example:
```console
# Source Elasticsearch cluster
SOURCE_ENDPOINT='https://sandbox.es.eastus2.azure.elastic-cloud.com'
SOURCE_API_KEY='bkhNUUg0NEJLXFFiTUpITDRITlk6aUtyV2ViLVNSSHFub184OXo5UURMZw=='

# Target Elasticsearch cluster
TARGET_ENDPOINT='https://migration-test.es.us-east-2.aws.elastic-cloud.com'
TARGET_API_KEY='TkdfME1ZNEOGWU1kazJiU2JVemo6UEN6MUN3d3JUN3llWUhRTVFXZWxKUQ=='
```

# Help
Help can be printed with the -h option.  Here is an example:
```console
python ./migrate_elastic.py -h 
usage: migrate_elastic.py [-h] [-a] [-u] [-r] [-rm]

Migrates all data and settings from one Elastic Cluster to another

options:
  -h, --help            show this help message and exit
  -a, --all             Synchronize everything (users, roles, kibana objects,
                        data)
  -u, --users           Synchronize *enabled* native users
  -r, --roles           Synchronize roles that are *not* reserved
  -rm, --role_mappings  Synchronize role mappings that are *enabled*

Process finished with exit code 1
```
