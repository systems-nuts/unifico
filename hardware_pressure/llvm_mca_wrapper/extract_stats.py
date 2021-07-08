import os
import matplotlib.pyplot as plt

from jsonstream import load

EXAMPLE_JSON = 'json_examples/fact_aarch64.json'


def parse_mca_json(file_path):
    """Decode the json file produced by llvm-mca tool

    llvm-mca with the `--json` option returns a file with a list of JSON objects one after the other.
    So, we parse them with the `jsonstream` library: 
    https://pypi.org/project/jsonstream/
    and we return a dictionary with keys:
    
    * InstructionInfo
    * Summary
    * Timeline
    * ResourcePressure

    Works with LLVM 13.
    Currently, the info contained in the JSON file is described briefly here:
    https://reviews.llvm.org/D86644?id=318077
    @param file_path
    @return: list of json objects
    """
    with open(file_path, 'r') as fp:
        stats_list = list(load(fp))

    mca_dict = {
        'InstructionInfo': stats_list[0],
        'Summary': stats_list[1],
        'Timeline': stats_list[2],
        'ResourcePressure': stats_list[3]
    }
    return mca_dict


def resource_pressure(mca_dict):
    """Get a dictionary with the total pressure for every hardware resource in the mca_dict

    Suppose that the mca_dict contains `n` instructions.
    Their indices are numbered from 0 to `n - 1`.
    Currently, the element indexed `n` inside the list given by the `ResourcePressureInfo` key,
    is the resource pressure per iteration, for the specific hardware resource.
    So, we just return these elements of the list for every resource index.
    @param mca_dict: a dictionary as returned by the function `parse_mca_json`
    @return: dictionary with total pressures
    """
    n = len(mca_dict['Timeline'])
    resources = mca_dict['InstructionInfo']['Resources']['Resources']  # Resources names

    return {
        resources[instr_dict['ResourceIndex']]: instr_dict['ResourceUsage']
        for instr_dict in mca_dict['ResourcePressure']['ResourcePressureInfo']
        if instr_dict['InstructionIndex'] == n
    }


def sort_by_pressure(folder_path, target_resources):
    """Sort the assembly files in a folder based on hardware pressure

    Calculates the hardware pressure for the given resources, for all the resources of the JSON files in a folder.
    Returns a list with the hardware pressure in ascending order.
    Hardware pressure per file is summed for all the resources.
    JSON files are created through the `llvm-mca --json` command and must be of the same architecture.
    @param folder_path: the location of the json files
    @param target_resources: list of processor resources
    @return: list with program names with their pressures in ascending order
    """
    result = []
    for file in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file)
        mca_dict = parse_mca_json(file_path)
        pressure_dict = resource_pressure(mca_dict)
        total_pressure = sum([pressure_dict[resource]
                              for resource in pressure_dict.keys()
                              if resource in target_resources])
        result.append([file, total_pressure])

    result = sorted(result, key=lambda x: x[1])  # Sort list of tuples based on the 2nd argument, i.e. total_pressure

    return list(zip(*result))


def plot_by_pressure(folder_path, target_resources):
    """Plot the assembly files in a folder based on hardware pressure

    Calculates the hardware pressure for the given resources, for all the resources of the JSON files in a folder.
    Plots the hardware pressure for every in ascending order.
    Hardware pressure per file is summed for all the resources.
    JSON files are created through the `llvm-mca --json` command and must be of the same architecture.
    @param folder_path: the location of the json files
    @param target_resources: list of processor resources
    @return:
    """
    pressure_list = sort_by_pressure(folder_path, target_resources)
    plt.bar(pressure_list[0], pressure_list[1])
    plt.show()


if __name__ == '__main__':
    mca = parse_mca_json(EXAMPLE_JSON)
    print(resource_pressure(mca))
    print(sort_by_pressure('json_examples', ['JALU0', 'JDiv']))
    print(sort_by_pressure('json_examples', ['THX2T99P0']))
    plot_by_pressure('json_examples', ['JALU0', 'JDiv'])
    plot_by_pressure('json_examples', ['THX2T99P0'])
