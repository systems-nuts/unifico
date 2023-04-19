#!/usr/bin/env python3

import os
import sys
import argparse
import json
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.ticker import ScalarFormatter, NullLocator


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def fill_colors(colors, expected_colors):
    if len(colors) < expected_colors:
        eprint("warning: using default values for colors")

        cmap = mpl.colormaps["Greys"]
        step = 1.0 / expected_colors
        for i in range(0, expected_colors):
            if i not in colors:
                colors.append(cmap((i + 1) * step))

    return colors


def plot(datafile, stylefile, configfile, interactive=False):
    plt.style.use(stylefile)

    cfg = json.loads("{}")

    with open(configfile) as jsonfile:
        cfg = json.load(jsonfile)

    cfg_plot = cfg["plot"]

    index_col = cfg_plot.get("index_column", 0)

    filename, _ = os.path.splitext(datafile)
    df = pd.read_csv(datafile, index_col=index_col)

    _, axis = plt.subplots()

    colors = cfg.get("colors", [])
    fill_colors(colors, len(df.columns))

    df.plot(
        ax=axis,
        kind=cfg_plot["kind"],
        logy=cfg_plot["logy"],
        figsize=(cfg_plot["width"], cfg_plot["height"]),
        width=cfg_plot["bar_width"],
        color=colors,
        legend=False,
    )

    cfg_axis = cfg["axis"]

    xticks_cfg = cfg_axis.get("xticks", {})
    plt.xticks(**xticks_cfg)

    axis.set_yscale(cfg_axis["yscale"])
    axis.set_ylim(cfg_axis["ylim"])
    plt.yticks(ticks=cfg_axis["yticks"]["values"])

    axis.yaxis.set_major_formatter(ScalarFormatter())
    axis.yaxis.set_minor_locator(NullLocator())

    axis.set_xlabel(cfg_axis["xlabel"])
    axis.set_ylabel(cfg_axis["ylabel"])

    axis.grid(axis=cfg["axis"]["grid"])

    if cfg_legend := cfg.get("legend", None):
        frame_linewidth = cfg_legend.get("frame_linewidth", 0.5)
        del cfg_legend["frame_linewidth"]

        _, _ = axis.get_legend_handles_labels()
        legend1 = axis.legend(**cfg_legend)
        legend1.get_frame().set_linewidth(frame_linewidth)
    else:
        axis.get_legend().remove()

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
