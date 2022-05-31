from matplotlib import pyplot as plt
from scipy.interpolate import interp1d
from numpy import arange, array, linspace
import numpy as np



plt.ion()
fig                 =   plt.figure(figsize=(8, 6), dpi=100)

YTEST  = linspace(100,900,100)

for ytest in YTEST:

    Pi = [300,400]
    Pf = [1200,ytest]

    Np = 4
    ExtraPoints = {}
    for k in range(Np):
        yrnd = np.random.rand()
        xk = Pi[0] + (Pf[0]-Pi[0])*(k+1)/(Np+1)
        yk = Pi[1] + (Pf[1]-Pi[1])*yrnd
        ExtraPoints[k] = [xk,yk]
        

    plt.plot(Pi[0],Pi[1],marker='o',color='C1')
    plt.plot(Pf[0],Pf[1],marker='o',color='C1')
    for key, elem in ExtraPoints.items():
        plt.plot(elem[0],elem[1],marker='o',color='C2')
        plt.plot(elem[0],elem[1],marker='o',color='C2')

    x = linspace(min([Pi[0],Pf[0]]),max([Pi[0],Pf[0]]),100)
    
    xdata = [Pi[0],Pf[0]]
    ydata = [Pi[1],Pf[1]]
    for key,elem in ExtraPoints.items():
        xdata.append(elem[0])
        ydata.append(elem[1])

    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter('ignore', np.RankWarning)
        f = np.poly1d(np.polyfit(xdata,ydata,4))

    frac = np.random.randint(8)
    amp = np.random.randint(150)
    beta = np.random.rand()*10
    y = f(x) + amp*np.sin((x-Pi[0])*frac*np.pi/(Pf[0]-Pi[0]))*np.exp(-beta*(x-Pi[0]))

    plt.plot(x,y)
    plt.xlim([0,1800])
    plt.ylim([0,950])
    plt.gca().invert_yaxis()
    plt.show()

    plt.pause(0.1)
    plt.clf()