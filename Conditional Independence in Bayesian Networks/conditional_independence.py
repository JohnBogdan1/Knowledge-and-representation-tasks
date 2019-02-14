A, B, C, D, E = "A", "B", "C", "D", "E"


def print_path(path):
    l = []
    for node in path:
        l.append(node["name"])

    return l


def check_if_observed_any_desc(children, given):
    for child in children:
        if child in given:
            return True

    return False


def check_causal_trail(x_i_prev, x_i_curr, x_i_next, given):
    if x_i_curr in x_i_prev["children"] and \
            x_i_next in x_i_curr["children"] and x_i_curr not in given:
        return True

    return False


def check_evidential_trail(x_i_prev, x_i_curr, x_i_next, given):
    if x_i_prev in x_i_curr["children"] and \
            x_i_curr in x_i_next["children"] and x_i_curr not in given:
        return True

    return False


def check_common_cause(x_i_prev, x_i_curr, x_i_next, given):
    if x_i_prev in x_i_curr["children"] and \
            x_i_next in x_i_curr["children"] and x_i_curr not in given:
        return True

    return False


def check_common_effect(x_i_prev, x_i_curr, x_i_next, given):
    if x_i_curr in x_i_prev["children"] and \
            x_i_curr in x_i_next["children"] and (
            x_i_curr in given or check_if_observed_any_desc(x_i_curr["children"], given)):
        return True

    return False


def check_cond_inds(path, given):
    x_i_prev = path[0]
    x_i_curr = path[1]
    x_i_next = path[2]

    res_c11 = check_causal_trail(x_i_prev, x_i_curr, x_i_next, given)
    res_c12 = check_evidential_trail(x_i_prev, x_i_curr, x_i_next, given)
    res_c13 = check_common_cause(x_i_prev, x_i_curr, x_i_next, given)
    res_c14 = check_common_effect(x_i_prev, x_i_curr, x_i_next, given)

    return res_c11 or res_c12 or res_c13 or res_c14


def check_paths(paths, given):
    for path in paths:
        if len(path) > 3:
            for i in range(len(path) - 3 + 1):
                temp_path = path[i:3 + i]
                # print print_path(temp_path)
                res = check_cond_inds(temp_path, given)
                # print "res: ", res
                if res == False:
                    break
        else:
            # print print_path(path)
            res = check_cond_inds(path, given)
            # print "res: ", res
            if res:
                return False

    return True


# find all paths from start to end
def dfs(start, end):
    print "PATH:", start["name"], "->", end["name"]
    stack = [(start, [start])]
    visited = []

    while stack:
        node, path = stack.pop()
        # print node["name"]
        # print visited

        for neighbor in node["neighbors"]:
            if not neighbor in visited:
                if neighbor["name"] == end["name"]:
                    yield path + [neighbor]
                else:
                    stack.append((neighbor, path + [neighbor]))

        visited.append(node)


def main():
    a = {"name": A, "neighbors": [], "children": [], "parent": []}
    b = {"name": B, "neighbors": [], "children": [], "parent": []}
    c = {"name": C, "neighbors": [], "children": [], "parent": []}
    d = {"name": D, "neighbors": [], "children": [], "parent": []}
    e = {"name": E, "neighbors": [], "children": [], "parent": []}
    a["children"].append(c)
    b["children"].extend([c, d])
    c["children"].extend([e, d])

    c["parent"].extend([a, b])
    d["parent"].extend([c, b])
    e["parent"].append(c)

    a["neighbors"].append(c)
    b["neighbors"].extend([c, d])
    c["neighbors"].extend([a, b, d, e])
    d["neighbors"].extend([b, c])
    e["neighbors"].append(c)

    queries = [
        {"X": [a, b], "Y": [e], "Z": [None]},
        {"X": [a, b], "Y": [e], "Z": [c]},
        {"X": [e], "Y": [d], "Z": [None]},
        {"X": [e], "Y": [d], "Z": [b]},
        {"X": [e], "Y": [d], "Z": [c]},
        {"X": [a], "Y": [b], "Z": [None]},
        {"X": [a], "Y": [b], "Z": [c]},
        {"X": [a], "Y": [b], "Z": [d]},
    ]

    for query in queries:
        # query = queries[4]
        all_paths = []
        for node in query["X"]:
            x_paths = dfs(node, query["Y"][0])
            for path in x_paths:
                all_paths.append(path)

        if query["Z"][0] != None:
            print "GIVEN:", query["Z"][0]["name"]
        else:
            print "GIVEN: []"

        print check_paths(all_paths, query["Z"])
        print
        # break


if __name__ == '__main__':
    main()
