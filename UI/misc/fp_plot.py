import numpy as np
import seaborn as sns
sns.set()
import matplotlib.pyplot as plt


def plot_fp(title, data):
    fig, fp = plt.subplots(figsize=(7,4))
    labels = [' ', '$-$', '$=$', '$\equiv$', '$\sim$']

    width = 0.2  # the width of the bars
    x = np.arange(len(labels))

    bars1 = fp.bar(x - width, FP[:, 0], width, label='1')
    bars2 = fp.bar(x, FP[:, 1], width, label='2')
    bars3 = fp.bar(x + width, FP[:, 2], width, label='3')

    fp.set_ylabel('Fluorescence (a.u.)')
    fp.set_title(title)
    fp.set_xticks(x)
    fp.set_xticklabels(labels)
    # fp.set_ylim(-500,-440)
    fp.legend()

    def autolabel(rects, ax, fmt='{}'):
        """Attach a text label above each bar in *rects*, displaying its height."""
        for rect in rects:
            height = rect.get_height()
            ax.annotate(fmt.format(height),
                        xy=(rect.get_x() + rect.get_width() / 2, abs(height)),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom')
    autolabel(bars1, fp)
    autolabel(bars2, fp)
    autolabel(bars3, fp)

    plt.show()


# FP = np.asarray([12,2,9,
#                 -3,8,13,
#                 2,34,34,
#                 -10,22,24,
#                 0,0,-6,
#                 ]).reshape((5,3))
# plot_fp('Fluorescence Polarization (mP)', FP)

# FP = np.asarray([-475,-479,-475,
# -485,-475,-472,
# -479,-458,-454,
# -489,-463,-464,
# -481,-481,-480]).reshape((5,3))
# plot_fp('Fluorescence Polarization (mP) 480/522/G 0.35', FP)

FP = np.asarray([6,7,13,
-8,1,16,
-4,22,18,
-8,12,6,
-10,9,8]).reshape((5,3))
plot_fp('Fluorescence Polarization (mP) 480/522/G 1 - PlateShift', FP)





# FP = np.asarray([-470,-472,-469,
# -478,-469,-465,
# -474,-451,-449,
# -480,-457,-455,
# -476,-474,-473,
# ]).reshape((5,3))
# plot_fp('Fluorescence Polarization (mP) 470/525/G 0.35', FP)


# FP = np.asarray([12,2,9,
# -3,8,13,
# 2,34,34,
# -10,22,24,
# 0,0,-6
# ]).reshape((5,3))
# plot_fp('Fluorescence Polarization (mP) 480/522/G 1', FP)