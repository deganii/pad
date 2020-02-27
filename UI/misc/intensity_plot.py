import numpy as np
import seaborn as sns
sns.set()
import matplotlib.pyplot as plt


def plot_intensity(title, data):
    fig, intensity = plt.subplots(figsize=(7,4))
    labels = [' ', '$-$', '$=$', '$\equiv$', '$\sim$']

    width = 0.2  # the width of the bars
    x = np.arange(len(labels))

    ibars1 = intensity.bar(x - width, data[:, 0], width, label='1')
    ibars2 = intensity.bar(x, data[:, 1], width, label='2')
    ibars3 = intensity.bar(x + width, data[:, 2], width, label='3')

    intensity.set_ylabel('Fluorescence (a.u.)')
    intensity.set_title(title)
    intensity.set_xticks(x)
    intensity.set_xticklabels(labels)
    intensity.legend()

    plt.show()



# Total_Intensity = np.asarray([87924,90274,90469,
#                         126403,94447,77331,
#                         90580,71233,96737,
#                         154555,121397,61796,
#                         104537,109889,50480]).reshape((5,3))
#
# plot_intensity('Total Intensity 480/522', Total_Intensity)



Total_Intensity = np.asarray([80155,82947,81521,
116695,85548,71210,
81909,67128,90212,
148043,109328,62272,
97679,106525,49998,
]).reshape((5,3))

plot_intensity('Total Intensity 470/525', Total_Intensity)