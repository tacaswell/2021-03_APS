#!/usr/bin/env python
# coding: utf-8

# In[1]:


# interactive figures, requires ipypml!
get_ipython().run_line_magic('matplotlib', 'widget')
import matplotlib.pyplot as plt


# In[2]:


import numpy as np
import pandas as pd
from gen_data import get_data, fit


# In[3]:


d = get_data(25)
d


# In[5]:


fig, ax = plt.subplots()
ax.plot(d.T)


# In[6]:


m = d[6]
m


# In[9]:


fig, ax = plt.subplots()
# ax.plot(m)
# ax.plot(m.time, m)
m.plot(ax=ax)


# In[10]:


fig, ax = plt.subplots()
control = float(m.control)
t = m.time
z = m.values
(ln,) = ax.plot(t, z, label=f"C: {control:.1f}")
ax.legend()
ax.set_xlabel("time (ms)")
ax.set_ylabel("displacement (mm)")


# In[11]:


def plot_one(ax, m):
    # pull what we want out of the xarray
    control = float(m.control)
    t = m.time
    z = m.values

    (ln,) = ax.plot(t, z, label=f"C: {control:.1f}")

    return {"raw": ln}


fig, ax = plt.subplots()
plot_one(ax, d[0])
plot_one(ax, d[5])
plot_one(ax, d[-1])
ax.legend()
ax.set_xlabel("time (ms)")
ax.set_ylabel("displacement (mm)")


# In[12]:


def plot_one(ax, m, offset=0):
    # pull what we want out of the xarray
    control = float(m.coords["control"])
    t = m.time
    z = m.values

    (ln,) = ax.plot(t, z + offset, label=f"C: {control:.1f}")

    return {"raw": ln}


fig, ax = plt.subplots()
plot_one(ax, d[0])
plot_one(ax, d[10], offset=4)
plot_one(ax, d[20], offset=8)
ax.legend()
ax.set_xlabel("time (ms)")
ax.set_ylabel("displacement (mm)")


# In[13]:


from gen_data import fit


# In[14]:


fit_vals = fit(d[6])
print(repr(fit_vals))
print(fit_vals)
print(fit_vals._repr_latex_())
fit_vals


# In[15]:


fig, ax = plt.subplots()
ax.plot(m.time, fit_vals.sample(m.time), label=fit_vals._repr_latex_(), color='k')
plt.gca().set_title(
     r"$A e^{-\zeta\omega_0t} \sin\left(\sqrt{1 - \zeta^2}\omega_0t + \varphi\right)$",
     usetex=True,
)

plt.legend()
ax.set_xlabel("time (ms)")
ax.set_ylabel("displacement (mm)")


# In[16]:


def plot_one(ax, m, popt, offset=0):
    # pull what we want out of the xarray
    control = float(m.coords["control"])
    t = m.coords["time"]
    z = m.values

    (ln,) = ax.plot(t, z + offset, label=f"C: {control:.1f}")
    (fit,) = ax.plot(t, popt.sample(t) + offset, color="k")
    ann = ax.annotate(
        f"$\\zeta={popt.zeta:.2g}$, $\\omega_0={popt.omega:.2f}$",
        # units are (axes-fraction, data)
        xy=(0.95, offset + 0.5),
        xycoords=ax.get_yaxis_transform(),
        # set the text alignment
        ha="right",
        va="bottom",
    )
    return {"raw": ln, "fit": fit, "annotation": ann}


# In[17]:


fig, ax = plt.subplots()
plot_one(ax, d[0], fit(d[0]))
plot_one(ax, d[10], fit(d[10]), offset=4)
plot_one(ax, d[20], fit(d[20]), offset=8)
plot_one(ax, d[24], fit(d[24]), offset=12)
ax.legend(ncol=3, loc="upper center")
ax.set_xlabel("time (ms)")
ax.set_ylabel("displacement (mm)")
plt.show()


# In[18]:


def plot_several(ax, d, fits):
    out = []

    for j, (m, popt) in enumerate(zip(d, fits)):
        arts = plot_one(ax, m, popt, offset=3.75 * j)
        out.append(arts)

    ax.set_xlabel("time (ms)")
    ax.set_ylabel("displacement (mm)")

    return out


# In[20]:


fig, ax = plt.subplots()
indx = [0, 5, 10]
plot_several(ax, d[indx], [fit(d[i]) for i in indx])
ax.legend(ncol=3, loc="upper center")


# In[21]:


fits = [fit(m) for m in d]                               # fit all of the curves
fits_df = pd.DataFrame(fits, index=d.coords["control"])  # put the fit values is a DataFrame


# In[22]:


fig, ax = plt.subplots()
fits_df.plot(y=['zeta', 'omega'], ax=ax)


# In[23]:


def plot_zeta(ax, fits_df):
    ax.set_ylabel(r"$\zeta$")
    ax.set_xlabel("control (arb)")
    ax.set_ylim(0, 0.08)
    return ax.plot(
        fits_df["zeta"], marker="o", color="k", label="\N{greek small letter zeta}", linestyle=''
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


# In[24]:


fig, (ax1, ax2) = plt.subplots(1, 2, constrained_layout=True)
plot_zeta(ax1, fits_df)
plot_omega(ax2, fits_df)
ax1.legend()
ax2.legend()


# In[25]:


def plot_one(ax, m, popt, offset=0):
    # pull what we want out of the xarray
    control = float(m.coords["control"])
    t = m.coords["time"]
    z = m.values

    (ln,) = ax.plot(t, z + offset, label=f"C: {control:.1f}")
    (fit,) = ax.plot(t, popt.sample(t) + offset, color="k")
    ann = ax.annotate(
        f"$C={control:.1f}$\n$\\zeta={popt.zeta:.2g}$ $\\omega_0={popt.omega:.2f}$",
        # units are (axes-fraction, data)
        xy=(0.95, offset + 0.5),
        xycoords=ax.get_yaxis_transform(),
        # set the text alignment
        ha="right",
        va="bottom",
    )
    return {"raw": ln, "fit": fit, "annotation": ann}

def plot_several(ax, d, fits):
    out = []

    for j, (m, popt) in enumerate(zip(d, fits)):
        arts = plot_one(ax, m, popt, offset=3.75 * j)
        out.append(arts)

    ax.set_xlabel("time (ms)")
    ax.set_ylabel("displacement (mm)")

    return out


# In[26]:


fig, ax = plt.subplots()
indx = [0, 10, 24]
plot_several(ax, d[indx], [fits[i] for i in indx])


# In[27]:


fig, (ax1, ax2, ax3) = plt.subplots(1, 3, constrained_layout=True)
indx = [0, 10, 24]
plot_several(ax1, d[indx], [fits[i] for i in indx])
plot_zeta(ax2, fits_df)
plot_omega(ax3, fits_df)


# In[28]:


fig, ax_dict = plt.subplot_mosaic("""
AB
AC
""", constrained_layout=True)
indx = [0, 10, 24]
plot_several(ax_dict['A'], d[indx], [fits[i] for i in indx])
plot_zeta(ax_dict['B'], fits_df)
plot_omega(ax_dict['C'], fits_df)
fig.align_ylabels(list(ax_dict.values()))


# In[29]:


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


# In[30]:


fig, ax_dict = plt.subplot_mosaic("""
AB
AC
""", constrained_layout=True)
indx = [0, 10, 24]
plot_several(ax_dict['A'], d[indx], [fits[i] for i in indx])
plot_zeta(ax_dict['B'], fits_df)
plot_omega(ax_dict['C'], fits_df)
fig.align_ylabels(list(ax_dict.values()))
subplot_labels = {
    k: subplot_label(v, f"({k.lower()})") for k, v in ax_dict.items()
}


# In[31]:


def paper_figure_2(fig, layout, d, fits, *, plot_every=5):
    ax_dict = fig.subplot_mosaic(layout)

    fits_df = pd.DataFrame(fits, index=d.coords["control"])

    index = list(range(0, len(d), plot_every))

    artists = {
        "vibrations": plot_several(ax_dict["A"], d[index], [fits[i] for i in index]),
        "zeta": plot_zeta(ax_dict["B"], fits_df),
        "omega": plot_omega(ax_dict["C"], fits_df),
    }

    fig.align_ylabels(list(ax_dict.values()))
    subplot_labels = {
        k: subplot_label(v, f"({k.lower()})") for k, v in ax_dict.items()
    }

    return (fig, ax_dict, artists, subplot_labels)


# In[32]:


single_col_width = 8.6 / 2.54  # single column APS figure
double_col_width = 17.8 / 2.54  # double column APS figure


# In[33]:


fig, axs, arts, labels = paper_figure_2(
    plt.figure(
        constrained_layout=True, figsize=(double_col_width, double_col_width * 0.5)
    ),
    "AB\nAC",
    d,
    fits,
    plot_every=5,
)


# In[34]:


paper_figure_2(
    plt.figure(
        constrained_layout=True, figsize=(single_col_width, single_col_width * 2.5)
    ),
    "A\nB\nC",
    d,
    fits,
    plot_every=10,
)


# In[ ]:
