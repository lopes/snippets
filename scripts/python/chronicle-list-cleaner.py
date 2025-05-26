'''
Cleans up lines in the reference lists in Chronicle SIEM with expired dates.

This script can be used to clean up some or all Reference Lists in Chronicle SIEM.
It scans each list and removes expired lines with the same pattern it is set to
monitor.  Lines outside this pattern are just ignored.  The pattern is:

<value>  // expires:YYYY-MM-DD


DEPLOYMENT
It is intended to be used as a Cloud Function in the GCP platform.  Create a new
function with the following parameters:

1. Environment: 2nd gen
2. Function name: chronicle-list-cleaner
3. Region: us-central1 (or another of your preference)
4. Trigger type: HTTPS (will setup Cloud Scheduler later but copy the URL now)
5. Set the runtime environment with the following minimum requirements:
  5.1. Memory: 256 MiB
  5.2. CPU: 1
  5.3. Timeout: 300 seconds
  5.4. Add the `CHRONICLE_KEY` environment variable with the JSON access key
6. Click Next

In the code section, set Python runtime (tested in 3.12) and using the inline
editor, set the entry point to `main`, paste the code below into the `main.py`
file.  In `requirements.txt` paste the following:

```
functions-framework==3.*
google-auth
requests
```

I recommend running some tests against specific lists before running it against
all lists!

Still in GCP, go to Cloud Scheduler and create a new job with the following
parameters:

1. Name: chronicle-list-cleaner
2. Region: According to your environment
3. Description: Runs chronicle-list-cleaner daily to remove expired lines
4. Frequency: Select the desired frequency, like `10 5 * * *` for daily at 0510
5. Timezone: According to your preference
6. Click to proceed and select HTTP for the target type
7. URL: Paste the URL from the Cloud Function created before
8. HTTP method: POST
9. Add an HTTP header to identify the request
  9.1. Content-Type: application/json
  9.2. User-Agent: Google Cloud Scheduler
10. Add the following body:
  {
    "command": "cleanup",
    "list_name": "ALL__LISTS",
    "list_type": ""
  }
11. Configure the authentication method according to your environment
12. Click to proceed and finish the job creation

If everything's correct, the job will run daily at the specified time and clean
up the lists with lines set to expire.


NOTE ON LINE ORDER
The `set()` function is used to remove duplicates, so the order of the lines in
the list will be changed!  If you want to keep the order, remove the `set()` and
use a different approach to remove duplicates.


NOTE ON EXPIRATION
The date is truncated to 0h each day, so it will remove items that expired on
the same day it is running.  If you want to keep the items until the end of the
day inform the date as the next day because it'll expire at 0h of the next day.


BASED ON
- https://github.com/chronicle/api-samples-python
- https://github.com/goog-cmmartin/thatsiemguy/blob/main/mati/cloud_function/main.py


AUTHOR: Joe Lopes <lopes.id>
DATE: 2023-07-18
LICENSE: MIT
'''

from requests.exceptions import HTTPError

from google.auth.transport import requests
from google.oauth2 import service_account

from json import loads
from re import compile
from datetime import datetime

import functions_framework  # cloud functions/flask requirement
from os import environ


AUTHORIZATION_SCOPES = [
  'https://www.googleapis.com/auth/chronicle-backstory',
  'https://www.googleapis.com/auth/malachite-ingestion'
]
CHRONICLE_API_BASE_URL = "https://backstory.googleapis.com"


re_expiration = compile(r'^[\w\:\-\?\!\@].*//\s*expires:\s*(?P<expiration>\d{4}-\d{2}-\d{2})')


def init_client(credentials, scopes=AUTHORIZATION_SCOPES):
  '''
  Obtains an authorized session using the provided credentials.
  Args:
    credentials (google.oauth2.service_account.Credentials): The service account credentials
  Returns:
    requests.AuthorizedSession: An authorized session for making API calls.
  '''
  credentials = service_account.Credentials.from_service_account_info(
    credentials,
    scopes=AUTHORIZATION_SCOPES
  )
  return requests.AuthorizedSession(credentials)

def get_lists(client, params):
  '''
  Obtain all Reference Lists in Chronicle SIEM.
  Args:
    client: Session for making API calls
  Returns:
    List of strings of all reference lists' names and types.
  '''
  url = f'{CHRONICLE_API_BASE_URL}/v2/lists'
  res = client.request('GET', url, params=params)
  res.raise_for_status()
  lists = list()
  for x in res.json()['lists']:
    try:
      lists.append((x['name'], x['contentType']))
    except KeyError:
      lists.append((x['name'], 'CONTENT_TYPE_DEFAULT_STRING'))
  return lists

def get_lines(client, list_name):
  '''
  Fetches all lines in a reference list.
  Args:
    client: Session for making API calls.
    list_name: Name of the reference list.
  Returns:
    Full response from Chronicle API in JSON format.
  '''
  url = f'{CHRONICLE_API_BASE_URL}/v2/lists/{list_name}'
  res = client.request('GET', url)
  res.raise_for_status()
  return res.json()

def cleanup_list(client, list_name, list_type):
  '''
  Removes expired lines from a list.
  Args:
    client: Session for making API calls
    list_name: Name of the reference list
    list_type: Type of the reference list
  Returns:
    Updates the list if any expired item and returns the number of deprecated lines.
  '''
  ref_list = get_lines(client, list_name)
  dedup_lines = set(ref_list['lines'])
  out_lines = list()
  today = datetime.today()
  expired = len(ref_list['lines']) - len(dedup_lines)

  for line in dedup_lines:
    if line:  # skipping blank lines
      try:
        # will ONLY work over lines in the format defined here
        p = re_expiration.search(line)
        if datetime.strptime(p.group('expiration'),'%Y-%m-%d') < today:
          out_lines.append(f'// {line}')  # just comment, don't delete
          expired += 1
        else:
          out_lines.append(line)
      except AttributeError:
        out_lines.append(line)

  # TODO: update the description with the timestamp + number of expired lines
  # ex.: <timestamp>: +X lines, -Y lines
  url = f'{CHRONICLE_API_BASE_URL}/v2/lists'
  body = {
    'name': list_name,
    'lines': sorted(out_lines),
    'content_type': list_type
  }
  params = {'update_mask': 'list.lines'}
  res = client.request('PATCH', url, params=params, json=body)
  res.raise_for_status()
  print(f'Cleaned {list_name} ({list_type}): {expired} items expired')
  return expired

def cleanup_all_lists(client):
  '''
  Removes expired lines from all lists in Chronicle SIEM.
  Args:
    client: Session for making API calls
  Returns:
    Updates the lists and returns a list of tuples like (list_name,num_expired).
  '''
  lists = get_lists(client, {'page_size':2000,'page_token':''})
  status = list()
  for lname,ltype in lists:
    try:
      expired = cleanup_list(client, lname, ltype)
      status.append((lname, expired))
    except HTTPError:
      print(f'Error processing: {lname} ({ltype})')
      status.append((lname, -1))
  return status


@functions_framework.http
def main(request):
  '''
  Entry point for Cloud Functions.
  Args:
    request: The caller's request parameters (args for URL params and json for data)
  Returns:
    Updates the list if any expired item and returns the number of deprecated lines.
  '''
  req_json = request.get_json(silent=True)
  req_args = request.args
  credentials = loads(environ.get('CHRONICLE_KEY'))
  client = init_client(credentials)

  if req_json['command'] == 'cleanup':
    print(f'Starting cleanup for {req_json['list_name']}')
    if req_json['list_name'] == 'ALL__LISTS':
      status = cleanup_all_lists(client)
    else:
      status = cleanup_list(client, req_json['list_name'], req_json['list_type'])
  else:
    raise ValueError('Invalid command')

  print(f'Finished: {len(status)} lists processed')
  return f'{status}'
