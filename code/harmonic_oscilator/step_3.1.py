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
fig, (ax1, ax2) = plt.subplots(2, 1, constrained_layout=True)
plot_zeta(ax1, fits_df)
plot_omega(ax2, fits_df)


# %%
out = Path("../../slides/figs") / Path(__file__).with_suffix(".pdf").name
fig.savefig(out)
