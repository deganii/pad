import matplotlib

import seaborn as sns
sns.set()
import matplotlib.pyplot as plt

glycerol_linear = list(range(75,-1,-5))
glycerol_serial = [25.0 * 0.5**i for i in range(9)]

avgs_serial = [40.66666667,3.666666667, 0, -0.6666666667, 0.3333333333,
  -0.3333333333, -0.6666666667, -2.666666667, -3]
stds_serial = [18.44812547, 5.507570547, 2.645751311, 0.5773502692, 0.5773502692,
        0.5773502692, 0.5773502692, 1.154700538, 1]
# # ax = sns.lineplot(x=list(range(1,len(avgs_serial)+1)), y=avgs_serial,
# #                 err_style="bars", ci='sd',  yerr=stds_serial, palette='Blues_d')
# ax = sns.barplot(x=["{0:.2f}".format(g) for g in glycerol_serial], y=avgs_serial,  capsize=.2,
#   yerr=stds_serial, palette='Blues_d', order=["{0:.2f}".format(g) for g in glycerol_serial])
#
avgs_linear = [188.5, 176, 151, 134, 110, 89.5, 67, 60, 41.5, 34.5, 21, 14.5, 7.5, 1, -2, -3]
stds_linear = [2.121320344, 5.656854249, 4.242640687, 1.414213562, 2.828427125,
        2.121320344, 1.414213562, 4.242640687, 2.121320344, 0.707106781,
        4.242640687, 2.121320344, 2.121320344, 1.414213562, 1.414213562, 1.414213562 ]

# ax = sns.barplot(x=["{0}".format(g) for g in glycerol_linear], y=avgs_linear,  capsize=.2,
#   yerr=stds_linear, palette='Blues_d', order=["{0}".format(g) for g in glycerol_linear])
#
import numpy as np
raw_par_linear_1 = np.asarray([51501, 49285, 47178, 48833, 44359, 46980, 41010,
                    44704, 41725, 41782, 41000, 40637, 40450, 41231, 41292, 40216])
raw_par_linear_2 = np.asarray([50428, 42184, 52688, 49244, 43555, 44414, 43209, 42529,
                    42865, 41123, 40507, 39712, 40530, 40891, 40367, 41052])
raw_par_linear_avg = np.mean(np.vstack((raw_par_linear_1, raw_par_linear_2)), axis=0)
raw_par_linear_std = np.std(np.vstack((raw_par_linear_1, raw_par_linear_2)), axis=0)
raw_perp_linear_1 = [30480, 30402, 31005, 33437, 32220, 36436, 33846, 37211,
                     37039, 37724, 38199, 38714, 39710, 41040, 41445, 40755]
raw_perp_linear_2 = [29637, 25464, 34039, 33545, 31945, 34201, 35492, 36014,
                     37822, 37177, 38448, 38176, 39490, 40869, 40680, 41285]
raw_perp_linear_avg = np.mean(np.vstack((raw_perp_linear_1, raw_perp_linear_2)), axis=0)
raw_perp_linear_std = np.std(np.vstack((raw_perp_linear_1, raw_perp_linear_2)), axis=0)

# ax = sns.barplot(x=["{0}".format(g) for g in glycerol_linear], y=raw_par_linear_avg,
#                  capsize=.2, yerr=raw_par_linear_std, palette='Blues_d',
#                  order=["{0}".format(g) for g in glycerol_linear])
# ax.set_title('Raw Parallel ($I_x$) Signal')
# ax.set_ylabel("Fluorescence Anisotropy (a.u.)")
# ax.set_xlabel("Glycerol Concentration (%)")
# plt.savefig(r'C:\dev\pad\data\raw_par_linear_avg.png')

# ax = sns.barplot(x=["{0}".format(g) for g in glycerol_linear], y=raw_perp_linear_avg,
#                  capsize=.2, yerr=raw_perp_linear_std, palette='Blues_d',
#                  order=["{0}".format(g) for g in glycerol_linear])
# ax.set_title('Raw Perpendicular ($I_x$) Signal')
# ax.set_ylabel("Fluorescence Anisotropy (a.u.)")
# ax.set_xlabel("Glycerol Concentration (%)")
# plt.savefig(r'C:\dev\pad\data\raw_perp_linear_avg.png')


# load experiment data
# exp_root = r'C:\dev\pad\Experiments\Glycerol_20200115-180314'
exp_root = r'C:\dev\pad\Experiments\Glycerol_Repeat_Align_20200127-170324'

msmts =[]
import re
import glob
import csv
import os
p = re.compile(r'measurement\_(\d+)\.csv')
files = glob.glob(exp_root + '/measurement_*.csv')
msmts_ix = np.empty(shape=[16,100])
msmts_iy = np.empty(shape=[16,100])
for i, file in enumerate(files):
    name = os.path.basename(file)
    msmt_num = int(re.match(p, name)[1]) - 1
    with open(file, 'r') as csvfile:
        msmtreader = csv.reader(csvfile, delimiter=',')
        next(msmtreader)
        for j, row in enumerate(msmtreader):
            msmts_ix[msmt_num,j] = float(row[1])
            msmts_iy[msmt_num, j] = float(row[2])

fig, ((pl_par, pa_par, sc_par), (pl_perp, pa_perp, sc_perp)) = plt.subplots(2, 3)

# remove outliers from data due to LED being off
msmts_ix[4,0] = msmts_ix[13,0] = np.nan
msmts_iy[4,0] = msmts_iy[13,0] = np.nan

plate_parallel = raw_par_linear_1
plate_parallel_err = raw_par_linear_std
pad_parallel = np.nanmean(msmts_ix, axis=1)
pad_parallel_err = np.nanstd(msmts_ix, axis=1)

plate_perp = raw_perp_linear_1
plate_perp_err = raw_perp_linear_std
pad_perp = np.nanmean(msmts_iy, axis=1)
pad_perp_err = np.nanstd(msmts_iy, axis=1)





# average the i_x and compare to
# raw_par_linear_avg
# plt.scatter(plate_parallel,pad_parallel)


sns.barplot(glycerol_linear, plate_parallel, ax=pl_par,
             order=glycerol_linear, palette='Blues_d')
sns.barplot(glycerol_linear, pad_parallel, ax=pa_par,
            yerr=pad_parallel_err, order=glycerol_linear, palette='Greens_d')
pl_par.set(xlabel='Glycerol (%)', ylabel='Plate Reader Fluorescence (a.u.)', ylim=(37000,53000))
pa_par.set(xlabel='Glycerol (%)', ylabel='PAD Fluorescence (a.u.)', ylim=(160,240))
cmap = sns.cubehelix_palette(dark=.3, light=.8, as_cmap=True) #'BuGn_r'
sns.scatterplot(plate_parallel,pad_parallel, palette=cmap , ax=sc_par,  hue=glycerol_linear)
sc_par.set(xlabel='Plate Reader Fluorescence (a.u.)', ylabel='PAD Fluorescence (a.u.)')


sns.barplot(glycerol_linear, plate_perp, ax=pl_perp,
             order=glycerol_linear, palette='Blues_d')
sns.barplot(glycerol_linear, pad_perp, ax=pa_perp,
            yerr=pad_perp_err, order=glycerol_linear, palette='Greens_d')
pl_perp.set(xlabel='Glycerol (%)', ylabel='Plate Reader Fluorescence (a.u.)', ylim=(25000,45000))
pa_perp.set(xlabel='Glycerol (%)', ylabel='PAD Fluorescence (a.u.)', ylim=(300,425))
cmap = sns.cubehelix_palette(dark=.3, light=.8, as_cmap=True) #'BuGn_r'
sns.scatterplot(plate_perp,pad_perp, palette=cmap , ax=sc_perp,  hue=glycerol_linear)
sc_perp.set(xlabel='Plate Reader Fluorescence (a.u.)', ylabel='PAD Fluorescence (a.u.)')


plt.show()