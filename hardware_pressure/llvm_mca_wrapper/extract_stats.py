from jsonstream import load

EXAMPLE_JSON = 'json_examples/fact_x86-64.json'


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


if __name__ == '__main__':
    mca = parse_mca_json(EXAMPLE_JSON)
    print(resource_pressure(mca))
