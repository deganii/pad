import matplotlib

import seaborn as sns
sns.set()
import matplotlib.pyplot as plt


fmri = sns.load_dataset("fmri")
# glycerol = [25,
#             12.5,
#             6.25,
#             3.125,
#             1.5625,
#             0.78125,
#             0.390625,
#             0.1953125,
#             0.09765625]
# avgs = [40.66666667,
#         3.666666667,
#         0,
#         -0.6666666667,
#         0.3333333333,
#         -0.3333333333,
#         -0.6666666667,
#         -2.666666667,
#         -3]
# stds = [18.44812547,
#         5.507570547,
#         2.645751311,
#         0.5773502692,
#         0.5773502692,
#         0.5773502692,
#         0.5773502692,
#         1.154700538,
#         1]
# # ax = sns.lineplot(x=list(range(1,len(avgs)+1)), y=avgs,
# #                 err_style="bars", ci='sd',  yerr=stds, palette='Blues_d')
# ax = sns.barplot(x=["{0:.2f}".format(g) for g in glycerol], y=avgs,  capsize=.2,
#   yerr=stds, palette='Blues_d', order=["{0:.2f}".format(g) for g in glycerol])

glycerol = [75,
            70,
            65,
            60,
            55,
            50,
            45,
            40,
            35,
            30,
            25,
            20,
            15,
            10,
            5,
            0
            ]
avgs = [188.5,
            176,
            151,
            134,
            110,
            89.5,
            67,
            60,
            41.5,
            34.5,
            21,
            14.5,
            7.5,
            1,
            -2,
            -3]
stds = [2.121320344,
5.656854249,
4.242640687,
1.414213562,
2.828427125,
2.121320344,
1.414213562,
4.242640687,
2.121320344,
0.707106781,
4.242640687,
2.121320344,
2.121320344,
1.414213562,
1.414213562,
1.414213562
]
ax = sns.barplot(x=["{0}".format(g) for g in glycerol], y=avgs,  capsize=.2,
  yerr=stds, palette='Blues_d', order=["{0}".format(g) for g in glycerol])


plt.show()