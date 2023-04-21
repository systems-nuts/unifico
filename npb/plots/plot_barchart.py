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


def fill_color(color, expected_color):
    if len(color) < expected_color:
        eprint("warning: using default values for color")

        cmap = mpl.colormaps["Greys"]
        step = 1.0 / expected_color
        for i in range(0, expected_color):
            if i not in color:
                color.append(cmap((i + 1) * step))


def plot(datafile, stylefile, configfile, interactive=False):
    plt.style.use(stylefile)

    cfg = json.loads("{}")

    with open(configfile) as jsonfile:
        cfg = json.load(jsonfile)

    cfg_df = cfg.setdefault("df", {})

    cfg_df.setdefault("index_col", 0)

    filename, _ = os.path.splitext(datafile)
    df = pd.read_csv(datafile, **cfg_df)

    _, axis = plt.subplots()

    cfg_plot = cfg.setdefault("plot", {})

    color = cfg_plot.get("color", [])
    fill_color(color, len(df.columns))
    cfg_plot["color"] = color

    cfg_plot["figsize"] = tuple(cfg_plot.setdefault("figsize", (8, 5)))

    plot_kind = cfg_plot.setdefault("kind", "bar")
    cfg_plot_kind = cfg.setdefault(plot_kind, {})

    df.plot(ax=axis, legend=False, **cfg_plot, **cfg_plot_kind)

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
