from config import *
from utils import *

from rich import pretty, print


# TODO https://rich.readthedocs.io/en/latest/progress.html
# TODO https://stackoverflow.com/questions/49320007/how-to-use-tqdm-to-iterate-over-a-list

# See https://pypi.org/project/rich/
pretty.install()


def local_network_up() -> bool:
    local_ip = colorize(have_ip_address())
    local_network = colorize(can_ping_all(LOCAL_IPS))
    local_dns = colorize(can_resolve_all_hosts(LOCAL_HOSTS_FQDN, resolver=LOCAL_DNS_IP))
    router = colorize(can_ping(ROUTER))
    modem = colorize(can_ping(MODEM))
    wifi = colorize(can_ping(WIFI))

    remote_network = colorize(can_ping_all(REMOTE_IPS))
    remote_domains = colorize(all(can_lookup_domain(domain, resolver=REMOTE_DNS_IP) for domain in REMOTE_DOMAINS))
    remote_hosts = colorize(can_resolve_all_hosts(REMOTE_HOSTS, resolver=REMOTE_DNS_IP))

    print(f'{local_ip=} {local_network=} {local_dns=} {router=} {modem=} {wifi=} {remote_network=} {remote_domains=} {remote_hosts=}')
    return local_ip and local_network and local_dns and router and modem and wifi and remote_network and remote_domains and remote_hosts


if __name__ == '__main__':
    local_network_up()
