# %%
from pathlib import Path
from gen_data import get_data, fit
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# %%
d = get_data(25)
# fit all of the curves
fits = [fit(m) for m in d]
# put the fit values is a DataFrame
fits_df = pd.DataFrame(fits, index=d.coords["control"])

# %%
def plot_zeta(ax, fits_df):
    ax.set_ylabel(r"$\zeta$")
    ax.set_xlabel("control (arb)")
    ax.set_ylim(0, 0.08)
    return ax.plot(
        fits_df["zeta"],
        marker="o",
        color="k",
        label="\N{greek small letter zeta}",
        linestyle="",
    )


def plot_omega(ax, fits_df):
    ax.set_ylabel(r"$\omega_0/2\pi$ (kHz)")
    ax.set_xlabel("control (arb)")
    ax.set_ylim(0, 1.25)
    return ax.plot(
        fits_df["omega"] / (2 * np.pi),
        marker="o",
        color="k",
        label="\N{greek small letter omega}",
    )


# %%


def plot_one(ax, m, fit_vals, offset=0):
    # pull what we want out of the xarray
    control = float(m.coords["control"])
    t = m.coords["time"]
    z = m.values

    (ln,) = ax.plot(t, z + offset, label=f"C: {control:.1f}")
    (fit,) = ax.plot(t, fit_vals.sample(t) + offset, color="k")
    ann = ax.annotate(
        (
            f"$C={control:.1f}$\n"
            f"$\\zeta={fit_vals.zeta:.2g}$, $\\omega_0={fit_vals.omega:.2f}$"
        ),
        # units are (axes-fraction, data)
        xy=(0.95, offset + 0.5),
        xycoords=ax.get_yaxis_transform(),
        # set the text alignment
        ha="right",
        va="bottom",
    )
    return {"raw": ln, "fit": fit, "annotation": ann}


# %%


def plot_several(ax, d, fits):
    out = []

    for j, (m, popt) in enumerate(zip(d, fits)):
        arts = plot_one(ax, m, popt, offset=4 * j)
        out.append(arts)

    ax.set_xlabel("time (ms)")
    ax.set_ylabel("displacement (mm)")

    return out


# %%


def subplot_label(ax, text):
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


# %%


def paper_figure_2(fig, layout, d, fits, *, plot_every=5):
    ax_dict = fig.subplot_mosaic(layout)

    fits_df = pd.DataFrame(fits, index=d.coords["control"])

    index = list(range(0, len(d), plot_every))

    artists = {
        "vibrations": plot_several(ax_dict["raw"], d[index], [fits[i] for i in index]),
        "zeta": plot_zeta(ax_dict["zeta"], fits_df),
        "omega": plot_omega(ax_dict["omega"], fits_df),
    }

    fig.align_ylabels(list(ax_dict.values()))

    subplot_labels = {
        k: subplot_label(ax_dict[k], f"({v})")
        for k, v in {"raw": "a", "omega": "b", "zeta": "c"}.items()
    }

    return (fig, ax_dict, artists, subplot_labels)


# %%


single_col_width = 8.6 / 2.54  # single column APS figure
double_col_width = 17.8 / 2.54  # double column APS figure


# %%
fig, axs, arts, labels = paper_figure_2(
    plt.figure(
        constrained_layout=True, figsize=(single_col_width, single_col_width * 2.5)
    ),
    [["raw"], ["omega"], ["zeta"]],
    d,
    fits,
    plot_every=10,
)


# %%
out = Path("../../slides/figs") / Path(__file__).with_suffix(".pdf").name
fig.savefig(out)
