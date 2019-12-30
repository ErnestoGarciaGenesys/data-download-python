mandatory = optional = None

API_KEY = mandatory
CLIENT_ID = mandatory
CLIENT_SECRET = mandatory
TENANT = ""
USER_NAME = mandatory
USER_PASSWORD = mandatory

HISTORY_MAX_SIZE = 100000 # Set to None for no limit
JOB_TITLE = optional

# If True, the string provided in JOB_TITLE is just checked to be contained in the actual job title.
# If False (default), the string provided in JOB_TITLE must match exactly the actual job title.
JOB_TITLE_MATCH_PARTIALLY = False 

LAST_HISTORY_ID = None

PRIVATE_KEY_PATH = mandatory
DOWNLOADS_FOLDER = 'downloads'
DECRYPTED_FOLDER = 'decrypted'

OPENSSL_COMMAND = 'openssl'
