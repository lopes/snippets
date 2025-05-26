'''
A simple script to test the Cortex API with Advanced and Standard keys.
It uses solely the Python 3 Standard Library, so no additional packages are needed.

USAGE
python3 lobotomy.py KEYID KEY KEYTYPE FQDN ENDPOINT START COUNT PAGES

EXAMPLE
python3 lobotomy.py \
    007 \
    my-loooong-key \
    advanced \
    api-acme.xdr.us.paloaltonetworks.com \
    /public_api/v1/alerts/get_alerts_multi_events \
    0 100 10

Will get the 100 most recent alerts starting from zero and will iterate (paginate)
10 times (1000 events in total).

REFERENCE
https://cortex-panw.stoplight.io/docs/cortex-xdr/813e387002342-get-all-alerts

AUTHOR.: José Lopes <lopes.id>
DATE...: 2023-11-09
LICENSE: MIT
'''


from sys import argv
from datetime import datetime, timezone
from secrets import choice
from string import ascii_letters, digits
from hashlib import sha256
from json import dumps
from http.client import HTTPSConnection


def get_headers(key_id, key, key_type):
    headers = {}
    if key_type == 'advanced':
        nonce = ''.join([choice(ascii_letters + digits) for _ in range(64)])
        timestamp = int(datetime.now(timezone.utc).timestamp()) * 1000
        auth_key = '%s%s%s' % (key, nonce, timestamp)
        headers = {
            'x-xdr-timestamp': str(timestamp),
            'x-xdr-nonce': nonce,
            'x-xdr-auth-id': str(key_id),
            'Authorization': sha256(auth_key.encode('utf-8')).hexdigest()
        }
    else:
        headers = {
            'Authorization': key,
            'x-xdr-auth-id': str(key_id)
        }
    return headers

def get_payload(start, end):
    'Lots of room for improvement here'
    payload = {
        'request_data': {
        'filters': [
            {
            'field': 'severity',
            'operator': 'in',
            'value': [
                'low',
                'medium',
                'high'
            ]
            }
        ],
        'search_from': start,
        'search_to': end,
        'sort': {
            'field': 'creation_time',
            'keyword': 'desc'
        }
        }
    }
    return payload

def request(key_id, key, key_type, fqdn, endpoint, start, end):
    payload = get_payload(start, end)
    headers = get_headers(key_id, key, key_type)
    conn = HTTPSConnection(fqdn)
    conn.request('POST', endpoint, dumps(payload), headers)
    res = conn.getresponse()
    data = res.read()
    return data.decode('utf-8')

def paginator(key_id, key, key_type, fqdn, endpoint, start, count, pages):
    page = 1
    base_name = f'cortex-alerts-{datetime.now().isoformat()}'
    while page <= pages:
        fname = f'{base_name}-{page}.json'
        end = start + count
        print(f'[{page:02d}/{pages:02d}] ', end='')
        with open(fname, 'w') as f:
            try:
                res = request(key_id, key, key_type, fqdn, endpoint, start, end)
            except:
                print('Error fetching data from Cortex')
                break
            f.write(res)
            print(f'Page {page} ({start:03d}-{end:03d}) stored in {fname}')
        page += 1
        start += count


paginator(
    int(argv[1]),
    argv[2],
    argv[3],
    argv[4],
    argv[5],
    int(argv[6]),
    int(argv[7]),
    int(argv[8])
)
