#!/usr/bin/env python
import re, sys, os


def cmp(a, b):
    return (a > b) - (a < b)


# Small struct to keep data about each logical processor
class Processor:
    def __init__(self, processor, core, node, socket):
        self.processor = processor
        self.core = core
        self.node = node
        self.socket = socket

    def __cmp__(self, other):
        return cmp(self.processor, other.processor)


def shift(l, n):
    return l[n:] + l[:n]


def sortAndShift(l):
    return shift(sorted(l), 1)


# Given a processor ID, return its corresponding NUMA node
def determineNode(processor):
    files = os.listdir("/sys/devices/system/cpu/cpu{0}".format(processor))
    for f in files:
        match = re.search("node(\d+)", f)
        if match:
            return match.group(1)

    # No NUMA node found - return -1
    return "-1"


# Parse /proc/cpuinfo
def parseProcessorInfo(raw):
    info = {}

    for rawProcessor in raw.split("\n\n")[:-1]:
        match = re.search("processor\s+:\s(\d+)", rawProcessor)
        processor = int(match.group(1))

        match = re.search("physical id\s+:\s(\d+)", rawProcessor)
        socket = int(match.group(1))

        match = re.search("core id\s+:\s(\d+)", rawProcessor)
        core = int(match.group(1))

        # Determine memory node
        node = int(determineNode(processor))

        processorObj = Processor(processor, core, node, socket)

        if socket not in info:
            info[socket] = {}

        if node not in info[socket]:
            info[socket][node] = {}

        if core not in info[socket][node]:
            info[socket][node][core] = []

        info[socket][node][core].append(processorObj)

    return info


def printTopology(info):
    sockets = 0
    cores = 0
    processors = 0
    nodes = 0

    for socket in sorted(info.keys()):
        sockets += 1
        print("Package " + str(socket))

        for node in sorted(info[socket].keys()):
            nodes += 1
            print("\tNUMA node " + str(node))

            for core in sorted(info[socket][node].keys()):
                cores += 1
                print("\t\tPhysical core " + str(core))

                for processor in sorted(info[socket][node][core]):
                    processors += 1
                    print("\t\t\tProcessor: " + str(processor.processor))

    print(
        "\nIn total, there are {0} physical packages (sockets), {1} NUMA nodes, "
        "{2} physical cores and {3} hardware threads\n".format(
            str(sockets), str(nodes), str(cores), str(processors)
        )
    )


# Avoid using processor 0, only put at the very last,
# since it's normally used by the OS, interrupts etc
def scatter(socket, node, core, processor, info):
    if socket >= len(info):
        return scatter(0, node + 1, core, processor, info)

    socketID = sortAndShift(info.keys())[socket]
    if node >= len(info[socketID]):
        return scatter(socket, 0, core + 1, processor, info)

    nodeID = sortAndShift(info[socketID].keys())[node]
    if core >= len(info[socketID][nodeID]):
        return scatter(socket, node, 0, processor + 1, info)

    coreID = sortAndShift(info[socketID][nodeID].keys())[core]
    if processor >= len(info[socketID][nodeID][coreID]):
        return []

    target = sortAndShift(info[socketID][nodeID][coreID])[processor].processor
    return [target] + scatter(socket + 1, node, core, processor, info)


def compact(info):
    mapping = []
    # For each socket
    for socket in sortAndShift(info.keys()):
        # For each node
        for node in sortAndShift(info[socket].keys()):
            # For each core
            for core in sortAndShift(info[socket][node].keys()):
                # For each hardware thread
                for thread in sortAndShift(info[socket][node][core]):
                    mapping.append(thread.processor)

    return mapping


def main():
    if len(sys.argv) > 2:
        print("Error: Too many arguments")
        print("Usage: {0} [affinity mapping]".format(sys.argv[0]))
        sys.exit(1)

    with open("/proc/cpuinfo") as f:
        rawInfo = f.read()

    info = parseProcessorInfo(rawInfo)

    if len(sys.argv) == 1:
        printTopology(info)

    # The script can also output some affinity mappings
    # For example, running ./cpu-topology.py scatter will
    # output a scatter affinity which will distribute
    # the cores/processes as evenly as possible
    if len(sys.argv) == 2:
        affinity = sys.argv[1]
        if affinity == "scatter":
            print(",".join(str(x) for x in scatter(0, 0, 0, 0, info)))
        elif affinity == "compact":
            print(",".join(str(x) for x in compact(info)))
        else:
            print(
                "Error: Unrecognized affinity mapping '{0}'".format(affinity)
            )


if __name__ == "__main__":
    main()
