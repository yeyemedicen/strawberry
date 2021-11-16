from matplotlib import pyplot as plt
from scipy.interpolate import interp1d
from numpy import arange, array, linspace



plt.ion()
fig                 =   plt.figure(figsize=(8, 6), dpi=100)

YTEST  = linspace(301,800,100)

for ytest in YTEST:

    P1 = [500,400]
    P2 = [600,300]

    alpha = [0.15,0.65]
    beta = [0.5,-0.1]

    if P2[1]>P1[1]:
        beta = [-0.2,-0.1]

    if P2[0]<P1[0]:
        if P2[1]>P1[1]:
            beta = [-0.1,-0.85]
        else:
            beta = [-0.1,0.1]


    x3 = min([P1[0],P2[0]]) + alpha[0]*(abs(P1[0] - P2[0]))
    x4 = min([P1[0],P2[0]]) + alpha[1]*(abs(P1[0] - P2[0]))
    y3 = min([P1[1],P2[1]]) + beta[0]*(abs(P1[1] - P2[1]))
    y4 = min([P1[1],P2[1]]) + beta[1]*(abs(P1[1] - P2[1]))

    P3 = [x3,y3]
    P4 = [x4,y4]


    plt.plot(P1[0],P1[1],marker='o',color='C1')
    plt.plot(P2[0],P2[1],marker='o',color='C1')
    plt.plot(P3[0],P3[1],marker='o',color='red')
    plt.plot(P4[0],P4[1],marker='o',color='lime')

    x = linspace(min([P1[0],P2[0]]),max([P1[0],P2[0]]),100)
    xdata = [P1[0],P4[0],P3[0],P2[0]]
    ydata = [P1[1],P4[1],P3[1],P2[1]]
    f = interp1d(xdata,ydata,kind='cubic')

    plt.plot(x,f(x))
    plt.xlim([0,1000])
    plt.ylim([0,900])
    plt.gca().invert_yaxis()
    plt.show()

    plt.pause(0.01)
    plt.clf()