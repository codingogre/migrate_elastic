from dotenv import load_dotenv
import argparse
import os
import sys
import requests

# Global envs
target_api_key = ''
source_api_key = ''
api_template_header = ''


# Check the .env file to make sure all required variables are set and formatted correctly
def check_configuration():
    global target_api_key, source_api_key, api_template_header
    try:
        source_api_key = os.environ["SOURCE_API_KEY"]
        target_api_key = os.environ["TARGET_API_KEY"]
    except KeyError as error:
        print(f'Invalid configuration for .env!\n Error message: {error}\n')
        exit(2)

    # Set global header for Elastic API requests
    api_template_header = '''
    {"kbn-xsrf": "true", "Content-Type": "application/json", "Authorization": f"ApiKey $api_key"}
    '''
    return True


def check_cli_opts(arguments: list):
    parser = argparse.ArgumentParser(
        description=f'Migrates all data and settings from one Elastic Cluster to another\n')

    users = parser.add_mutually_exclusive_group()
    users.add_argument('-u', action='store_true', required=False, help='Synchronize the users')
    users.add_argument('--users', action='store_true', required=False, help='Synchronize the users')

    try:
        args = parser.parse_args(arguments[1:])
        return args
    except SystemExit:
        exit(1)


def main(arguments: list):
    load_dotenv(override=True)
    check_configuration()
    args = check_cli_opts(arguments=arguments)


if __name__ == "__main__":
    main(arguments=sys.argv)
