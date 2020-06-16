#!/usr/bin/env python
from random import choice, randint
import click


SERVICE_PORTS = [80, 443, 8080, 25, 22]


def inet_aton(network):
    parts = network.strip().split('.')
    return (
        int(parts[0]) << 24 | int(parts[1]) << 16 | int(parts[2]) << 8 | int(parts[3])
    )


def inet_ntoa(uint32):
    parts = []
    parts.append((uint32 & 0xFF000000) >> 24)
    parts.append((uint32 & 0x00FF0000) >> 16)
    parts.append((uint32 & 0x0000FF00) >> 8)
    parts.append(uint32 & 0x000000FF)
    return ".".join([str(part) for part in parts])


def random_ip_in_network(network):
    ip = network.strip()
    if '/' not in ip:
        return ip

    # Split into network addr and CIDR bits count
    network, cidr_bits = ip.split('/')

    # Create bitmasks for Host and Network sections
    host_mask = (1 << (32 - int(cidr_bits))) - 1
    # network_mask = 0xFFFFFFFF - host_mask

    # Convert string to int
    network_int = inet_aton(network)
    network_int += randint(0, host_mask - 1)

    return inet_ntoa(network_int)


@click.command()
@click.argument('src_nets', type=click.File("r"))
@click.argument('dst_nets', type=click.File("r"))
@click.option('--port', '-p', 'ports', type=int, multiple=True, default=[443],
              help=("Add port to list of 'server ports' to choose from."))
@click.option('--count', '-c', 'count', type=int, default=100,
              help=("Specify number of flows to generate."))
# @click.option('--random-cap', '-r', 'random_cap', type=int, default=0)
def main(src_nets, dst_nets, ports, count):
    """
    Random IPs - Within network ranges

    When supplied with two files, containing lists of networks, specified
    as A.B.C.D/CIDR, will generate upto 'count' IP flows, "From" a random
    network in the source networks, "To" a random network in the destination
    networks. Each time a flow is created there is a 1-in-3 chance that
    an existing flow will be taken from those already generated and the
    source and destination information will be swapped, simulating response
    traffic.

    Note: It is quite possible the randomly selected flow was the result of
    being randomly selected as well. This would result in a "double-swap" of
    sorts. That's fine. In _theory_ (totally unproven, btw) this will add
    some random weighting to request vs. response traffic.

    Additional ports can be specified for selection as the source. The idea
    is to use common service port numbers, like 443. This can be specified
    multiple times.
    """
    result_set = []

    source_networks = [s.split('#')[0].strip() for s in src_nets.readlines()]
    dest_networks = [d.split('#')[0].strip() for d in dst_nets.readlines()]

    i = 0
    while i < count:
        # 1 in 3 chance of add reversed existing flow
        if randint(0, 1000000) % 3 == 0 and len(result_set) > 0:
            flowstr = choice(result_set)
            # swap fields
            parts = flowstr.split()
            flowstr = "{} {} {} {} 6".format(parts[2], parts[3], parts[0], parts[1])
        else:
            src_addr = random_ip_in_network(choice(source_networks))
            dst_addr = random_ip_in_network(choice(dest_networks))
            port = choice(ports)
            flowstr = "{} {} {} {} 6".format(src_addr, port, dst_addr, randint(32000, 60000))
        result_set.append(flowstr)
        print(flowstr)
        i += 1


if __name__ == "__main__":
    main()
