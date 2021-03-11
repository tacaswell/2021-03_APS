import sys

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from gen_data import get_data, fit


def _plot_zeta(ax, fits_df):
    ax.set_ylabel(r"$\zeta$")
    ax.set_xlabel("control (arb)")
    ax.set_ylim(0, 0.08)
    return ax.plot(
        fits_df["zeta"], marker="o", color="k", label="\N{greek small letter zeta}"
    )


def _plot_omega(ax, fits_df):
    ax.set_ylabel(r"$\omega_0/2\pi$ (kHz)")
    ax.set_xlabel("control (arb)")
    ax.set_ylim(0.25, 1.25)
    return ax.plot(
        fits_df["omega"] / (2 * np.pi),
        marker="o",
        color="k",
        label="\N{greek small letter omega}",
    )


def _plot_several(ax, d, fits):
    out = []

    for j, (m, popt) in enumerate(zip(d, fits)):
        arts = plot_one(ax, m, popt, offset=3.75 * j)
        out.append(arts)

    ax.set_xlabel("time (ms)")
    ax.set_ylabel("displacement (mm)")

    return out


def subfigure_label(ax, text):
    return ax.annotate(
        text,
        # units are (axes-fraction, axes-fraction)
        # # this is bottom right
        # xy=(1, 0),
        # this is the top left
        xy=(0, 1),
        xycoords="axes fraction",
        # units are absolute offset in points from xy
        xytext=(-5, 5),
        textcoords=("offset points"),
        # set the text alignment
        ha="right",
        va="bottom",
        fontweight="bold",
        fontsize="larger",
    )


def plot_one(ax, m, popt, offset=0):
    # pull what we want out of the xarray
    control = float(m.coords["control"])
    t = m.coords["time"]
    z = m.values

    (ln,) = ax.plot(t, z + offset, label=f"C: {control:.1f}")
    (fit,) = ax.plot(t, popt.sample(t) + offset, color="k")
    ann = ax.annotate(
        f"$C={control:.1f}$\n$\\zeta={popt.zeta:.2g}$ $\\omega_0={popt.omega:.2f}$",
        # units are (axes-fraction, data)
        xy=(0.95, offset + 0.5),
        xycoords=ax.get_yaxis_transform(),
        # set the text alignment
        ha="right",
        va="bottom",
    )
    return {"raw": ln, "fit": fit, "annotation": ann}


def paper_figure_2(fig, layout, d, fits, *, plot_every=5):
    ax_dict = fig.subplot_mosaic(layout)
    assert set(ax_dict) == set("ABC")

    fits_df = pd.DataFrame(fits, index=d.coords["control"])

    index = list(range(0, len(d), plot_every))

    artists = {
        "vibrations": _plot_several(ax_dict["A"], d[index], [fits[i] for i in index]),
        "zeta": _plot_zeta(ax_dict["B"], fits_df),
        "omega": _plot_omega(ax_dict["C"], fits_df),
    }

    fig.align_ylabels(list(ax_dict.values()))
    subplot_labels = {
        k: subfigure_label(v, f"({k.lower()})") for k, v in ax_dict.items()
    }

    return (fig, ax_dict, artists, subplot_labels)


d = get_data(25)
fits = [fit(m) for m in d]
paper_figure_2(plt.figure(constrained_layout=True), "ABC", d, fits, plot_every=5)

single_col_width = 8.6 / 2.54  # single column APS figure
double_col_width = 17.8 / 2.54  # double column APS figure

layout = """
AB
AC
"""

fig, axs, arts, labels = paper_figure_2(
    plt.figure(
        constrained_layout=True, figsize=(double_col_width, double_col_width * 0.5)
    ),
    layout,
    d,
    fits,
    plot_every=5,
)
paper_figure_2(
    plt.figure(
        constrained_layout=True, figsize=(double_col_width, double_col_width * 0.5)
    ),
    "AABC",
    d,
    fits,
)
paper_figure_2(
    plt.figure(
        constrained_layout=True, figsize=(single_col_width, single_col_width * 2.5)
    ),
    "A\nB\nC",
    d,
    fits,
    plot_every=10,
)
