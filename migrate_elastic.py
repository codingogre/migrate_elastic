from dotenv import load_dotenv
import argparse
import os
import sys
import requests
import secrets

# Global envs
target_api_key = ''
target_endpoint = ''
source_api_key = ''
source_endpoint = ''
api_header_template = {"kbn-xsrf": "true", "Content-Type": "application/json", "Authorization": ''}

# Create a global session object for requests to use HTTP keep-alive
s = requests.Session()


# Check the .env file to make sure all required variables are set and formatted correctly
def check_configuration():
    global target_api_key, target_endpoint, source_api_key, source_endpoint, api_header_template
    try:
        source_api_key = os.environ["SOURCE_API_KEY"]
        source_endpoint = os.environ["SOURCE_ENDPOINT"]
        target_api_key = os.environ["TARGET_API_KEY"]
        target_endpoint = os.environ["TARGET_ENDPOINT"]
    except KeyError as error:
        print(f'Invalid configuration for .env!\n Error message: {error}\n')
        exit(2)
    return True


def check_cli_opts(arguments: list):
    parser = argparse.ArgumentParser(
        description=f'Migrates all data and settings from one Elastic Cluster to another\n')

    parser.add_argument('-a', '--all', action='store_true', required=False,
                        help='Synchronize everything (users, roles, kibana objects, data)')
    parser.add_argument('-u', '--users', action='store_true', required=False,
                        help='Synchronize *enabled* native users')
    parser.add_argument('-r', '--roles', action='store_true', required=False,
                        help='Synchronize roles that are *not* reserved')
    parser.add_argument('-rm', '--role_mappings', action='store_true', required=False,
                        help='Synchronize role mappings that are *enabled*')

    try:
        args = parser.parse_args(arguments[1:])
        return args
    except SystemExit:
        exit(1)


def get_users(disabled: bool):
    url = f"{source_endpoint}/_security/user"
    api_header_template['Authorization'] = f'ApiKey {source_api_key}'
    r = s.get(url=url, headers=api_header_template)
    check_http_status_code(r.status_code, 'Get native users')
    users = r.json()
    if not disabled:
        for key in list(users):
            if not users[key]['enabled']:
                users.pop(key)
    return users


def create_user(user: dict):
    username = user['username']
    # Generate a XKCD-style (https://xkcd.com/936/) passphrase.  If file doesn't exist generate a random 12 digit one
    if os.path.isfile('/usr/share/dict/words'):
        with open('/usr/share/dict/words') as f:
            words = [word.strip() for word in f]
            password = ' '.join(secrets.choice(words) for _ in range(4))
    else:
        password = secrets.token_urlsafe(12)
    user['password'] = password
    url = f"{target_endpoint}/_security/user/{username}"
    user.pop('username')
    api_header_template['Authorization'] = f'ApiKey {target_api_key}'
    r = s.post(url=url, headers=api_header_template, json=user)
    check_http_status_code(r.status_code, f'Create native user: {username}')
    return username, password


def get_roles(reserved: bool):
    url = f"{source_endpoint}/_security/role"
    api_header_template['Authorization'] = f'ApiKey {source_api_key}'
    r = s.get(url=url, headers=api_header_template)
    check_http_status_code(r.status_code, 'Get roles')
    roles = r.json()
    if not reserved:
        for key in list(roles):
            if '_reserved' in roles[key]['metadata']:
                roles.pop(key)
    return roles


def create_role(role_name: str, role: dict):
    url = f"{target_endpoint}/_security/role/{role_name}"
    api_header_template['Authorization'] = f'ApiKey {target_api_key}'
    r = s.post(url=url, headers=api_header_template, json=role)
    check_http_status_code(r.status_code, f'Create role {role_name}')


def get_role_mappings(cloud_sso: bool):
    url = f"{source_endpoint}/_security/role_mapping"
    api_header_template['Authorization'] = f'ApiKey {source_api_key}'
    r = s.get(url=url, headers=api_header_template)
    check_http_status_code(r.status_code, 'Get role mapping')
    role_mappings = r.json()
    if not cloud_sso:
        role_mappings.pop('elastic-cloud-sso-kibana-do-not-change')
    for key in list(role_mappings):
        if not role_mappings[key]['enabled']:
            role_mappings.pop(key)
    return role_mappings


def create_role_mappings(role_mapping_name: str, role_mapping: dict):
    url = f"{target_endpoint}/_security/role_mapping/{role_mapping_name}"
    api_header_template['Authorization'] = f'ApiKey {target_api_key}'
    r = s.post(url=url, headers=api_header_template, json=role_mapping)
    check_http_status_code(r.status_code, f'Create role mapping {role_mapping_name}')


def check_http_status_code(status_code: int, message: str):
    if status_code == 200:
        print(f'  {message} succeeded')
    else:
        print(f'  {message} failed')
        exit(1)


def main(arguments: list):
    load_dotenv(override=True)
    check_configuration()
    args = check_cli_opts(arguments=arguments)
    print(args)
    if args.all or args.users:
        print('*** Migrating Users ***')
        users = get_users(disabled=False)
        user_db = []
        for user in users:
            username, password = create_user(users[user])
            user_db.append((username, password))
        print('  List of usernames and passwords:')
        for item in user_db:
            print(f'    Username: "{item[0]}" Password: "{item[1]}"')
    if args.all or args.roles:
        print('*** Migrating Roles ***')
        roles = get_roles(reserved=False)
        for role in roles:
            create_role(role_name=role, role=roles[role])
    if args.all or args.role_mappings:
        print('*** Migrating Role Mappings ***')
        role_mappings = get_role_mappings(cloud_sso=False)
        for role_mapping in role_mappings:
            create_role_mappings(role_mapping_name=role_mapping, role_mapping=role_mappings[role_mapping])


if __name__ == "__main__":
    main(arguments=sys.argv)
