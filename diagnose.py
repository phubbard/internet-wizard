
# from nslookup import Nslookup
from ping3 import ping
from rich import pretty, print

from config import *
from dns import resolve, lookup_domain


# TODO https://rich.readthedocs.io/en/latest/progress.html
# TODO https://stackoverflow.com/questions/49320007/how-to-use-tqdm-to-iterate-over-a-list

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


def can_resolve_host(host: str, resolver=REMOTE_DNS_IP) -> bool:
    # Try the Julia Evans code - only depends on stdlib
    print(f"Resolving {host} with {resolver}...", end='')
    try:
        resolve(host, nameserver=resolver)
        print("[green]ok[/]")
        return True
    except:
        print("[red]fail[/]")
        return False


def can_resolve_all_hosts(hosts: list, resolver: str) -> bool:
    tf_list = [can_resolve_host(host, resolver=resolver) for host in hosts]
    return all(tf_list)


def can_lookup_domain(domain: str, resolver: str) -> bool:
    print(f"Looking up {domain} with {resolver}...", end='')
# try:
    lookup_domain(domain)
    print("[green]ok[/]")
    return True
    # except:
    #     print("[red]fail[/]")
    #     return False


def colorize(tf: bool) -> str:
    if tf:
        return "[green]ok[/]"
    return "[red]fail[/]"


def local_network_up() -> bool:
    local_network = colorize(can_ping_all(LOCAL_IPS))
    local_dns = colorize(can_resolve_all_hosts(LOCAL_HOSTS, resolver=LOCAL_DNS_IP))
    router = colorize(can_ping(ROUTER))
    modem = colorize(can_ping(MODEM))
    wifi = colorize(can_ping(WIFI))

    remote_network = colorize(can_ping_all(REMOTE_IPS))
    remote_domains = colorize(all(can_lookup_domain(domain, resolver=REMOTE_DNS_IP) for domain in REMOTE_DOMAINS))
    remote_hosts = colorize(can_resolve_all_hosts(REMOTE_HOSTS, resolver=REMOTE_DNS_IP))

    print(f'{local_network=} {local_dns=} {router=} {modem=} {wifi=} {remote_network=} {remote_domains=} {remote_hosts=}')
    return local_network and local_dns and router and modem and wifi and remote_network and remote_domains and remote_hosts


if __name__ == '__main__':
    # local_network_up()
    can_lookup_domain('google.com', resolver=REMOTE_DNS_IP)