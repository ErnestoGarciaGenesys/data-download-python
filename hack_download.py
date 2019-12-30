# Several alternative ways to download files have been tried out:

filename = history_to_download[0]['fileName']
url = 'https://gapi-euw1.genesyscloud.com/data-download/v3/files/' + filename


# Using the requests library
# This works, but requires that the file is fully stored in memory.

def create_file(folder, file_name, content):
    with open(os.path.join(folder, file_name), mode='wb') as f:
        f.write(content)

def get_file(file_name):
    file_response = requests.get(
        'https://gapi-euw1.genesyscloud.com/data-download/v3/files/' + file_name,
        headers={
            'x-api-key': conf.API_KEY,
            'Authorization': 'Bearer ' + api_token,
        })

    return file_response


# Using the urllib library
# It doesn't work. The redirection request fails with '400 Bad Request', probably for some disallowed headers.

import urllib
handler = urllib.request.HTTPHandler(debuglevel=1)
opener = urllib.request.build_opener(handler)
opener.addheaders = [
    ('x-api-key', conf.API_KEY),
    ('Authorization', 'Bearer ' + api_token)
]
urllib.request.install_opener(opener)
urllib.request.urlretrieve(url)


# Using wget 
# It doesn't work. The redirection request fails with '400 Bad Request', probably for some disallowed headers (Authorization?).

subprocess.run([
    'wget', 
    '--debug',
    '--header', 'Authorization: Bearer ' + api_token,
    '--header', 'x-api-key: ' + conf.API_KEY,
    url
])


# Using curl
# This one works. It doesn't propagate the Authorization header to the redirection request.

subprocess.run([
    'curl', 
    '--verbose',
    '-O',
    '--location', # follow redirects
    '--header', 'Authorization: Bearer ' + api_token,
    '--header', 'x-api-key: ' + conf.API_KEY,
    url
])


