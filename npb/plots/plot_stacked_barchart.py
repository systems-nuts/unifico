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
        dfpart.plot(
            ax=axis,
            sharey=True,
            sharex=True,
            kind=cfg_plot["kind"],
            stacked=cfg_plot["stacked"],
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
            width = cfg_plot["bar_width"]
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

    to_label = []
    for i in group_cfg.get("patches_to_label", []):
        to_label.extend(
            j for j in range(i, i + len(axis.containers) - ncolumns, nstack)
        )

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
    args = parser.parse_args()

    plot(args.file, args.style, args.config, args.interactive)
