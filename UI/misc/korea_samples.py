import numpy as np
import seaborn as sns
sns.set()
import matplotlib.pyplot as plt

FP = np.asarray([-3, 23, 21, 9, 59, 74,
                 26, 34, 54, -11, 37, 158,
                 23, 69, 33, 29, 33, 132,
                 24, 68, 36, 83, 35, 6,
                -20, 71, 103, 48, 10, 58]
                ).reshape((5,6))
FP_Q = FP[:,3:]
FP_non_Q = FP[:,:3]

Perp = np.asarray([49004, 35059, 13617, 20291, 4548, 4494,
        13816, 18381, 8567, 5039, 5033, 3881,
        22339, 12204, 36745, 4422, 3797, 1951,
        27254, 9710, 14120, 4145, 8628, 3186,
        49814, 12573, 7164, 8565, 16537, 1880]
                ).reshape((5,6))
Perp_Q = Perp[:,3:]
Perp_non_Q = Perp[:,:3]


Parallel = np.asarray([48681, 36710, 14202, 20662, 5122, 5214,
            14565, 19666, 9539, 4934, 5423, 5340,
            23395, 14018, 39258, 4690, 4058, 2543,
            28605, 11117, 15185, 4896, 9249, 3224,
            47846, 14502, 8818, 9434, 16862, 2112]
                ).reshape((5,6))
Parallel_Q = Parallel[:,3:]
Parallel_non_Q = Parallel[:,:3]


Aniso = np.asarray([-2, 15, 14, 6, 40, 51,
         18, 23, 36, -7, 25, 111,
         16, 47, 22, 20, 22, 92,
         16, 46, 25, 57, 23, 4,
         -13, 49, 71, 33, 7, 40]
                ).reshape((5,6))
Aniso_Q = Aniso[:,3:]
Aniso_non_Q = Aniso[:,:3]


Total_Intensity = np.asarray([47778, 35255, 13259, 19661, 4809, 4868,
             6602, 19070, 9069, 4219, 4951, 4795,
             22824, 13462, 37046, 4229, 3905, 2260,
             27610, 10389, 13933, 3970, 9521, 3197,
             46437, 13496, 7848, 9929, 16445, 2005]
                ).reshape((5,6))

Total_Intensity_Q = Total_Intensity[:,3:]
Total_Intensity_non_Q = Total_Intensity[:,:3]


fig, ((q_fp, q_int), (non_q_fp, non_q_int )) = plt.subplots(2, 2)
labels = [' ', '$-$', '$=$', '$\equiv$', '$\sim$']

width = 0.2  # the width of the bars
x = np.arange(len(labels))

## Q Plots
qbars1 = q_fp.bar(x - width, FP_Q[:, 0], width, label='Q1')
qbars2 = q_fp.bar(x, FP_Q[:, 1], width, label='Q2')
qbars3 = q_fp.bar(x + width, FP_Q[:, 2], width, label='Q3')

q_fp.set_ylabel('Fluorescence Polarization (mP)')
q_fp.set_title('Fluorescence Polarization (Q-Samples)')
q_fp.set_xticks(x)
q_fp.set_xticklabels(labels)
q_fp.legend()


## non-Q Plots
bars1 = non_q_fp.bar(x - width, FP_non_Q[:, 0], width, label='1')
bars2 = non_q_fp.bar(x, FP_non_Q[:, 1], width, label='2')
bars3 = non_q_fp.bar(x + width, FP_non_Q[:, 2], width, label='3')

non_q_fp.set_ylabel('Fluorescence Polarization (mP)')
non_q_fp.set_title('Fluorescence Polarization (non Q-Samples)')
non_q_fp.set_xticks(x)
non_q_fp.set_xticklabels(labels)
non_q_fp.legend()

## Q Plots
qibars1 = q_int.bar(x - width, Total_Intensity_Q[:, 0], width, label='Q1')
qibars2 = q_int.bar(x, Total_Intensity_Q[:, 1], width, label='Q2')
qibars3 = q_int.bar(x + width, Total_Intensity_Q[:, 2], width, label='Q3')

q_int.set_ylabel('Fluorescence (a.u.)')
q_int.set_title('Total Intensity (Q-Samples)')
q_int.set_xticks(x)
q_int.set_xticklabels(labels)
q_int.legend()

## non-Q Plots
ibars1 = non_q_int.bar(x - width, Total_Intensity_non_Q[:, 0], width, label='1')
ibars2 = non_q_int.bar(x, Total_Intensity_non_Q[:, 1], width, label='2')
ibars3 = non_q_int.bar(x + width, Total_Intensity_non_Q[:, 2], width, label='3')

non_q_int.set_ylabel('Fluorescence (a.u.)')
non_q_int.set_title('Total Intensity (non Q-Samples)')
non_q_int.set_xticks(x)
non_q_int.set_xticklabels(labels)
non_q_int.legend()

def autolabel(rects, ax, fmt='{}'):
    """Attach a text label above each bar in *rects*, displaying its height."""
    for rect in rects:
        height = rect.get_height()
        ax.annotate(fmt.format(height),
                    xy=(rect.get_x() + rect.get_width() / 2, abs(height)),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom')

autolabel(qbars1, q_fp)
autolabel(qbars2, q_fp)
autolabel(qbars3, q_fp)

autolabel(bars1, non_q_fp)
autolabel(bars2, non_q_fp)
autolabel(bars3, non_q_fp)

# autolabel(ibars1, non_q_int)
# autolabel(ibars2, non_q_int)
# autolabel(ibars3, non_q_int)
#
# autolabel(qibars1, q_int)
# autolabel(qibars2, q_int)
# autolabel(qibars3, q_int)

plt.show()


# Non-Q Plot