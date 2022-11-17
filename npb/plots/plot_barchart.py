#!/usr/bin/env python3

import os
import sys
import argparse
import json
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.ticker import ScalarFormatter, NullLocator


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def fill_colors(colors, expected_colors):
    if len(colors) < expected_colors:
        eprint("warning: using default values for colors")

        cmap = cm.get_cmap("Greys")
        step = 1.0 / expected_colors
        for i in range(0, expected_colors):
            if i not in colors:
                colors.append(cmap((i + 1) * step))

    return colors


def plot(datafile, stylefile, configfile, interactive=False):
    plt.style.use(stylefile)

    filename, _ = os.path.splitext(datafile)
    df = pd.read_csv(datafile)

    cfg = json.loads("{}")

    with open(configfile) as jsonfile:
        cfg = json.load(jsonfile)

    _, axis = plt.subplots(1, 1)

    colors = []

    try:
        colors = cfg["colors"]
    except KeyError:
        pass

    fill_colors(colors, len(df.columns))

    cfg_plot = cfg["plot"]

    df.plot(
        kind=cfg_plot["kind"],
        logy=cfg_plot["logy"],
        ax=axis,
        figsize=(cfg_plot["width"], cfg_plot["height"]),
        width=cfg_plot["bar_width"],
        color=colors,
    )

    cfg_axis = cfg["axis"]

    plt.xticks(rotation=cfg_axis["xticks"]["rotation"]),
    axis.set_yscale(cfg_axis["yscale"])

    axis.set_ylim(cfg_axis["ylim"])
    plt.yticks(ticks=cfg_axis["yticks"]["values"])

    axis.yaxis.set_major_formatter(ScalarFormatter())
    axis.yaxis.set_minor_locator(NullLocator())

    axis.set_xlabel(cfg_axis["xlabel"])
    axis.set_ylabel(cfg_axis["ylabel"])

    cfg_legend = cfg["legend"]

    axis.legend(
        title=cfg_legend["title"],
        bbox_to_anchor=cfg_legend["anchor"],
        ncol=cfg_legend["columns"],
    )
    axis.get_legend().get_frame().set_linewidth(cfg_legend["frame_linewidth"])

    axis.grid(axis=cfg["axis"]["grid"])

    if interactive:
        plt.show()
    else:
        pp = PdfPages(filename + ".pdf")
        plt.savefig(pp, format="pdf")
        pp.close()


#

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate bar chart.")
    parser.add_argument(
        "-f",
        "--file",
        const=str,
        nargs="?",
        help="Input data file in CSV format",
    )
    parser.add_argument(
        "-s",
        "--style",
        const=str,
        nargs="?",
        help="Style sheet configuration file for plotting parameters",
    )
    parser.add_argument(
        "-c",
        "--config",
        const=str,
        nargs="?",
        help="Supplementary configuration file for plotting parameters",
    )
    parser.add_argument(
        "-i",
        "--interactive",
        action="store_true",
        help="Display interactive plot only",
    )
    args = parser.parse_args()

    plot(args.file, args.style, args.config, args.interactive)
