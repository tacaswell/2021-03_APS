import sys

import pandas as pd
import matplotlib.pyplot as plt

from gen_data import get_data, fit


d = get_data(25)


fits = [fit(m) for m in d]
fits_df = pd.DataFrame(fits, index=d.coords["control"])

fits_df.plot()

fig, (ax1, ax2) = plt.subplots(2)

ax1.set_ylabel(r"$\zeta$")
ax1.set_xlabel("control (arb)")
ax1.set_ylim(0, 0.08)
ax1.plot(fits_df["zeta"], marker="o", color="k", label="\N{greek small letter zeta}")
ax1.legend()

ax2.set_ylabel(r"$\omega_0/2\pi$ (kHz)")
ax2.set_xlabel("control (arb)")
ax2.set_ylim(0.25, 1.25)
ax2.plot(
    fits_df["omega"] / (2 * np.pi),
    marker="o",
    color="k",
    label="\N{greek small letter omega}",
)
ax2.legend()


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


fig, (ax1, ax2) = plt.subplots(1, 2)
_plot_omega(ax1, fits_df)
_plot_zeta(ax2, fits_df)


fig, ax_dict = plt.subplot_mosaic(
    """
AB
AC
""",
    constrained_layout=True,
)

_plot_omega(ax_dict["B"], fits_df)
_plot_zeta(ax_dict["C"], fits_df)
