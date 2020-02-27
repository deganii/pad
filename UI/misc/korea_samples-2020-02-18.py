import numpy as np
import seaborn as sns
sns.set()
import matplotlib.pyplot as plt

FP = np.asarray([12,2,9,
                -3,8,13,
                2,34,34,
                -10,22,24,
                0,0,-6,
                ]).reshape((5,3))
FP_non_Q = FP

Total_Intensity = np.asarray([87924,90274,90469,
                        126403,94447,77331,
                        90580,71233,96737,
                        154555,121397,61796,
                        104537,109889,50480]).reshape((5,3))
Total_Intensity_non_Q = Total_Intensity

fig, (non_q_fp, non_q_int) = plt.subplots(2, 1, figsize=(7,8))
labels = [' ', '$-$', '$=$', '$\equiv$', '$\sim$']

width = 0.2  # the width of the bars
x = np.arange(len(labels))

bars1 = non_q_fp.bar(x - width, FP_non_Q[:, 0], width, label='1')
bars2 = non_q_fp.bar(x, FP_non_Q[:, 1], width, label='2')
bars3 = non_q_fp.bar(x + width, FP_non_Q[:, 2], width, label='3')

non_q_fp.set_ylabel('Fluorescence Polarization (mP)')
non_q_fp.set_title('Fluorescence Polarization (Q-Samples)')
non_q_fp.set_xticks(x)
non_q_fp.set_xticklabels(labels)
non_q_fp.legend()


## Q Plots
ibars1 = non_q_int.bar(x - width, Total_Intensity_non_Q[:, 0], width, label='1')
ibars2 = non_q_int.bar(x, Total_Intensity_non_Q[:, 1], width, label='2')
ibars3 = non_q_int.bar(x + width, Total_Intensity_non_Q[:, 2], width, label='3')

non_q_int.set_ylabel('Fluorescence (a.u.)')
non_q_int.set_title('Total Intensity (Q-Samples)')
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