from config import *
from utils import *

from rich import pretty, print


# TODO https://rich.readthedocs.io/en/latest/progress.html
# TODO https://stackoverflow.com/questions/49320007/how-to-use-tqdm-to-iterate-over-a-list

# See https://pypi.org/project/rich/
pretty.install()


def local_network_up() -> bool:
    try:
        local_ip = colorize(have_ip_address())
        
        # Check local network connectivity
        try:
            local_network = colorize(can_ping_all(LOCAL_IPS))
        except Exception as e:
            print(f"[red]Error checking local network: {str(e)}[/]")
            local_network = colorize(False)
            
        try:
            local_dns = colorize(can_resolve_all_hosts(LOCAL_HOSTS_FQDN, resolver=LOCAL_DNS_IP))
        except Exception as e:
            print(f"[red]Error checking local DNS: {str(e)}[/]")
            local_dns = colorize(False)
            
        # Check local devices
        try:
            router = colorize(can_ping(ROUTER))
        except Exception as e:
            print(f"[red]Error checking router: {str(e)}[/]")
            router = colorize(False)
            
        try:
            wifi = colorize(can_ping(WIFI))
        except Exception as e:
            print(f"[red]Error checking wifi: {str(e)}[/]")
            wifi = colorize(False)

        # Check remote connectivity
        try:
            remote_network = colorize(can_ping_all(REMOTE_IPS))
        except Exception as e:
            print(f"[red]Error checking remote network: {str(e)}[/]")
            remote_network = colorize(False)
            
        try:
            remote_domains = colorize(all(can_lookup_domain(domain, resolver=REMOTE_DNS_IP) for domain in REMOTE_DOMAINS))
        except Exception as e:
            print(f"[red]Error checking remote domains: {str(e)}[/]")
            remote_domains = colorize(False)
            
        try:
            remote_hosts = colorize(can_resolve_all_hosts(REMOTE_HOSTS, resolver=REMOTE_DNS_IP))
        except Exception as e:
            print(f"[red]Error checking remote hosts: {str(e)}[/]")
            remote_hosts = colorize(False)

        print(f'{local_ip=} {local_network=} {local_dns=} {router=} {wifi=} {remote_network=} {remote_domains=} {remote_hosts=}')
        
        # Evaluate overall network status
        all_checks = [
            "ok" in local_ip, "ok" in local_network, "ok" in local_dns,
            "ok" in router, "ok" in wifi,
            "ok" in remote_network, "ok" in remote_domains, "ok" in remote_hosts
        ]
        return all(all_checks)
    except Exception as e:
        print(f"[red]Critical error in diagnostic: {str(e)}[/]")
        return False


if __name__ == '__main__':
    try:
        result = local_network_up()
        print(f"Network status: {'[green]UP[/]' if result else '[red]DOWN[/]'}")
    except KeyboardInterrupt:
        print("\n[yellow]Diagnostic interrupted by user[/]")
    except Exception as e:
        print(f"[red]Unexpected error: {str(e)}[/]")
