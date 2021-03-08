import sys


import matplotlib.pyplot as plt

from gen_data import get_data, fit


d = get_data(25)

m = d[0]

print(d)

fig, ax = plt.subplots()

control = float(m.coords["control"])
t = m.coords["time"]
z = m.values
(ln,) = ax.plot(t, z, label=f"C: {control:.1f}")
ax.legend()
plt.show()


def plot_one(ax, m):
    # pull what we want out of the xarray
    control = float(m.coords["control"])
    t = m.coords["time"]
    z = m.values

    (ln,) = ax.plot(t, z, label=f"C: {control:.1f}")

    return {"raw": ln}


fig, ax = plt.subplots()
plot_one(ax, d[0])
plot_one(ax, d[-1])
ax.legend()

plt.show()


def plot_one(ax, m, offset=0):
    # pull what we want out of the xarray
    control = float(m.coords["control"])
    t = m.coords["time"]
    z = m.values

    (ln,) = ax.plot(t, z + offset, label=f"C: {control:.1f}")

    return {"raw": ln}


fig, ax = plt.subplots()
plot_one(ax, d[0])
plot_one(ax, d[10], offset=4)
plot_one(ax, d[20], offset=8)
ax.legend()

plt.show()


popt = fit(d[0])
print(repr(popt))
print(popt)
print(popt._repr_latex_())

# plt.plot(x, curve(x, *popt), label=popt._repr_latex_())
# plt.gca().set_title(
#     r"$A e^{-\zeta\omega_0t} \sin\left(\sqrt{1 - \zeta^2}\omega_0t + \varphi\right)$",
#     usetex=True,
# )
#
# plt.legend(usetex=True)
#


fig, ax = plt.subplots()
plot_one(ax, d[0], fit(d[0]))
plot_one(ax, d[10], fit(d[10]), offset=4)
plot_one(ax, d[20], fit(d[20]), offset=8)
ax.legend(ncol=3, loc="upper center")

plt.show()


def plot_several(ax, d):
    out = []

    for j, m in enumerate(d):
        popt = fit(m)
        arts = plot_one(ax, m, popt, offset=3.75 * j)
        out.append(arts)

    ax.set_xlabel("time (ms)")
    ax.set_ylabel("displacement (mm)")

    return out


fig, ax = plt.subplots()

plot_several(ax, d[[0, 10, 20, 24]])
