# %%
from pathlib import Path
from gen_data import get_data, fit
import matplotlib.pyplot as plt

# %%
d = get_data(25)
m = d[6]
fit_vals = fit(m)

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
            f"$\\zeta={fit_vals.zeta:.2g}$ $\\omega_0={fit_vals.omega:.2f}$"
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

fig, ax = plt.subplots()
indx = [0, 5, 24]
plot_several(ax, d[indx], [fit(d[i]) for i in indx])

# %%
out = Path("../../slides/figs") / Path(__file__).with_suffix(".pdf").name
fig.savefig(out)
