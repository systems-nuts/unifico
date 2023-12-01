import re
import pandas as pd

PERF_STATS_REGEX = r"(\w+)\s(\d+)"


def parse_perf_output(src):
    """Parses the folded version of perf output and returns the time spent on each function.

    Example:

    -----
    sh;_int_malloc;page_fault;error_entry 1
    sh;_init;handle_mm_fault 1
    -----

    This should return the following dictionary:

    {
        "error_entry": 1,
        "handle_mm_fault": 1
    }

    @param src: Path to file
    @return: dictionary
    """
    result = {}
    with open(src, "r") as fp:
        lines = fp.readlines()

        for line in lines:
            match_result = re.search(PERF_STATS_REGEX, line)

            if match_result:
                function = match_result.group(1)
                time = match_result.group(2)
                result.setdefault(function, 0)
                result[function] += int(time)

    return result


def get_weights(function_dict):
    """

    @param function_dict:
    @return:
    """
    total_time = sum(function_dict.values())
    for key, value in function_dict.items():
        function_dict[key] = value / total_time

    return function_dict


def print_weighted_pressure(pressure_src, function_weights):
    """

    @param pressure_src:
    @param function_weights:
    @return:
    """
    df = pd.read_csv(pressure_src)
    for index, row in df.iterrows():
        function_name = row["function"]
        function_pressure = row["pressure"]
        print(
            function_name
            + ","
            + str(function_pressure * function_weights[function_name])
        )


if __name__ == "__main__":
    weights = get_weights(parse_perf_output("test/out.folded"))
    print_weighted_pressure("test/pressure-output.txt", weights)
