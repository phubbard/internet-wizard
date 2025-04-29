from io import BytesIO
from dataclasses import dataclass
import dataclasses
import random
import struct
import socket
from typing import List

from ping3 import ping

from rich import pretty, print
pretty.install()

@dataclass
class DNSHeader:
    id: int
    flags: int
    num_questions: int = 0
    num_answers: int = 0
    num_authorities: int = 0
    num_additionals: int = 0


@dataclass
class DNSQuestion:
    name: bytes
    type_: int
    class_: int


@dataclass
class DNSRecord:
    name: bytes
    type_: int
    class_: int
    ttl: int
    data: bytes


@dataclass
class DNSPacket:
    header: DNSHeader
    questions: List[DNSQuestion]
    answers: List[DNSRecord]
    authorities: List[DNSRecord]
    additionals: List[DNSRecord]


TYPE_A = 1
CLASS_IN = 1
TYPE_TXT = 16
TYPE_NS = 2
RECURSION_DESIRED = 1 << 8
DNS_DEFAULT_IP = '8.8.8.8'

def header_to_bytes(header):
    fields = dataclasses.astuple(header)
    return struct.pack('!HHHHHH', *fields)


def question_to_bytes(question):
    return question.name + struct.pack('!HH', question.type_, question.class_)


def encode_dns_name(domain_name):
    encoded = b''
    for part in domain_name.encode('ascii').split(b'.'):
        encoded += bytes([len(part)]) + part
    return encoded + b'\x00'


def build_query(domain_name, record_type):
    name = encode_dns_name(domain_name)
    id = random.randint(0, 65535)
    header = DNSHeader(id=id, num_questions=1, flags=RECURSION_DESIRED)
    question = DNSQuestion(name=name, type_=record_type, class_=CLASS_IN)
    return header_to_bytes(header) + question_to_bytes(question)


def parse_header(reader):
    items = struct.unpack('!HHHHHH', reader.read(12))
    return DNSHeader(*items)


def decode_name(reader):
    parts = []
    while (length := reader.read(1)[0]) != 0:
        if length & 192:
            parts.append(decode_compressed_name(length, reader))
            break
        else:
            parts.append(reader.read(length))
    return b'.'.join(parts)


def decode_compressed_name(length, reader):
    pointer_bytes = bytes([length & 63]) + reader.read(1)
    pointer = struct.unpack('!H', pointer_bytes)[0]
    current_pos = reader.tell()
    reader.seek(pointer)
    result = decode_name(reader)
    reader.seek(current_pos)
    return result


def ip_to_string(ip):
    return '.'.join([str(x) for x in ip])


def parse_record(reader):
    name = decode_name(reader)
    data = reader.read(10)
    type_, class_, ttl, data_len = struct.unpack("!HHIH", data)
    data = reader.read(data_len)
    return DNSRecord(name, type_, class_, ttl, data)


def parse_dns_packet(data):
    reader = BytesIO(data)
    header = parse_header(reader)
    questions = [parse_question(reader) for _ in range(header.num_questions)]
    answers = [parse_record(reader) for _ in range(header.num_answers)]
    authorities = [parse_record(reader) for _ in range(header.num_authorities)]
    additionals = [parse_record(reader) for _ in range(header.num_additionals)]
    return DNSPacket(header, questions, answers, authorities, additionals)


def parse_question(reader):
    name = decode_name(reader)
    data = reader.read(4)
    type_, class_ = struct.unpack("!HH", data)
    return DNSQuestion(name, type_, class_)


def send_query(ip_address, domain_name, record_type):
    query = build_query(domain_name, record_type)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.settimeout(5)  # Add timeout to prevent hanging
        sock.sendto(query, (ip_address, 53))
        data, _ = sock.recvfrom(1024)
        return parse_dns_packet(data)
    except Exception as e:
        raise Exception(f"DNS query failed: {str(e)}")
    finally:
        sock.close()


def get_answer(packet):
    for x in packet.answers:
        if x.type_ == TYPE_A:
            return x.data


def get_nameserver_ip(packet):
    for x in packet.additionals:
        if x.type_ == TYPE_A:
            return x.data


def get_nameserver(packet):
    for x in packet.authorities:
        if x.type_ == TYPE_NS:
            return x.data.decode('utf-8')


def resolve(domain_name, record_type=TYPE_A, nameserver='198.41.0.4'):
    while True:
        # FIXME Recursion and rate limits
        # FIXME Scope the exception
        # print(f'Querying {nameserver} for {domain_name}', end=' ')
        response = send_query(nameserver, domain_name, record_type)
        if ip := get_answer(response):
            return ip_to_string(ip)
        elif nsIP := get_nameserver_ip(response):
            nameserver = nsIP
        elif ns_domain := get_nameserver(response):
            nameserver = resolve(ns_domain, TYPE_A, nameserver=nameserver)
        else:
            raise Exception('something went wrong')


############################################################
# Public API calls - DNS lookup, host lookup, interface IP #
def lookup_domain(domain_name):
    # TODO make resolver a named param w/default to google
    try:
        query = build_query(domain_name, TYPE_A)
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(5)  # Add timeout to prevent hanging
        sock.sendto(query, ('8.8.8.8', 53))
        data, _ = sock.recvfrom(1024)
        response = parse_dns_packet(data)
        return ip_to_string(response.answers[0].data)
    except IndexError:
        # No answers in response
        return None
    except Exception as e:
        print(f"[red]DNS lookup error: {str(e)}[/]")
        return None


def lookup_host(hostname:str, nameserver='8.8.8.8') -> str:
    # Hardwired - non-recursive, A records only
    try:
        response = send_query(nameserver, hostname, TYPE_A)
        if ip := get_answer(response):
            return ip_to_string(ip)
        return None
    except Exception as e:
        print(f"[red]Host lookup error: {str(e)}[/]")
        return None


def get_interface_ip() -> str:
    # Modified from https://stackoverflow.com/questions/166506/finding-local-ip-addresses-using-pythons-stdlib
    # We want to know if we have an IP - usually DHCP but not always
    # so this will use a bit of the socket library and return None if just localhost exists
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        # doesn't even have to be reachable
        s.connect(('8.8.8.8', 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = None
    finally:
        s.close()
    return ip


def have_ip_address() -> bool:
    print("Checking for IP address...", end='')
    ip = get_interface_ip()
    if ip:
        print(f"[green]ok {ip=}[/]")
        return True
    print("[red]fail[/]")
    return False


def can_ping(host: str, timeout=2) -> bool:
    """
    One single ping, to bastardize the movie quote.
    """
    print(f"Pinging {host}...", end='')
    try:
        rc = ping(host, timeout=timeout)
        if rc:
            print("[green]up[/]")
            return True
        print("[red]down[/]")
        return False
    except Exception as e:
        print(f"[red]error: {str(e)}[/]")
        return False


def can_ping_all(hosts: list, timeout=1) -> bool:
    """
    Ping all hosts in a list
    """
    try:
        tf_list = [can_ping(host, timeout=timeout) for host in hosts]
        return all(tf_list)
    except Exception as e:
        print(f"[red]Error in ping_all: {str(e)}[/]")
        return False


def can_resolve_host(host: str, resolver=DNS_DEFAULT_IP) -> bool:
    # Try the Julia Evans code - only depends on stdlib
    print(f"Resolving {host} with {resolver}...", end='')
    try:
        ip = lookup_host(host, nameserver=resolver)
        if ip:
            print(f"[green]ok {ip=}[/]")
            return True
        print("[red]fail[/]")
        return False
    except Exception as e:
        print(f"[red]error: {str(e)}[/]")
        return False


def can_resolve_all_hosts(hosts: list, resolver: str) -> bool:
    tf_list = [can_resolve_host(host, resolver=resolver) for host in hosts]
    return all(tf_list)


def can_lookup_domain(domain: str, resolver: str) -> bool:
    print(f"Looking up {domain} with {resolver}...", end='')
    try:
        res = lookup_domain(domain)
        if res:
            print(f"[green] {res} ok[/]")
            return True
        print("[red]fail - no result[/]")
        return False
    except Exception as e:
        print(f"[red]error: {str(e)}[/]")
        return False


def colorize(tf: bool) -> str:
    if tf:
        return "[green]ok[/]"
    return "[red]fail[/]"

