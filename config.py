
# thinking with code.
LOCAL_IPS = [
    '204.128.136.3',
    '204.128.136.11',
    '204.128.136.5',
    '204.128.136.2'
]

WIFI = 'wifi'
ROUTER = 'fratboy'

LOCAL_HOSTS = [
    'webserver', 'servlet', WIFI, ROUTER
]

REMOTE_IPS = [
    '8.8.8.8',
    '9.9.9.9',
    '1.1.1.1'
]

REMOTE_DOMAINS = [
    'google.com', 'cloudflare.com', 'amazon.com'
]

REMOTE_HOSTS = [
    'www.google.com', 'www.cloudflare.com', 'www.amazon.com'
]

LOCAL_DOMAIN = 'phfactor.net'
LOCAL_DNS_IP = '204.128.136.5'
REMOTE_DNS_IP = '8.8.8.8'

LOCAL_HOSTS_FQDN = [f'{x}.{LOCAL_DOMAIN}' for x in LOCAL_HOSTS]