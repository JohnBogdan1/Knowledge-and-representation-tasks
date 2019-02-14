cliques = []


def print_clique(clique):
    s = ""
    for node in clique:
        s += node["name"] + "|"

    print s[:-1]


def share_check(clique1, clique2):
    return list(set(clique1).intersection(clique2))


def my_intersection(candidates, neighbors):
    intersection = []

    for node in candidates:
        if node["name"] in neighbors:
            intersection.append(node)

    return intersection


def bron_kerbosch(clique, candidates, excluded):
    if not candidates and not excluded:
        cliques.append(clique)
        return

    # iterate over a copy of list
    for v in list(candidates):
        new_candidates = my_intersection(candidates, v["named_neighbors"])
        new_excluded = my_intersection(excluded, v["named_neighbors"])
        bron_kerbosch(clique + [v], new_candidates, new_excluded)
        candidates = [x for x in candidates if not (v["name"] == x.get('name'))]
        excluded.append(v)
