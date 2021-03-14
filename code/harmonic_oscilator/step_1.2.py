# %%
from pathlib import Path
from gen_data import get_data
import matplotlib.pyplot as plt

# %%
d = get_data(25)
m = d[6]

# %%
fig, ax = plt.subplots()

ax.plot(m.time, m, label=f"C: {float(m.control):.1f}")
ax.legend()
ax.set_xlabel("time (ms)")
ax.set_ylabel("displacement (mm)")

# %%
out = Path('../../slides/figs') / Path(__file__).with_suffix('.pdf').name
fig.savefig(out)
