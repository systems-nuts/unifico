import os
import re

from utilities.switch_cpu import switch_cpu


class SystemTopology:
    def __init__(self, lstopo_out=None):
        """
        Class for representing the system's topology.
        Requires `lstopo-no-graphics` of Linux
        """
        if lstopo_out is None:
            lstopo_out = "/tmp/lstopo_output.txt"
            os.system("lstopo-no-graphics -p >{}".format(lstopo_out))

        # Open file
        with open(lstopo_out, "r") as fp:
            # Regular expressions
            package_pattern = re.compile("Package[ \t]+P#([0-9]+)")
            core_pattern = re.compile("Core[ \t]+P#([0-9]+)")
            pu_pattern = re.compile("PU[ \t]+P#([0-9]+)")

            cur_node = -1
            cur_package = -1  # TODO
            cur_core = -1

            # Scanning file
            self.packages = []
            for line in fp:
                package_match = package_pattern.search(line)
                if package_match:
                    cur_package = package_match.group(1)
                    package_dict = {"id": cur_package, "cores": []}
                    self.packages.append(package_dict)
                    continue

                package_match = package_pattern.search(line)
                if package_match:
                    cur_package = package_match.group(1)
                    package_dict = {"id": cur_package, "cores": []}
                    self.packages.append(package_dict)
                    continue

                core_match = core_pattern.search(line)
                if core_match:
                    cur_core = core_match.group(1)
                    core_dict = {"id": cur_core, "cpus": []}
                    package_dict["cores"].append(core_dict)
                    continue

                pu_match = pu_pattern.search(line)
                if pu_match:
                    cur_pu = pu_match.group(1)
                    if (
                        cur_package == -1 or cur_core == -1
                    ):  # TODO: check if necessary
                        print(
                            "Error cur_package "
                            + str(cur_package)
                            + " cur_core "
                            + str(cur_core)
                            + " on line "
                            + str(line)
                        )
                        continue
                    core_dict["cpus"].append(cur_pu)

        self.core_num = 0
        self.compact_affinity_order = []  # TODO: add more variations
        for package in self.packages:
            self.core_num += len(package["cores"])
            for core in package["cores"]:
                self.compact_affinity_order.extend(core["cpus"])

        self.cpu_num = len(self.compact_affinity_order)
        self.scattered_affinity_order = list(range(0, self.cpu_num))

    def switch_cpus(self, thread_num, affinity_type, option):
        """
        Set up the system for a specific affinity_type by deactivating cpus based on the number of thread_num.
        :param thread_num: Number of threads to run
        :param affinity_type: 'compact' or 'scatter'  # TODO: add more
        :param option: '0' or '1'
        :return:
        """
        if affinity_type == "compact":
            cpus_to_deactivate = self.compact_affinity_order[thread_num:]
        else:
            cpus_to_deactivate = self.scattered_affinity_order[thread_num:]
        switch_cpu(cpus_to_deactivate, option)

    def reset_cpus(self):  # TODO: change
        """
        Switch all cpus on.
        Start from cpu1. Usually we can't mess with cpu0 anyway.
        :return:
        """
        switch_cpu(self.scattered_affinity_order[1:], "1")


if __name__ == "__main__":
    system_topology = SystemTopology(
        "/home/blackgeorge/Documents/phd/unified_abi/utilities/temp.txt"
    )
    print(system_topology)
