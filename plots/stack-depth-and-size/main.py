import logging
import os
import re
import matplotlib.pyplot as plt
import zipfile

# logging.basicConfig(level=logging.DEBUG, format='%(message)s')

BENCHMARKS_NAMES = ["npb", "spec"]

BENCHMARKS_FOLDERS = {
    "spec": {
        "600.perlbench_s": "perlbench_s_bas",
        "602.gcc_s": "sgcc_base.gccba",
        "605.mcf_s": "mcf_s_base.gccb",
        "619.lbm_s": "lbm_s_base.gccb",
        "620.omnetpp_s": "omnetpp_s_base.",
        "623.xalancbmk_s": "xalancbmk_s_bas",
        "625.x264_s": "x264_s_base.gcc",
        "631.deepsjeng_s": "deepsjeng_s_bas",
        "638.imagick_s": "imagick_s_base.",
        "641.leela_s": "leela_s_base.gc",
        "644.nab_s": "nab_s_base.gccb",
        "657.xz_s": "xz_s_base.gccba",
    },
    "npb": {
        "bt.B.x": "bt.B",
        "cg.B.x": "cg.B",
        "ep.B.x": "ep.B",
        "ft.B.x": "ft.B",
        "is.B.x": "is.B",
    },
}


def get_next_function(lines):
    if not lines:
        raise Exception("There is no more function record.")
    if is_non_plt_function_def(lines[0]):
        return lines[0]
    return get_next_function(lines[1:])


def is_non_plt_function_def(line):
    return is_function_def(line) and not_plt_def(line)


def not_plt_def(line):
    return "@plt" not in line


def is_function_def(line):
    return re.search(r"<.*>:", line)


def is_sub_rsp(line):
    return re.search(r"sub.*,%rsp", line)


def get_next_size(lines):
    if not lines:
        return None
    if is_sub_rsp(lines[0]):
        return lines[0]
    if is_non_plt_function_def(lines[0]):
        return None
    return get_next_size(lines[1:])


def trim_non_push_and_sub_instructions(instructions):
    i = 0
    while i != len(instructions) and (
        ("push   %" in instructions[i]) or ("sub    $0x" in instructions[i])
    ):
        i += 1
    return instructions[:i]


def calculate_function_size(instructions):
    size = 16
    for i in instructions:
        if "push" in i:
            size += 8
        if "sub" in i:
            if ",%rsp" not in i:
                break
            search = re.search(r"sub.*,%rsp", i)
            group = search.group()
            s = group[len("sub    $0x") : -len(",%rsp")]
            sub_size = int(s, 16)
            size += sub_size
    return size


def stack_states_with_size_and_duration(
    functions_sizes, perf_txt=None, benchmark_name=None
):
    logging.info("Reading folded perf file.")
    with open(perf_txt) as file:
        lines = file.readlines()
    lines = [line.rstrip() for line in lines]
    lines = [line for line in lines if line.startswith(benchmark_name)]
    _ = []
    for line in lines:
        frames = line[: line.rfind(" ")]
        duration = int(line[line.rfind(" ") + 1 :])
        _.append((frames, duration))
    lines = _
    stack_states = []
    unresolved = set()
    for line in lines:
        assert len(line) == 2
        duration = int(line[1])

        frames = line[0].split(";")[1:]
        sizes = []
        for frame in frames:
            size = functions_sizes.get(frame, None)
            if size is None:
                unresolved.add(frame)
                sizes.append(24)
            else:
                sizes.append(size)

        stack_states.append((sizes, duration))
    logging.info("Unresolved frames:\n %s" % unresolved)
    return stack_states


def parse_and_calculate_function_sizes(asm_file):
    logging.info("Reading assembly file.")
    with open(asm_file) as file:
        lines = file.readlines()
    lines = [line.rstrip() for line in lines]
    lines = [line for line in lines if line != ""]
    in_text = False
    functions = []
    for line in lines:
        if in_text and line.startswith("Disassembly of section"):
            logging.info("End of parsing .text section.")
            break

        if not in_text:
            if line.startswith("Disassembly of section .text:"):
                in_text = True
                logging.info("Start of parsing .text section.")
            continue

        if is_non_plt_function_def(line):  # functions
            function_name = re.search(r"<.*>:", line).group()[1:-2]
            if "(" in function_name:
                function_name = function_name[: function_name.find("(")]
            functions.append([function_name, []])
        else:  # instructions
            functions[-1][1].append(line)
    functions_sizes = {}
    for f in functions:
        functions_sizes[f[0]] = calculate_function_size(
            trim_non_push_and_sub_instructions(f[1])
        )
    return functions_sizes


def main():
    for benchmarks_name in BENCHMARKS_NAMES:
        benchmarks_folder = "./" + benchmarks_name
        with zipfile.ZipFile(
            "./" + benchmarks_name + ".stack.zip", "r"
        ) as zip_ref:
            zip_ref.extractall("./")
        spec_sizes = {}
        for benchmark_folder in [
            name
            for name in os.listdir(benchmarks_folder)
            if os.path.isdir(os.path.join(benchmarks_folder, name))
        ]:
            asm_file = os.path.join(
                benchmarks_folder, benchmark_folder, "asm.s"
            )
            functions_sizes = parse_and_calculate_function_sizes(asm_file)

            benchmark_name = BENCHMARKS_FOLDERS[benchmarks_name][
                benchmark_folder
            ]
            perf_txt = os.path.join(
                benchmarks_folder, benchmark_folder, "out.folded"
            )
            stack_states = stack_states_with_size_and_duration(
                functions_sizes, perf_txt, benchmark_name
            )

            stack_states_sizes = [
                (sum(stack_state[0]), stack_state[1])
                for stack_state in stack_states
            ]
            sizes = []
            for i in stack_states_sizes:
                sizes.extend(i[1] * [i[0]])
            spec_sizes[benchmark_name] = sizes
            plt.xlabel("Time")
            plt.ylabel("Stack Size (Bytes)")
            plt.title(benchmark_folder)
            plt.plot(sizes)
            plt.savefig("%s.stack-size.jpeg" % benchmark_folder)
            plt.close()
            plt.cla()
            plt.clf()

            counts = []
            for i in stack_states:
                counts.extend(i[1] * [len(i[0])])
            plt.xlabel("Time")
            plt.ylabel("Stack Frames Count (#)")
            plt.title(benchmark_folder)
            plt.plot(counts)
            plt.savefig("%s.stack-depth-and-size.jpeg" % benchmark_folder)
            plt.close()
            plt.cla()
            plt.clf()


if __name__ == "__main__":
    main()
