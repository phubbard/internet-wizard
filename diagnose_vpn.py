
from rich import pretty, print

from config_vpn import *
from utils import *


# TODO https://rich.readthedocs.io/en/latest/progress.html
# TODO https://stackoverflow.com/questions/49320007/how-to-use-tqdm-to-iterate-over-a-list

# See https://pypi.org/project/rich/
pretty.install()


def local_network_up() -> bool:
    local_ip = colorize(have_ip_address())
    local_network = colorize(can_ping_all(LAN_LOCAL_IPS))
    local_bcast = colorize(can_ping_all(LAN_LOCAL_HOSTS))

    remote_network = colorize(can_ping_all(REMOTE_IPS))
    remote_domains = colorize(all(can_lookup_domain(domain, resolver=REMOTE_DNS_IPS[0]) for domain in REMOTE_DOMAINS))
    remote_hosts = colorize(can_resolve_all_hosts(REMOTE_HOSTS, resolver=REMOTE_DNS_IPS[0]))

    print(f'{local_ip=} {local_network=} {local_bcast=} {remote_network=} {remote_domains=} {remote_hosts=}')

if __name__ == '__main__':
    local_network_up()
