from copy import deepcopy
import kruskal
import maximal_cliques
import random
from threading import Thread
from time import sleep

A, B, C, D, E, F, G, H, I, J, K, L = "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L"

assignments = {1: [0, 1], 2: [(0, 0),
                              (0, 1),
                              (1, 0),
                              (1, 1)]}

global_root = None


def define_parents_and_neighbors(nodes):
    for node in nodes:
        for parent_name in node["named_parent"]:
            parent = find_node_by_name(nodes, parent_name)
            node["parent"].append(parent)
            node["neighbors"].append(parent)
            parent["neighbors"].append(node)


def define_named_neighbors(nodes):
    for node in nodes:
        for neigh in node["neighbors"]:
            node["named_neighbors"].append(neigh["name"])


def pretty_print_graph(nodes):
    for node in nodes:
        s = "" + node["name"]
        for neigh in node["named_neighbors"]:
            s += "|" + neigh
        print s


def pretty_print_graph_v1(nodes, key):
    for node in nodes:
        s = "" + node["name"]
        for neigh in node[key]:
            s += "|" + neigh["name"]
        print s


def find_node_by_name(nodes, name):
    for node in nodes:
        if node["name"] == name:
            return node

    return None


def moralize_graph(nodes):
    for node in nodes:
        parents = node["parent"]
        if len(parents) >= 2:
            # add edge between every parent nodes
            for i in range(len(parents) - 1):
                parents[i]["neighbors"].append(parents[i + 1])
                parents[i]["named_neighbors"].append(parents[i + 1]["name"])

                parents[i + 1]["neighbors"].append(parents[i])
                parents[i + 1]["named_neighbors"].append(parents[i]["name"])


def get_min_node_score(scores):
    min_score = 9999
    min_node = None

    for node in scores:
        score = scores[node][0]

        if score < min_score:
            min_score = score
            min_node = node

    return min_node


def fill_in_edges(node):
    edges = []
    node_neighbors = node["neighbors"]

    # add edge between non-adjacent neighbors of node as a result of its removal
    for i in range(len(node_neighbors)):
        for j in range(i + 1, len(node_neighbors)):
            if node_neighbors[j]["name"] not in node_neighbors[i]["named_neighbors"]:
                edges.append((node_neighbors[i], node_neighbors[j]))

    return edges


def min_fill(node):
    edges = fill_in_edges(node)
    return len(edges), edges


def add_edges(original_nodes, edges):
    for edge in edges:
        print "ADDED EDGE:", edge[0]["name"], edge[1]["name"]
        edge[0]["neighbors"].append(edge[1])
        edge[0]["named_neighbors"].append(edge[1]["name"])

        edge[1]["neighbors"].append(edge[0])
        edge[1]["named_neighbors"].append(edge[0]["name"])

        # add edge(chord) in original graph
        node_left = find_node_by_name(original_nodes, edge[0]["name"])
        node_right = find_node_by_name(original_nodes, edge[1]["name"])

        node_left["neighbors"].append(node_right)
        node_left["named_neighbors"].append(node_right["name"])

        node_right["neighbors"].append(node_left)
        node_right["named_neighbors"].append(node_left["name"])


def remove_node_from_graph(nodes, node_to_remove):
    nodes = [x for x in nodes if not (node_to_remove["name"] == x.get('name'))]

    for node in nodes:
        if node_to_remove["name"] in node["named_neighbors"]:
            node["neighbors"] = [x for x in node["neighbors"] if not (node_to_remove["name"] == x.get('name'))]
            node["named_neighbors"] = [x for x in node["named_neighbors"] if not (node_to_remove["name"] == x)]

    return nodes


def triangulate_graph(original_nodes, nodes):
    elimination_order = []
    while nodes:
        scores = {node["name"]: min_fill(node) for node in nodes}
        min_score_node = get_min_node_score(scores)
        elimination_order.append(min_score_node)

        add_edges(original_nodes, scores[min_score_node][1])

        node_to_remove = find_node_by_name(nodes, min_score_node)
        nodes = remove_node_from_graph(nodes, node_to_remove)

    print "ELIMINATION ORDER:", elimination_order
    return elimination_order


def check_cpd(query, cpd, value):
    p = 0
    for q in query:
        if q in cpd and cpd[q] == query[q]:
            p = value
            break
    return p


def get_node_values(nodes, name, clique_nodes):
    node = find_node_by_name(nodes, name)
    parents = [parent["name"] for parent in node["parent"]]
    n = len(parents)
    values = node["values"]
    cpds = []
    if n == 0:
        cpd = {}
        cpd[name] = 1
        cpds.append((cpd, values[0]))
    elif n == 1:
        for i in range(2 * n):
            cpd = {parents[0]: assignments[n][i]}
            cpd[name] = 1
            cpds.append((cpd, values[i]))
    else:
        for i in range(2 * n):
            cpd = {parents[j]: assignments[n][i][j] for j in range(n)}
            cpd[name] = 1
            cpds.append((cpd, values[i]))

    # print cpds
    return node["name"], cpds


def update_nodes_cpd(nodes, updated_cpd):
    for node in nodes:
        cpd_elems = node["cpd"]
        for i in range(len(cpd_elems[:])):
            cpd = cpd_elems[i]
            if cpd[0] == updated_cpd[0]:
                cpd_elems[i] = updated_cpd


def incorporate_evidence(nodes, evidence_name, evidence_value):
    for node in nodes:
        found = 0
        for cpd in node["cpd"]:
            cpd_name, cpd_tuples = cpd

            for i in range(len(cpd_tuples[:])):
                cpd_tuple = cpd_tuples[i]
                cpd_assignments, cpd_value = cpd_tuple
                if evidence_name in cpd_assignments:
                    found = 1
                    if cpd_assignments[evidence_name] != evidence_value:
                        new_cpd_tuple = list(cpd_tuple)
                        new_cpd_tuple[1] = 0
                        cpd_tuples[i] = tuple(new_cpd_tuple)

            if found:
                updated_cpd = cpd
                update_nodes_cpd(nodes, updated_cpd)
                return


def set_links(root):
    for neighbor in root["neighbors"]:
        if neighbor["name"] not in root["named_parent"]:
            root["children"].append(neighbor)
            root["named_children"].append(neighbor["name"])

            neighbor["parent"].append(root)
            neighbor["named_parent"].append(root["name"])
            set_links(neighbor)

    # set leaf nodes
    if not root["children"]:
        root["leaf"] = True
        # print root["name"], root["leaf"]
        return


def leaf_function(**node):
    name = node["name"]
    parent = node["parent"][0]
    # print "Working on %s node" % name

    print "[%s] -> LEAF NODE SENT MSG TO PARENT!" % name
    parent["recv_child_map"][name] = True
    parent["msg_child_map"][name] = "GOT MSG FROM CHILD" + name

    while False in node["recv_parent_map"].values():
        sleep(1)

    print "LEAF [%s] RECEIVED ALL FROM ROOT." % name

    sleep(1)

    # print "Finished on %s node" % node["name"]


def intermediary_node_function(**node):
    global global_root
    name = node["name"]
    # print "Working on %s node" % name

    while False in node["recv_child_map"].values():
        sleep(1)

    if name == global_root:
        print "-> RECEIVED ALL IN ROOT.\n"
        print "[[ROOT -> LEAVES]]\n"

        sleep(1)

        children = node["children"]

        print "[%s] -> ROOT NODE SENT MSG TO CHILDREN!" % name
        for child in children:
            child["recv_parent_map"][name] = True
            child["msg_parent_map"][name] = "GOT MSG FROM PARENT" + name
    else:
        print "[%s] -> NODE SENT MSG TO PARENT!" % name
        parent = node["parent"][0]
        parent["recv_child_map"][name] = True
        parent["msg_child_map"][name] = "GOT MSG FROM CHILD" + name

        while False in node["recv_parent_map"].values():
            sleep(1)

        children = node["children"]

        print "[%s] -> NODE SENT MSG TO CHILDREN!" % name
        for child in children:
            child["recv_parent_map"][name] = True
            child["msg_parent_map"][name] = "GOT MSG FROM PARENT" + name

    sleep(1)

    # print "Finished on %s node" % node["name"]


def main():
    file = open("bnet", "r")

    # define nodes of the graph
    nodes = []
    for line in file:
        node, parents, values = line.split(";")
        values = map(float, values.strip().split())
        parents = parents.strip().split()

        bn_n = {"name": node.strip(), "neighbors": [], "named_neighbors": [], "named_parent": parents, "parent": [],
                "values": values}

        nodes.append(bn_n)

    define_parents_and_neighbors(nodes)
    define_named_neighbors(nodes)

    print "MORALIZED GRAPH"
    moralize_graph(nodes)
    pretty_print_graph(nodes)

    print "\nTRIANGULATED GRAPH"
    triangulate_graph(nodes, deepcopy(nodes))
    pretty_print_graph(nodes)

    print "\nMAXIMAL CLIQUES"
    maximal_cliques.bron_kerbosch([], nodes, [])

    cliques = maximal_cliques.cliques
    str_cliques = []

    clique_nodes = {}
    k = 1

    for clique in cliques:
        str_clique = [node["name"] for node in clique]
        str_cliques.append(str_clique)
        maximal_cliques.print_clique(clique)
        name = "c" + str(k)
        clique_nodes[name] = str_clique
        k += 1

    edges = set()

    for i in range(len(clique_nodes)):
        for j in range(i + 1, len(clique_nodes)):
            key1 = clique_nodes.keys()[i]
            key2 = clique_nodes.keys()[j]
            clique1 = clique_nodes[key1]
            clique2 = clique_nodes[key2]
            share = maximal_cliques.share_check(clique1, clique2)
            if share:
                # print clique1, clique2, len(share)
                edges.add((len(share), key1, key2))
                edges.add((len(share), key2, key1))

    vertices = clique_nodes.keys()
    # print clique_nodes
    # print vertices
    # print edges

    my_graph = dict()
    my_graph["vertices"] = vertices
    my_graph["edges"] = edges

    # print my_graph

    mst = kruskal.kruskal(my_graph)

    print "\nMAXIMUM SPANNING TREE"
    print mst

    # for edge in mst: print "(" + str(clique_nodes[edge[1]]) + ", " + str(clique_nodes[edge[2]]) + ") -> " + str(edge[0])

    # *********** second part ***********
    query = {"E": 0}
    print "\nQUERY:", query

    clique_tree_nodes = []
    orig_clique_nodes = deepcopy(clique_nodes)

    for clique in clique_nodes:
        # print clique_nodes[clique], "->", clique
        str_nodes = clique_nodes[clique]
        # format your CPD graph representation
        clique_nodes[clique] = [get_node_values(nodes, node, clique_nodes[clique]) for node in str_nodes]

        cn = {"name": clique, "neighbors": [], "children": [], "named_children": [], "parent": [], "named_parent": [],
              "leaf": False, "recv_child_map": None, "recv_parent_map": None, "msg_child_map": None,
              "msg_parent_map": None}
        cn["cpd"] = clique_nodes[clique]
        clique_tree_nodes.append(cn)

    # print orig_clique_nodes

    # set clique nodes neighbors
    for edge in mst:
        clqn1 = find_node_by_name(clique_tree_nodes, edge[1])
        clqn2 = find_node_by_name(clique_tree_nodes, edge[2])
        clqn1["neighbors"].append(clqn2)
        clqn2["neighbors"].append(clqn1)

        clique1 = orig_clique_nodes[clqn1["name"]]
        clique2 = orig_clique_nodes[clqn2["name"]]
        share = maximal_cliques.share_check(clique1, clique2)
        # print clique1, clique2, share

        # set sepsets
        if share:
            if not "sepset" in clqn1:
                clqn1["sepset"] = {clqn2["name"]: share}
            else:
                clqn1["sepset"][clqn2["name"]] = share

            if not "sepset" in clqn2:
                clqn2["sepset"] = {clqn1["name"]: share}
            else:
                clqn2["sepset"][clqn1["name"]] = share

    print "\nSEPSETS"
    for c in clique_tree_nodes: print c["name"], c["sepset"]

    for evidence in query:
        incorporate_evidence(clique_tree_nodes, evidence, query[evidence])

    print "\nFACTORS"
    for c in clique_tree_nodes: print c["name"], c["cpd"]

    # pretty_print_graph_v1(clique_tree_nodes, "neighbors")

    # root = clique_tree_nodes[random.randint(0, len(clique_tree_nodes) - 1)]
    root = [node for node in clique_tree_nodes if node["name"] == "c1"][0]
    global global_root
    global_root = root["name"]
    print "\n-> ROOT:", root["name"]

    # set children/parent according to root init
    set_links(root)
    print "\nPARENTS:"
    pretty_print_graph_v1(clique_tree_nodes, "parent")

    print "\nLEAVES:"
    for c in clique_tree_nodes:
        if c["leaf"]:
            print c["name"]

    for node in clique_tree_nodes:
        node["recv_child_map"] = {children: False for children in node["named_children"]}
        node["recv_parent_map"] = {parent: False for parent in node["named_parent"]}

        node["msg_child_map"] = {children: None for children in node["named_children"]}
        node["msg_parent_map"] = {parent: None for parent in node["named_parent"]}

    print "\nINITIAL STATUS OF THE CLIQUE NODES"
    if 1 == 2:
        for n in clique_tree_nodes:
            print n["name"], "sent to parent -> ", n["recv_parent_map"]
            print n["name"], "received from child -> ", n["recv_child_map"]
    else:
        print "INITIALIZED."

    print "----------------"
    print "\nSEND_MESSAGES"
    print "----------------"
    print "[[LEAVES -> ROOT]]\n"

    leaf_threads = []
    for c in clique_tree_nodes:
        if c["leaf"]:
            thread = Thread(target=leaf_function, kwargs=(c))
            thread.setName(c["name"])
            leaf_threads.append(thread)
            thread.start()

    non_leaf_threads = []
    for c in clique_tree_nodes:
        if not c["leaf"]:
            thread = Thread(target=intermediary_node_function, kwargs=(c))
            thread.setName(c["name"])
            non_leaf_threads.append(thread)
            thread.start()

    for thread in leaf_threads:
        thread.join()
        print thread.name, "leaf finished...exiting"

    for thread in non_leaf_threads:
        thread.join()
        print thread.name, "node finished...exiting"

    print "\nALL DONE."


if __name__ == '__main__':
    main()
