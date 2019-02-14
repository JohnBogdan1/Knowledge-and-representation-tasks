import math
import random

assignments = {1: [0, 1], 2: [(0, 0),
                              (0, 1),
                              (1, 0),
                              (1, 1)]}


def find_node_by_name(nodes, name):
    for node in nodes:
        if node["name"] == name:
            return node

    return None


def my_sigmoid(x):
    return 1 / ((1 + math.exp(-x)) * 1.0)


def print_thetas(nodes):
    for node in nodes:
        print node["name"], ";", node["parent"], ";", " ".join([str(my_sigmoid(val[1])) for val in node["theta"]])


def my_count(l1, l2):
    c1 = 0
    c2 = 0
    for i in xrange(len(l1)):
        if l1[i] == 1 and l2[i] == 0:
            c1 += 1

        if l1[i] == 1 and l2[i] == 1:
            c2 += 1
    return c1, c2


def my_count_v1_aux(l1, l2):
    c1 = 0
    c2 = 0
    c3 = 0
    c4 = 0
    for i in xrange(len(l1)):
        if l1[i] == 0 and l2[i] == 0:
            c1 += 1

        if l1[i] == 0 and l2[i] == 1:
            c2 += 1

        if l1[i] == 1 and l2[i] == 0:
            c3 += 1

        if l1[i] == 1 and l2[i] == 1:
            c4 += 1
    return c1, c2, c3, c4


def my_count_v1(l1, l2, l3):
    c1 = 0
    c2 = 0
    c3 = 0
    c4 = 0
    for i in xrange(len(l1)):
        if l1[i] == 1 and l2[i] == 0 and l3[i] == 0:
            c1 += 1

        if l1[i] == 1 and l2[i] == 0 and l3[i] == 1:
            c2 += 1

        if l1[i] == 1 and l2[i] == 1 and l3[i] == 0:
            c3 += 1

        if l1[i] == 1 and l2[i] == 1 and l3[i] == 1:
            c4 += 1

    return c1, c2, c3, c4


def set_pbs(node, n, parents, values):
    cpds = []
    thetas = []
    node = node.strip()
    if n == 0:
        cpd = {}
        # cpd[node] = 1
        cpds.append((cpd, values[0]))
        thetas.append((cpd, random.uniform(0, 1)))
    elif n == 1:
        for i in range(2 * n):
            cpd = {parents[0]: assignments[n][i]}
            # cpd[node] = 1
            cpds.append((cpd, values[i]))
            thetas.append((cpd, random.uniform(0, 1)))
    elif n == 2:
        for i in range(2 * n):
            cpd = {parents[j]: assignments[n][i][j] for j in range(n)}
            # cpd[node] = 1
            cpds.append((cpd, values[i]))
            thetas.append((cpd, random.uniform(0, 1)))

    return cpds, thetas


def laplace_smoothing_freq(numerator, denominator, alpha=1, cardinal=2):
    return (numerator + alpha) / ((denominator + alpha * cardinal) * 1.0)


def mle_aprox(bn_nodes, list_map):
    for node in bn_nodes:
        name = node["name"]
        parents = node["parent"]
        lenp = len(parents)

        if lenp == 0:
            l = list_map[name]
            p_res = laplace_smoothing_freq(l.count(1), len(l))
            print name, ";", parents, ";", p_res
            node["approximated_cpd"] = set_pbs(name, lenp, parents, [p_res])
        elif lenp == 1:
            l1 = list_map[name]
            l2 = list_map[parents[0]]

            c1, c2 = my_count(l1, l2)

            p_res1 = laplace_smoothing_freq(c1, l2.count(0))
            p_res2 = laplace_smoothing_freq(c2, l2.count(1))

            print name, ";", parents, ";", p_res1, p_res2
            node["approximated_cpd"] = set_pbs(name, lenp, parents, [p_res1, p_res2])
        elif lenp == 2:
            l1 = list_map[name]
            l2 = list_map[parents[0]]
            l3 = list_map[parents[1]]

            c1, c2, c3, c4 = my_count_v1(l1, l2, l3)
            c11, c22, c33, c44 = my_count_v1_aux(l2, l3)

            p_res1 = laplace_smoothing_freq(c1, c11)
            p_res2 = laplace_smoothing_freq(c2, c22)
            p_res3 = laplace_smoothing_freq(c3, c33)
            p_res4 = laplace_smoothing_freq(c4, c44)

            print name, ";", parents, ";", p_res1, p_res2, p_res3, p_res4
            node["approximated_cpd"] = set_pbs(name, lenp, parents, [p_res1, p_res2, p_res3, p_res4])


def get_var_sample_indices(list_map, parents, max_len):
    if len(parents) == 0:
        return range(max_len)

    inds = []

    for i in xrange(max_len):
        stop = False
        for parent in parents:
            if not list_map[parent][i] == parents[parent]:
                stop = True

        if not stop:
            inds.append(i)

    return inds


def stochastic_kl_optim(list_map, nodes, nr_iter=100, tau=1e-3):
    sample_len = len(list_map["A"])
    cache = {}
    for _ in xrange(nr_iter):
        for node in nodes:
            name = node["name"]
            theta_tuples_list = node["theta"]

            for k in range(len(theta_tuples_list[:])):
                parents, theta = theta_tuples_list[k][0], theta_tuples_list[k][1]
                hash_name = name + "".join(parents.keys()) + "".join([str(v) for v in parents.values()])

                if not hash_name in cache:
                    inds = get_var_sample_indices(list_map, parents, sample_len)
                    cache[hash_name] = inds
                else:
                    inds = cache[hash_name]

                for i in inds:
                    theta += -tau * (my_sigmoid(theta) - list_map[name][i])

                new_tuple = list(theta_tuples_list[k])
                new_tuple[1] = theta
                theta_tuples_list[k] = tuple(new_tuple)


def main():
    file = open("bn1", "r")
    file_samples = open("samples_bn1", "r")
    m, nn = map(int, file.readline().split())

    bn_nodes = []
    for _ in xrange(m):
        node, parents, values = file.readline().split(";")
        values = map(float, values.strip().split())
        parents = parents.strip().split()
        # print node
        # print parents
        # print values
        # print

        n = len(parents)

        bn_n = {"name": node.strip(), "parent": parents}

        bn_n["cpd"], bn_n["theta"] = set_pbs(node, n, parents, values)
        bn_nodes.append(bn_n)

    # print bn_nodes

    names = file_samples.readline().split()

    vars = [[] for _ in range(len(names))]

    list_map = {names[i]: vars[i] for i in range(len(names))}

    for line in file_samples:
        numbers = map(int, line.split())
        for i in range(len(numbers)):
            vars[i].append(numbers[i])

    print "####### [MLE] #######"

    mle_aprox(bn_nodes, list_map)

    print "####### [/MLE] #######"

    print "####### [BLE] #######"

    stochastic_kl_optim(list_map, bn_nodes)
    print_thetas(bn_nodes)

    print "####### [/BLE] #######"

    file.close()
    file_samples.close()


if __name__ == '__main__':
    main()
