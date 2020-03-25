import random
import matplotlib.pyplot as plot
import time

colors = ["red", "blue", "cyan", "magenta", "green", "yellow"]
sets = ["english", "french"]


# HERE STARTS LINEAR REGRESSION WITH GRADIENT DESCENT #


def batchgradientdescent(data, k, m, L):
    d_k, d_m = calculategradient(data, k, m)
    return k - L * d_k, m - L * d_m


def stochasticgradientdescent(data, k, m, L):
    d_k, d_m = calculategradient([random.choice(data)], k, m)
    return k - L * d_k, m - L * d_m


def calculategradient(data, k, m):
    size = len(data)
    d_k = -2 / size * sum([(data[i][1] - k * data[i][0] - m) * data[i][0] for i in range(len(data))])
    d_m = -2 / size * sum([(data[i][1] - k * data[i][0] - m) for i in range(len(data))])
    return d_k, d_m


def parsegd(file):
    file = open(file, "r")
    return [(int(pair.split("\t")[0]), int(pair.split("\t")[1])) for pair in file.readlines()]


def getmax(datasets):
    x, y = 0, 0
    for data in datasets:
        for val in data:
            x = val[0] if val[0] > x else x
            y = val[1] if val[1] > y else y
    return x, y


def getplotvalues(data):
    x, y = [], []
    for value in data:
        x.append(value[0])
        y.append(value[1])
    return x, y


def gd(datasets, learning=0.25):
    maxx, maxy = getmax(datasets)
    for i in range(len(datasets)):
        datasets[i] = [(point[0] / maxx, point[1] / maxy) for point in datasets[i]]
        x, y = getplotvalues(datasets[i])
        color = random.choice(colors)
        colors.remove(color)
        plot.scatter(x, y, c=color)
        k_s, m_s, k_b, m_b = 0, 0, 0, 0
        for _ in range(500):
            k_s, m_s = stochasticgradientdescent(datasets[i], k_s, m_s, learning)
            k_b, m_b = batchgradientdescent(datasets[i], k_b, m_b, learning)
        plot.plot([0, 1], [m_s, k_s + m_s], c=color, linestyle='--', label="Stochastic Gradient Descent for " + sets[i])
        plot.plot([0, 1], [m_s, k_b + m_b], c=color, linestyle=':', label="Batch Gradient Descent for " + sets[i])
    plot.legend()
    plot.show()


if __name__ == '__main__':
    start_time = time.time()
    gd([parsegd("english.txt"), parsegd("french.txt")])
    print("--- %s seconds ---" % (time.time() - start_time))
