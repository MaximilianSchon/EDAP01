import random
import math
from copy import deepcopy
import time

colors = ["red", "blue", "cyan", "magenta", "green", "yellow"]
sets = ["english", "french"]

# HERE STARTS THE PERCPETRON #


def parsesvm(file, amtAttr=3):
    datasets = []
    for i in range(len(sets)):
        datasets.append([])
    file = open(file, 'r')
    for line in file.readlines():
        line = line.split(" ")
        setindex = int(line[0])
        entry = [0] * amtAttr
        for attr in line[1:]:
            index, value = attr.split(":")
            entry[int(index) - 1] += int(value)
        datasets[setindex].append(entry)
    maxx, maxy = getmax(datasets)
    for i in range(len(datasets)):
        datasets[i] = [(1, point[0] / maxx, point[1] / maxy) for point in datasets[i]]
    return datasets


def classifysetperceptron(w, datasets):
    for dataset in range(len(datasets)):
        for values in datasets[dataset]:
            if dataset != classifyperceptron(w, values):
                return False
    return True


def classifyperceptron(w, values):
    dot = sum([w[value] * values[value] for value in range(len(values))])
    if dot > 0:
        return 1
    elif dot < 0:
        return 0


def perceptron(datasets, amtAttr=3):
    w = [0] * amtAttr
    done = False
    while not done:
        dataset = random.randint(0, len(datasets)-1)
        for values in datasets[dataset]:
            if dataset == classifyperceptron(w, values):
                if classifysetperceptron(w, datasets):
                    done = True
            else:
                w = tuneperceptron(w, values, dataset)
    return w


def stochasticpercepton(datasets, amtAttr=3):
    w = [0] * amtAttr
    done = False
    while not done:
        dataset = random.randint(0, len(datasets) - 1)
        values = random.choice(datasets[dataset])
        if dataset == classifyperceptron(w, values):
            if classifysetperceptron(w, datasets):
                done = True
        else:
            w = tuneperceptron(w, values, dataset)
    return w


def tuneperceptron(w, values, dataset):
    dot = sum([w[value] * values[value] for value in range(len(values))])
    change = (dataset - dot)
    return [w[weight] + change * values[weight] for weight in range(len(w))]


def evalperceptron(datasets):
    correct = 0
    vals = 0
    for i in range(len(datasets)):
        for j in range(len(datasets[i])):
            training = deepcopy(datasets)
            test = training[i][j]
            training[i].remove(test)
            w = stochasticpercepton(training)
            if i == classifyperceptron(w, test):
                correct += 1
            else:
                print("Weight" + str(w))
                print("Faulty: " + str(test))
            vals += 1
    return vals - correct


# HERE STARTS THE LOGICAL REGRESSION #

def logisticstochastic(datasets, amtAttr=3):
    w = [0] * amtAttr
    done = False
    while not done:
        dataset = random.randint(0, len(datasets) - 1)
        values = random.choice(datasets[dataset])
        w = tunestochasticlogistic(w, values, dataset)
        if dataset == classifylogistic(w, values):
            if classifysetlogistic(w, datasets):
                done = True
    return w


def logisticbatch(datasets, amtAttr=3):
    w = [0] * amtAttr
    done = False
    while not done:
        w = tunebatchlogistic(w, datasets)
        if classifysetlogistic(w, datasets):
            done = True
    return w


def classifylogistic(w, values):
    dot = sum([w[i] * values[i] for i in range(len(values))])
    p1 = 1/(1 + math.exp(-dot))
    p2 = math.exp(-dot)/(1+math.exp(-dot))
    return 1 if p1 > p2 else 0


def classifysetlogistic(w, datasets):
    correct = 0
    for dataset in range(len(datasets)):
        for values in datasets[dataset]:
            if dataset != classifylogistic(w, values):
                return False
            correct += 1
    return True


def tunestochasticlogistic(w, values, dataset):
    dot = sum([w[i] * values[i] for i in range(len(values))])
    return [w[weight] + values[weight] * (dataset - 1/(1+math.exp(-dot))) for weight in range(len(w))]


def tunebatchlogistic(w, datasets):
    change = [0] * len(w)
    for classification in range(len(datasets)):
        for values in datasets[classification]:
            dot = sum([w[value] * values[value] for value in range(len(values))])
            change = [change[i] + (classification - (1/(1 + math.exp(-dot)))) * values[i] for i in range(len(change))]
    w = [w[i] + change[i] for i in range(len(w))]
    classifysetlogistic(w, datasets)
    return w


def getmax(datasets):
    x, y = 0, 0
    for data in datasets:
        for val in data:
            x = val[0] if val[0] > x else x
            y = val[1] if val[1] > y else y
    return x, y


def evalbatchlogistic(datasets):
    correct = 0
    vals = 0
    for i in range(len(datasets)):
        for j in range(len(datasets[i])):
            training = deepcopy(datasets)
            test = training[i][j]
            training[i].remove(test)
            w = logisticbatch(training)
            if i == classifyperceptron(w, test):
                correct += 1
            else:
                print("Weight" + str(w))
                print("Faulty: " + str(test))
            vals += 1
    return vals - correct


def evalstochlogistic(datasets):
    correct = 0
    vals = 0
    for i in range(len(datasets)):
        for j in range(len(datasets[i])):
            training = deepcopy(datasets)
            test = training[i][j]
            training[i].remove(test)
            w = logisticstochastic(training)
            if i == classifyperceptron(w, test):
                correct += 1
            else:
                print("Weight" + str(w))
                print("Faulty: " + str(test))
            vals += 1
    return vals - correct


if __name__ == '__main__':
    start_time = time.time()
    print("Perceptron faults: " + str(evalperceptron(parsesvm("datasets.txt"))))
    print("Time taken for evaluation: %s seconds" % (time.time() - start_time))
    start_time = time.time()
    print("Logistic Regression with Batch Gradient Ascent faults: " + str(evalbatchlogistic(parsesvm("datasets.txt"))))
    print("Time taken for evaluation: %s seconds" % (time.time() - start_time))
    start_time = time.time()
    print("Logistic Regression with Stochastic Gradient Ascent faults: " + str(evalstochlogistic(parsesvm("datasets.txt"))))
    print("Time taken for 30 evaluation: %s seconds" % (time.time() - start_time))


