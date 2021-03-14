# %%
from pathlib import Path
from gen_data import get_data
import matplotlib.pyplot as plt

# %%
d = get_data(25)

# %%
fig, ax = plt.subplots()
m = d[6]
ax.plot(m)

# %%
out = Path("../../slides/figs") / Path(__file__).with_suffix(".pdf").name
fig.savefig(out)
