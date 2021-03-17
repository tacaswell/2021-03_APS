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
fig, ax_dict = plt.subplot_mosaic(
    [["raw", "omega"], ["raw", "zeta"]], constrained_layout=True
)
indx = [0, 10, 24]
plot_several(ax_dict["raw"], d[indx], [fits[i] for i in indx])
plot_zeta(ax_dict["zeta"], fits_df)
plot_omega(ax_dict["omega"], fits_df)
fig.align_ylabels(list(ax_dict.values()))


# %%
out = Path("../../slides/figs") / Path(__file__).with_suffix(".pdf").name
fig.savefig(out)
