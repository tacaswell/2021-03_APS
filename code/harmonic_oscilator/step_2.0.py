# %%
from pathlib import Path
from gen_data import get_data, fit
import matplotlib.pyplot as plt

# %%
d = get_data(25)
m = d[6]
fit_vals = fit(m)

# %%

fig, ax = plt.subplots()
ax.plot(m.time, fit_vals.sample(m.time), label=fit_vals._repr_latex_(), color="k")
ax.set_title(
    r"$A e^{-\zeta\omega_0t} \sin\left(\sqrt{1 - \zeta^2}\omega_0t + \varphi\right)$",
    usetex=True,
)

plt.legend()
ax.set_xlabel("time (ms)")
ax.set_ylabel("displacement (mm)")


# %%
out = Path("../../slides/figs") / Path(__file__).with_suffix(".pdf").name
fig.savefig(out)
