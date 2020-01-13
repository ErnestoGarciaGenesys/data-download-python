# This file is for experimentation, and is meant to be run step by step in a Python REPL

import conf
import os
import requests
from pprint import pprint
import logging
import subprocess
from download_export_files import *


# To reload configuration without restarting REPL
import importlib
importlib.reload(conf)
import download_export_files
importlib.reload(download_export_files)
from download_export_files import *


logging.basicConfig(level=logging.DEBUG)


api_token_response = request_api_token()
pprint(api_token_response.json())
api_token_response.raw.info()
api_token_response.status_code
api_token = extract_api_token(api_token_response)
pprint(api_token)

history_response = request_history(api_token)
pprint(history_response.json())
history_response.request.url
history = extract_history(history_response)
pprint(history)

history_to_download = list(filter(check_if_download, history))
pprint(history_to_download)

download_file(history_to_download[0]['fileName'], api_token)

main()

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
