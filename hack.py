# This file is for experimentation, and is meant to be run step by step in a Python REPL

import conf
import os
import requests
from pprint import pprint
import logging
import subprocess

logging.basicConfig(level=logging.DEBUG)

# TODO maybe try with existing OAuth lib:
# https://requests-oauthlib.readthedocs.io/en/latest/oauth2_workflow.html#backend-application-flow

token_response = requests.post(
    'https://gapi-euw1.genesyscloud.com/auth/v3/oauth/token',
    headers={
        'x-api-key': conf.API_KEY,
        'Accept': 'application/json',
    },
    data={
        'grant_type': 'password',
        'client_id': conf.CLIENT_ID,
        'username': (conf.TENANT + '\\' + conf.USER_NAME) if conf.TENANT else conf.USER_NAME,
        'password': conf.USER_PASSWORD,
    },
    auth=(conf.CLIENT_ID, conf.CLIENT_SECRET))

token_response.raise_for_status()

print(token_response.json())

access_token = token_response.json()['access_token']
print(access_token)

importlib.reload(conf)

history_response = requests.get(
    'https://gapi-euw1.genesyscloud.com/data-download/v4/export/history',
    params={
        'orderField': 'createdDate', # this should be by 'id', but it does not work
        'descAsc': 'true', # desc
        'title': conf.JOB_TITLE,
        'size': conf.HISTORY_MAX_SIZE,
    },
    headers={
        'x-api-key': conf.API_KEY,
        'Authorization': 'Bearer ' + access_token,
    })

history_response.raise_for_status()
pprint(history_response.json())
history = history_response.json()['data']

if history['count'] > history['size']:
    raise RuntimeError((
        "History max size is not enough to deliver all history items; you may want to increase it. "
        "Requested max size = %d, history size = %d.") %
        (history['size'], history['count']))

history_response.request.url
history_items = history_response.json()['data']['items']
pprint(history_items)

def accepted(history_item):
    return \
        (conf.JOB_TITLE_MATCH_PARTIALLY or history_item['title'] == conf.JOB_TITLE) \
        and (not conf.LAST_HISTORY_ID or history_item['id'] > conf.LAST_HISTORY_ID) \
        and history_item['fileName']

accepted_history_items = [i for i in history_items if accepted(i)]
pprint(accepted_history_items)


def get_file(file_name):
    file_response = requests.get(
        'https://gapi-euw1.genesyscloud.com/data-download/v3/files/' + file_name,
        headers={
            'x-api-key': conf.API_KEY,
            'Authorization': 'Bearer ' + access_token,
        })

    return file_response

file_response = get_file(accepted_history_items[0])
file_response.request.url
file_response.content

def create_folder(folder):
    if not os.path.exists(folder):
        os.mkdir(folder)


def create_file(folder, file_name, content):
    create_folder(folder)

    with open(os.path.join(folder, file_name), mode='wb') as f:
        f.write(content)

create_file(conf.DOWNLOADS_FOLDER, accepted_history_items[0]['fileName'], file_response.content)


def download_file(history_item):
    file_response = get_file(history_item['fileName'])
    create_file(conf.DOWNLOADS_FOLDER, history_item['fileName'], file_response.content)

download_file(accepted_history_items[0])

for history_item in accepted_history_items:
    print("Downloading file %s of size %d"
        % (history_item['fileName'], history_item['fileSize']))
    
    download_file(history_item)


def decrypt_smime(private_key_path, smime_path, decrypted_path):
    completed_process = subprocess.run([
        conf.OPENSSL_COMMAND,
        'smime',
        '-decrypt',
        '-inkey', private_key_path,
        '-in', smime_path,
        '-out', decrypted_path])
    
    completed_process.check_returncode()

def decrypt_file(in_file_name, out_file_name):
    create_folder(conf.DECRYPTED_FOLDER)

    decrypt_smime(
        conf.PRIVATE_KEY_PATH, 
        os.path.join(conf.DOWNLOADS_FOLDER, in_file_name), 
        os.path.join(conf.DECRYPTED_FOLDER, out_file_name))

for history_item in accepted_history_items:
    file_name = history_item['fileName']

    print("Decrypting file %s" % file_name)

    if not file_name.endswith('.smime'):
        raise RuntimeError("Expected filename to end with '.smime': " + file_name)

    decrypt_file(file_name, file_name[:-len('.smime')])
