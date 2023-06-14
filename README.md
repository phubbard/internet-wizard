# What is this?

I have a decent home network, which is also a sort-of hobby. Whenever it has issues, I have a list of commands I run, from which I infer what's wrong.

In this project I hope to automate that.

# Constraints

I want to run this from my iPad, using Pyto, Juno, a-Shell, Carnets or similar. This limits me to Python 3, its 
standard libraries and any Python-only packages. No C binaries, for example.


## Plan

Step one - use Python to automate the ping / dns tests

In progress. The DNS library exceptions are a bit weird, but I think I can figure it out.

Step two - refactor using a goal-seeking algorithm. For each step,
it should print out success / failure, what it might mean and how to reset / resolve / fix / reboot.

## How it works (step one)

The config.py file contains a few lists and constants. I want to test

1. Local ping by IP. Most-basic. DHCP and connectivity.
2. Local ping by hostname. DNS and domain default working.
3. Local ping wifi, router and modem - respectively.
4. TODO - ping next upstream box. Discover via traceroute / TTL cleverness.
5. Ping google, cloudflare and Level3 DNS servers by IP. IP connectivity.
6. Ping google and cloudflare by hostname - full connectivity.
7. Resolve remote hosts and domains
8. TODO Protocol-level connectivity - use Requests to get a web page from local and remote hosts.

## Rules and inference

Once we have facts, e.g. 'the modem pings but remote DNS is failing' I want the code to make inferences
and suggest remedies. Gotta be a rule-based system engine out there, so after I get the base code solid I'll 
go after that next.

# Installation and use
Right now, the code is aimed at my network (see config.py). I'm working on making it more generic.

