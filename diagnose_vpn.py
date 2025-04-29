from rich import pretty, print
pretty.install()

from config_vpn import *
from utils import *


# TODO https://rich.readthedocs.io/en/latest/progress.html
# TODO https://stackoverflow.com/questions/49320007/how-to-use-tqdm-to-iterate-over-a-list



def local_network_up() -> bool:
    try:
        local_ip = colorize(have_ip_address())

        remote_network = colorize(can_ping_all(REMOTE_IPS))
        remote_domains = colorize(False)  # Initialize with failure
        remote_hosts = colorize(False)    # Initialize with failure
        
        try:
            remote_domains = colorize(all(can_lookup_domain(domain, resolver=REMOTE_DNS_IPS[0]) for domain in REMOTE_DOMAINS))
        except Exception as e:
            print(f"[red]Error checking remote domains: {str(e)}[/]")
            
        try:
            for resolver in REMOTE_DNS_IPS:
                remote_hosts = colorize(can_resolve_all_hosts(REMOTE_HOSTS, resolver=resolver))
        except Exception as e:
            print(f"[red]Error checking remote hosts: {str(e)}[/]")

        print(f'{local_ip=} {remote_network=} {remote_domains=} {remote_hosts=}')
        return "ok" in local_ip and "ok" in remote_network and "ok" in remote_domains and "ok" in remote_hosts
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
