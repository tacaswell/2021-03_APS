# %%
from pathlib import Path
from gen_data import get_data
import matplotlib.pyplot as plt

# %%
d = get_data(25)


# %%
def plot_one(ax, m, offset=0):
    control = float(m.control)
    (ln,) = ax.plot(m.time, m + offset, label=f"C: {control:.1f}")
    return {"raw": ln}


# %%
fig, ax = plt.subplots()
plot_one(ax, d[0])
plot_one(ax, d[5], offset=4)
plot_one(ax, d[-1], offset=8)
ax.legend()
ax.set_xlabel("time (ms)")
ax.set_ylabel("displacement (mm)")

# %%
out = Path("../../slides/figs") / Path(__file__).with_suffix(".pdf").name
fig.savefig(out)
