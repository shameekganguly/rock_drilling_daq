from matplotlib import pyplot as plt
import pandas
pandas.set_option("mode.chained_assignment", None)
from pandas import read_csv
import numpy as np

data = read_csv("datalog.csv", low_memory=False)
data = data.rename(columns=lambda x: x.strip())
data.loc[data.index.size-1].iloc[1:] = [0]*(data.columns.size - 1)

# print data

fig, axes = plt.subplots(4,1, sharex=True)
# plot force
axes[0].plot(data["timestamp"]*1e-6, data["force_0"]*7.0/5.0)
axes[0].set_ylabel("Force (N)")
# plot torque
axes[1].plot(data["timestamp"]*1e-6, data["torque_0"]/30)
axes[1].set_ylabel("Torque (Nm)")
# plot speed
speed = np.diff(data["speed_0"], prepend=0)
axes[2].plot(data["timestamp"]*1e-6, speed)
axes[2].set_ylabel("Shaft speed (RPM)")
# plot pressure
axes[3].plot(data["timestamp"]*1e-6, data["pressure_0"]*0.0063125)
axes[3].set_ylabel("Pressure (bar)")
axes[3].set_xlabel("Time (sec)")
plt.show()