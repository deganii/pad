import seaborn as sns
sns.set()
import matplotlib.pyplot as plt
import numpy as np

fields = ['t', 'i_x', 'i_y', 'temp', 'pid_ctrl',
    'ref_x', 'ref_y', 'ref_pa_r0', 'raw_pa_r',
    'pa_delta_r']

# load experiment data
# data shape = [measurement number, fields, samples]

# PROTOCOL
# 1) Put in high viscosity Sample #1
# 2) Back and forth (away from wall / towards wall) on parallel channel (i.x)       Measurement 1,2
# 3) Back and forth on perpendicular (i.y)  Measurement 3,4
# 4) Put in low viscosity Sample #16
# 5) Back and forth on parallel (i.x)       Measurement 5,6
# 6) Back and forth on perpendicular (i.y)  Measurement 7,8

# measurements 0,1 are high viscosity / parallel
# measurements 2,3 are high viscosity / perpendicular
# measurements 4,5 are low viscosity / parallel
# measurements 6,7 are low viscosity / perpendicular

data = np.load(r'C:\dev\pad\Experiments\Alignment-1-16_20200124-172547\data.npz')['data']
fig = plt.figure()
ax = fig.add_subplot(111)
for i in range(data.shape[0]):
    ax.plot(data[i,0,:], data[i,1,:])
    ax.plot(data[i,0,:], data[i,2,:])
ax.set(xlabel='Time (s)', ylabel='PAD Fluorescence (a.u.)')

# high viscosity calc:
hv_par =  np.min((data[0,1,:],data[1,1,:]))
hv_perp = np.max((data[2,2,:],data[3,2,:]))

lv_par =  np.min((data[4,1,:],data[5,1,:]))
lv_perp = np.max((data[6,2,:],data[7,2,:]))

pf = 1
hv_pa = (hv_par - hv_perp) / (hv_par + pf*hv_perp)
lv_pa = (lv_par - lv_perp) / (lv_par + pf*lv_perp)
# kind = 'bar'
plt.show()


# ax.annotate('',
#             xy=(thistheta, thisr),  # theta, radius
#             xytext=(0.05, 0.05),  # fraction, fraction
#             textcoords='figure fraction',
#             horizontalalignment='left',
#             verticalalignment='bottom',
#             )
