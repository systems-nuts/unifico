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


def plot(datafile, stylefile, configfile, interactive=False, sort=False):
    plt.style.use(stylefile)

    cfg = json.loads("{}")

    with open(configfile) as jsonfile:
        cfg = json.load(jsonfile)

    cfg_df = cfg.setdefault("df", {})

    cfg_df.setdefault("index_col", 0)

    filename, _ = os.path.splitext(datafile)
    df = pd.read_csv(datafile, **cfg_df)

    if sort:
        df.sort_index(inplace=True, key=lambda col: col.str.swapcase())

    _, axis = plt.subplots()

    cfg_plot = cfg.setdefault("plot", {})

    color = cfg_plot.get("color", [])
    fill_color(color, len(df.columns))
    cfg_plot["color"] = color

    cfg_plot["figsize"] = tuple(cfg_plot.setdefault("figsize", (8, 5)))

    plot_kind = cfg_plot.setdefault("kind", "bar")
    cfg_plot_kind = cfg.setdefault(plot_kind, {})

    df_all = []
    group_labels = []

    group_cfg = cfg.get("group", None)

    if group_cfg and (groupby := group_cfg.get("by", None)):
        df_grouped = df.groupby(groupby)
        for dfg in df_grouped:
            for w in dfg[0]:
                group_labels.append(w)
            g = dfg[1].drop(groupby, axis=1)
            df_all.append(g)
    else:
        df_all.append(df)

    for i, dfpart in enumerate(df_all):
        dfpart.plot(ax=axis, legend=False, **cfg_plot, **cfg_plot_kind)

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

    nstacks = len(df_all[0].columns)
    ncolumns = len(df_all)

    xticks = axis.xaxis.get_major_locator().locs

    if cfg_legend := cfg.get("legend", None):
        frame_linewidth = cfg_legend.get("frame_linewidth", 0.5)
        del cfg_legend["frame_linewidth"]

        h, labels1 = axis.get_legend_handles_labels()
        legend1 = axis.legend(h[:nstacks], labels1[:nstacks], **cfg_legend)
        legend1.get_frame().set_linewidth(frame_linewidth)

        if group_cfg:
            hatches = group_cfg["hatches"]
            alphas = group_cfg["alphas"]
            width = axis.patches[0].get_width()
            mid_point = ncolumns * width / 2.0

            for i in range(0, ncolumns * nstacks, nstacks):
                ncol = int(i / nstacks)
                for j, pa in enumerate(h[i : (i + nstacks)]):
                    for k, rect in enumerate(pa.patches):
                        rect.set_x(xticks[k] - mid_point + ncol * width)
                        rect.set_hatch(hatches[ncol])
                        rect.set_alpha(alphas[ncol])

            # add invisible data to add another legend
            n = []
            for i in range(ncolumns):
                bar_params = {
                    "color": "gray",
                    "alpha": alphas[i],
                    "hatch": hatches[i],
                    "width": 0,
                }
                n.append(axis.bar(0, 0, **bar_params))

            groups_legend_params = group_cfg.get("legend", {})

            groups_legend = plt.legend(n, group_labels, **groups_legend_params)

            axis.add_artist(groups_legend)
            axis.add_artist(legend1)
    else:
        axis.get_legend().remove()

    if v := cfg_axis.get("xticks_expand_by", 0):
        xticks_cfg["ticks"] = [xticks[0] - v, *xticks, xticks[-1] + v]
        plt.xticks(**xticks_cfg)

    nstack = len(df_all[0].columns)

    to_label = None
    if group_cfg:
        for i in group_cfg.get("patches_to_label", []):
            to_label = [
                j
                for j in range(i, i + len(axis.containers) - ncolumns, nstack)
            ]

    if to_label and (patch_label_cfg := group_cfg.get("patch_label", None)):
        for j, p in enumerate(axis.containers):
            if j in to_label:
                axis.bar_label(p, **patch_label_cfg)

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
    parser.add_argument(
        "--sort",
        action="store_true",
        help="Display interactive plot only",
    )
    args = parser.parse_args()

    plot(args.file, args.style, args.config, args.interactive, args.sort)
