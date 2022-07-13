import time


def switch_hyperthreading(option):
    """
    Simple python wrapper for Simultaneous Multithreading (SMT) control.
    See: https://serverfault.com/questions/235825/disable-hyperthreading-from-within-linux-no-access-to-bios
    Requires sudo.
    :param option: 'on', 'off' or 'forceoff'
    :return:
    """
    if option in ["on", "off", "forceoff"]:
        with open("/sys/devices/system/cpu/smt/control", "w") as fp:
            fp.write(option)
    else:
        print("Unknown option.")


def switch_cpu(cpu_id_list, option):
    """
    Simple python wrapper for cpu control.
    Switch the cpus in list.
    Requires sudo.
    :param cpu_id_list: list of physical cpu ids as represented in the Linux kernel
    :param option: 0 or 1
    :return:
    """
    if not cpu_id_list:  # Empty list
        return

    if option in ["0", "1"]:
        for cpu_id in cpu_id_list:
            with open(
                "/sys/devices/system/cpu/cpu{}/online".format(str(cpu_id)), "w"
            ) as fp:
                fp.write(option)
            time.sleep(0.1)
            with open(
                "/sys/devices/system/cpu/cpu{}/online".format(str(cpu_id)), "r"
            ) as fp:
                if fp.read(1) != option:
                    exit(1)
    else:
        print("Unknown option.")


if __name__ == "__main__":
    switch_cpu()
