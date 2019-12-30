import os
import requests
import shutil
import urllib3

import conf


def request_api_token():
    # TODO maybe try with existing OAuth lib:
    # https://requests-oauthlib.readthedocs.io/en/latest/oauth2_workflow.html#backend-application-flow

    return requests.post(
        'https://gapi-euw1.genesyscloud.com/auth/v3/oauth/token',
        headers={
            'x-api-key': conf.API_KEY,
            'Accept': 'application/json',
        },
        auth=(conf.CLIENT_ID, conf.CLIENT_SECRET),
        data={
            'grant_type': 'password',
            'client_id': conf.CLIENT_ID,
            'username': (conf.TENANT + '\\' + conf.USER_NAME) if conf.TENANT else conf.USER_NAME,
            'password': conf.USER_PASSWORD,
        })
    

def extract_api_token(token_response):
    token_response.raise_for_status()
    return token_response.json()['access_token']


def request_history(api_token):
    return requests.get(
        'https://gapi-euw1.genesyscloud.com/data-download/v4/export/history',
        params={
            'orderField': 'createdDate', # this should be by 'id', but it does not work
            'descAsc': 'true', # desc
            'title': conf.JOB_TITLE,
            'size': conf.HISTORY_MAX_SIZE,
        },
        headers={
            'x-api-key': conf.API_KEY,
            'Authorization': 'Bearer ' + api_token,
        })


def extract_history(history_response):
    history_response.raise_for_status()
    history = history_response.json()['data']

    if history['count'] > history['size']:
        raise RuntimeError((
            "History max size is not enough to deliver all history items; you may want to increase it. "
            "Requested max size = %d, history size = %d.") %
            (history['size'], history['count']))
    
    return history['items']


def check_if_download(history_item):
    return \
        (conf.JOB_TITLE_MATCH_PARTIALLY or history_item['title'] == conf.JOB_TITLE) \
        and (not conf.LAST_HISTORY_ID or history_item['id'] > conf.LAST_HISTORY_ID) \
        and history_item['fileName']


def create_folder(folder):
    if not os.path.exists(folder):
        os.mkdir(folder)


def download_file(file_name, api_token):
    http = urllib3.PoolManager()

    url = 'https://gapi-euw1.genesyscloud.com/data-download/v3/files/' + file_name
    
    headers = {
        'x-api-key': conf.API_KEY,
        'Authorization': 'Bearer ' + api_token,
    }

    local_file_name = os.path.join(conf.DOWNLOADS_FOLDER, file_name)

    # https://stackoverflow.com/a/27406501/503785
    with http.request('GET', url, headers=headers, preload_content=False) as response, open(local_file_name, 'wb') as out_file:
        shutil.copyfileobj(response, out_file)


def main():
    api_token = extract_api_token(request_api_token())
    history = extract_history(request_history(api_token))
    history_to_download = filter(check_if_download, history)
    for history_item in history_to_download:
        download_file(history_item['fileName'], api_token)


if __name__ == '__main__':
    main()