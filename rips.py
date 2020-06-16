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
@click.option('--port', '-p', 'ports', type=int, multiple=True, default=[443])
@click.option('--count', '-c', 'count', type=int, default=100)
# @click.option('--random-cap', '-r', 'random_cap', type=int, default=0)
def main(src_nets, dst_nets, ports, count):
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
