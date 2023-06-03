
from nslookup import Nslookup
from ping3 import ping
from rich import pretty, print

from config import *


# TODO https://rich.readthedocs.io/en/latest/progress.html
# TODO https://stackoverflow.com/questions/49320007/how-to-use-tqdm-to-iterate-over-a-list

# Instantiate once for reuse
dns_query = Nslookup()
# See https://pypi.org/project/rich/
pretty.install()


def can_ping(host: str, timeout=2) -> bool:
    """
    One single ping, to bastardize the movie quote.
    """
    print(f"Pinging {host}...", end='')
    rc = ping(host, timeout=timeout)
    if rc:
        print("[green]up[/]")
        return True
    print("[red]down[/]")
    return False


def can_ping_all(hosts: list, timeout=2) -> bool:
    """
    Ping all hosts in a list
    """
    tf_list = [can_ping(host, timeout=timeout) for host in hosts]
    return all(tf_list)


def can_resolve(host: str) -> bool:
    # Simplest-possible one-host to IPv4 lookup
    print(f"Resolving {host}...", end='')
    record = dns_query.dns_host_lookup(host, 'A')
    if len(record.answer) > 0:
        print("[green]ok[/]")
        return True
    print("[red]fail[/]")
    return False


def can_resolve_all(hosts: list) -> bool:
    # Are all hosts resolvable?
    tf_list = [can_resolve(host) for host in hosts]
    return all(tf_list)


def colorize(tf: bool) -> str:
    if tf:
        return "[green]ok[/]"
    return "[red]fail[/]"

def local_network_up() -> bool:
    local_network = colorize(can_ping_all(LOCAL_IPS))
    local_dns = colorize(can_resolve_all(LOCAL_HOSTS))
    router = colorize(can_ping(ROUTER))
    modem = colorize(can_ping(MODEM))
    wifi = colorize(can_ping(WIFI))

    remote_network = colorize(can_ping_all(REMOTE_IPS))
    remote_dns = colorize(can_resolve_all(REMOTE_HOSTS))

    print(f'{local_network=} {local_dns=} {router=} {modem=} {wifi=} {remote_network=} {remote_dns=}')
    return local_network and local_dns and router and modem and wifi and remote_network and remote_dns


if __name__ == '__main__':
    local_network_up()
