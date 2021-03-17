from matplotlib import pyplot as plt
import pandas
pandas.set_option("mode.chained_assignment", None)
from pandas import read_csv
import numpy as np
import sys

data = read_csv(sys.argv[1], low_memory=False)
data = data.rename(columns=lambda x: x.strip())
data.loc[data.index.size-1].iloc[1:] = [0]*(data.columns.size - 1)

start_time = 150e6
stop_time =  300e6

data = data[(data['timestamp'] > start_time)]
data = data[(data['timestamp'] < stop_time)]

time = data["timestamp"]*1e-6

# print data

fig, axes = plt.subplots(4,1, sharex=True)
# plot force
axes[0].plot(time, data["force_0"])
axes[0].set_ylabel("Force (N)")
# plot torque
axes[1].plot(time, data["torque_0"])
axes[1].set_ylabel("Torque (Nm)")
# plot speed
axes[2].plot(time, data["drill_speed_0"])
axes[2].set_ylabel("Shaft speed (RPM)")
# plot pressure
axes[3].plot(time, data["screwjack_speed_0"])
axes[3].set_ylabel("Screwjack speed (cm/min)")
axes[3].set_ylim(-20, 40)
# # plot temperature
# axes[4].plot(data["timestamp"]*1e-6, data["front_temp_0"]/10)
# axes[4].set_ylabel("Front temp (deg C)")
# axes[4].set_xlabel("Time (sec)")


fig, axes = plt.subplots(3,1, sharex=True)
# plot force
axes[0].plot(time, data["hpu_pressure_0"])
axes[0].set_ylabel("HPU Pressure")

axes[1].plot(time, data["drill_pressure_0"])
axes[1].set_ylabel("Drill Pressure")

axes[2].plot(time, data["screwjack_pressure_0"])
axes[2].set_ylabel("Screw Pressure")
plt.show()
