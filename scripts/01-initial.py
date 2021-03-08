
from gen_data import get_data

import matplotlib.pyplot as plt

d = get_data(25)

print(d)

fig, ax = plt.subplots()

for m in d:
    ax.plot(m)

plt.show()
