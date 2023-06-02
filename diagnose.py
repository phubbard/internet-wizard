
import logging

from nslookup import Nslookup
from ping3 import ping
from config import *

logging.basicConfig(level=logging.DEBUG, format='%(pathname)s(%(lineno)s): %(levelname)s %(message)s')
log = logging.getLogger()


def can_ping(host: str, timeout=2) -> bool:
    """
    One single ping, to bastardize the movie quote.
    """
    rc = ping(host, timeout=timeout)
    if rc:
        return True
    return False


def can_ping_all(hosts: list, timeout=2) -> bool:
    """
    Ping all hosts in a list
    """
    tf_list = [can_ping(host, timeout=timeout) for host in hosts]
    return all(tf_list)


def can_resolve(host: str) -> bool:
    """
    Forward A-record DNS lookup
    """

    dns_query = Nslookup()
    record = dns_query.dns_host_lookup(host, 'A')
    if record.answer:
        return True
    return False


def can_resolve_all(hosts: list) -> bool:
    """
    Forward A-record DNS lookup
    """

    dns_query = Nslookup()
    tf_list = [dns_query.dns_host_lookup(host, 'A') for host in hosts]
    return all(tf_list)


def local_network_up() -> bool:

    connected = can_ping_all(LOCAL_IPS)
    local_dns_ok = can_resolve_all(LOCAL_HOSTS)
    router_ok = can_ping(ROUTER)
    modem_ok = can_ping(MODEM)
    wifi_ok = can_ping(WIFI)

    remote_ok = can_ping_all(REMOTE_IPS)
    remote_dns_ok = can_resolve_all(REMOTE_HOSTS)

    print(f'{connected=} {local_dns_ok=} {router_ok=} {modem_ok=} {wifi_ok=} {remote_ok=} {remote_dns_ok=}')
    return connected and local_dns_ok and router_ok and modem_ok and wifi_ok and remote_ok and remote_dns_ok


if __name__ == '__main__':
    print(local_network_up())