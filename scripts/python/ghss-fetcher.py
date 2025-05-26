'''
Reads all secret-scanning findings from GitHub and outputs them in a JSON file.

Author: Joe Lopes <lopes.id>
Date: 2025-05-24
License: MIT

Usage:
  - Issue a GitHub Fine Grained Personal Access Token (FGPAT) with sufficient
    permissions to read secret scanning findings
  - Set the PAT as an environment variable named `GH_PAT`
  - Review the configurations under the CONFIG variable, like the ORG_NAME
  - Run the script: `python ghss-fetcher.py`

Dependencies:
  - requests

References
  - https://docs.github.com/en/rest/secret-scanning/secret-scanning
'''


import os
import requests
import json
import time


CONFIG = {
  'TOKEN': os.getenv('GH_PAT'),
  'ORG_NAME': 'ACME',
  'MAX_PER_PAGE': 100,
  # for filters: leave empty to get all findings
  'SECRET_TYPES': 'aws_access_key_id,aws_secret_access_key,aws_secret_access_key,aws_session_token,aws_temporary_access_key_id'
}

if not CONFIG['TOKEN']:
  raise ValueError('GitHub token not set')


def fetch_page(page_num: int) -> list:
  headers = {
    'Accept': 'application/vnd.github+json',
    'Authorization': f'Bearer {CONFIG['TOKEN']}',
    'X-GitHub-Api-Version': '2022-11-28'
  }

  if CONFIG['SECRET_TYPES']:
    url = f'https://api.github.com/orgs/{CONFIG["ORG_NAME"]}/secret-scanning/alerts?secret_type=${CONFIG["SECRET_TYPES"]}&page={page_num}&per_page=${CONFIG["MAX_PER_PAGE"]}'
  else:
    url = f'https://api.github.com/orgs/{CONFIG["ORG_NAME"]}/secret-scanning/alerts?page={page_num}&per_page=${CONFIG["MAX_PER_PAGE"]}'

  try:
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()
  except requests.exceptions.RequestException as e:
    print(f'Error fetching page {page_num}: {e}')
    return []


# MAIN
alerts_json = []
page = 1
output = 'ghss-output.json'

while True:
  print(f'Fetching page {page}...', end='\n')
  response_data = fetch_page(page)

  current_page_json = [
    {
      'created_at': alert.get('created_at'),
      'updated_at': alert.get('updated_at'),
      'url': alert.get('url'),
      'secret_type': alert.get('secret_type'),
      'secret': alert.get('secret'),
      'resolution': alert.get('resolution'),
      'resolved_at': alert.get('resolved_at')
    }
    for alert in response_data
  ]

  if not current_page_json:
    print('No more alerts found. Exiting.')
    break

  alerts_json.extend(current_page_json)
  page += 1
  time.sleep(0.1)  # api friendly

print(f'Fetched {len(alerts_json)} results.')

with open(output, 'w') as f:
  json.dump(alerts_json, f, indent=2)

print(f'Alerts exported to {output}')
