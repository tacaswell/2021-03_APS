# %%
from pathlib import Path
from gen_data import get_data, fit
import matplotlib.pyplot as plt
import pandas as pd

# %%
d = get_data(25)
# fit all of the curves
fits = [fit(m) for m in d]
# put the fit values is a DataFrame
fits_df = pd.DataFrame(fits, index=d.coords["control"])

# %%


fig, ax = plt.subplots()
fits_df.plot(y=["zeta", "omega"], ax=ax)


# %%
out = Path("../../slides/figs") / Path(__file__).with_suffix(".pdf").name
fig.savefig(out)
