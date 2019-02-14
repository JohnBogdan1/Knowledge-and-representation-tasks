from copy import deepcopy

AND, OR, IMPL, EQ, NEG = "AND", "OR", "IMPL", "EQ", "NEG"


# return str(self.operator) + "(" + str(self.expr1) + "," + str(self.expr2) + ")"

class Expression:
    # def __repr__(self):
    #	return self.__str__()

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


class AndExpression(Expression):
    def __init__(self, expr1, expr2):
        self.can_split = True
        self.operator = AND
        self.expr1 = expr1
        self.expr2 = expr2

    def __str__(self):
        # return str(self.__dict__)
        return str(self.operator) + "(" + str(self.expr1) + "," + str(self.expr2) + ")"


class OrExpression(Expression):
    def __init__(self, expr1, expr2):
        self.can_split = True
        self.operator = OR
        self.expr1 = expr1
        self.expr2 = expr2

    def __str__(self):
        return str(self.operator) + "(" + str(self.expr1) + "," + str(self.expr2) + ")"


class ImplExpression(Expression, object):
    def __init__(self, expr1, expr2):
        self.can_split = True
        self.operator = IMPL
        self.expr1 = expr1
        self.expr2 = expr2

    def __str__(self):
        return str(self.operator) + "(" + str(self.expr1) + "," + str(self.expr2) + ")"

    def expanded(self):
        return OrExpression(NegExpression(self.expr1), self.expr2)


class EqExpression(Expression, object):
    def __init__(self, expr1, expr2):
        self.can_split = True
        self.operator = EQ
        self.expr1 = expr1
        self.expr2 = expr2

    def __str__(self):
        return str(self.operator) + "(" + str(self.expr1) + "," + str(self.expr2) + ")"

    def expanded(self):
        return OrExpression(AndExpression(self.expr1, self.expr2),
                            AndExpression(NegExpression(self.expr1), NegExpression(self.expr2)))


class NegExpression(Expression, object):
    def __init__(self, expr):
        super(NegExpression, self).__init__()
        self.can_split = False
        self.operator = NEG
        self.expr = expr

    def __str__(self):
        return str(self.operator) + "(" + str(self.expr) + ")"


class Variable(Expression, object):
    def __init__(self, name):
        super(Variable, self).__init__()
        self.can_split = False
        self.name = name

    def __str__(self):
        return str(self.name)


def apply_negation(expression):
    if isinstance(expression, NegExpression):
        return expression

    expr1 = expression.expr1
    expr2 = expression.expr2

    if isinstance(expression, AndExpression):
        return OrExpression(NegExpression(expr1), NegExpression(expr2))
    elif isinstance(expression, OrExpression):
        return AndExpression(NegExpression(expr1), NegExpression(expr2))
    elif isinstance(expression, ImplExpression):
        return AndExpression(expr1, NegExpression(expr2))
    elif isinstance(expression, EqExpression):
        return OrExpression(AndExpression(expr1, NegExpression(expr2)), AndExpression(NegExpression(expr1), expr2))


def is_complex_formula(formula):
    return isinstance(formula, ImplExpression) or isinstance(formula, EqExpression)


def pre_processing(formulae_set):
    new_formulae_set = []

    for formula in formulae_set:
        if is_complex_formula(formula):
            new_formulae_set.append(formula.expanded())
        else:
            new_formulae_set.append(formula)

    return new_formulae_set


def heuristic(formulae_set):
    for formula in formulae_set:
        if isinstance(formula, AndExpression):
            return formulae_set.index(formula)

    for formula in formulae_set:
        if isinstance(formula, NegExpression) and not isinstance(formula.expr, Variable):
            return formulae_set.index(formula)

    for formula in formulae_set:
        if isinstance(formula, OrExpression):
            return formulae_set.index(formula)

    return -1


def is_literal(formula):
    if isinstance(formula, Variable):
        return True
    elif isinstance(formula, NegExpression):
        if isinstance(formula.expr, Variable):
            return True

    return False


def is_finished_state(formulae_set):
    for formula in formulae_set:
        if not is_literal(formula):
            return False

    return True


def are_complementary(formula1, formula2):
    if isinstance(formula1, NegExpression) and isinstance(formula2, Variable):
        if formula1.expr.__eq__(formula2):
            return True

    if isinstance(formula1, Variable) and isinstance(formula2, NegExpression):
        if formula2.expr.__eq__(formula1):
            return True

    return False


def is_closed_state(formulae_set):
    for formula1 in formulae_set:
        for formula2 in formulae_set:
            if are_complementary(formula1, formula2):
                return True

    return False


def print_formulae_set(formulae_set):
    print [form.__str__() for form in formulae_set]


def make_tree(formulae_set):
    if is_finished_state(formulae_set) and is_closed_state(formulae_set):
        return "X"
    elif is_finished_state(formulae_set) and not is_closed_state(formulae_set):
        print_formulae_set(formulae_set)
        return "O"

    formulae_set = pre_processing(formulae_set)

    index = heuristic(formulae_set)
    formula = formulae_set[index]

    if isinstance(formula, AndExpression):
        formulae_set.remove(formula)
        formulae_set.append(formula.expr1)
        formulae_set.append(formula.expr2)

        # print "AndExpression: ", formulae_set
        ret = make_tree(deepcopy(formulae_set))

        if ret == "X":
            return "X"
        else:
            return "O"
    elif isinstance(formula, NegExpression):
        formulae_set.remove(formula)
        formulae_set.append(apply_negation(formula.expr))

        # print "NegExpression:", formulae_set
        ret = make_tree(deepcopy(formulae_set))

        if ret == "X":
            return "X"
        else:
            return "O"
    elif isinstance(formula, OrExpression):
        formulae_set.remove(formula)
        left_formulae_set = deepcopy(formulae_set)
        right_formulae_set = deepcopy(formulae_set)

        left_formulae_set.append(formula.expr1)
        right_formulae_set.append(formula.expr2)

        # print "LeftNegExpression:", left_formulae_set
        # print "RightNegExpression:", right_formulae_set

        left_ret = make_tree(left_formulae_set)

        if left_ret == "O":
            return "O"
        else:
            right_ret = make_tree(right_formulae_set)
            if right_ret == "X":
                return "X"
            else:
                return "O"


def main():
    print "Laborator 1 - KRR"

    expr = AndExpression(OrExpression(NegExpression(Variable("A")), Variable("B")),
                         OrExpression(Variable("C"), NegExpression(Variable("D"))))

    # print expr

    tr_expr = NegExpression(ImplExpression(Variable("A"), Variable("B")))

    # print apply_negation(tr_expr.expr)

    formulae_set1 = [ImplExpression(Variable("p"), Variable("q")), ImplExpression(Variable("q"), Variable("r")),
                     NegExpression(ImplExpression(Variable("p"), Variable("r")))]

    formulae_set2 = [NegExpression(ImplExpression(Variable("A"), Variable("B"))),
                     OrExpression(NegExpression(Variable("A")), Variable("B"))]

    formulae_set3 = [NegExpression(AndExpression(ImplExpression(Variable("A1"), Variable("A2")),
                                                 OrExpression(Variable("A3"), NegExpression(
                                                     OrExpression(Variable("A3"), NegExpression(Variable("A1")))))))]

    formulae_set4 = [
        ImplExpression(Variable("WeatherSunny"), Variable("ParkBeautiful")),
        ImplExpression(Variable("ParkBeautiful"), Variable("PeopleWalkDogs")),
        ImplExpression(Variable("PeopleWalkDogs"), Variable("ParkFullDogs")),
        AndExpression(Variable("WeatherSunny"), NegExpression(Variable("ParkFullDogs")))
    ]

    formulae_set5 = [
        ImplExpression(Variable("PaulLikes"), Variable("PaulBuys")),
        ImplExpression(Variable("WendyLikes"), Variable("WendyBuys")),
        ImplExpression(Variable("SusanLikes"), Variable("SusanBuys")),
        ImplExpression(Variable("WendyBuys"), Variable("BasketHas")),
        OrExpression(Variable("PaulLikes"), OrExpression(Variable("WendyLikes"), Variable("SusanLikes"))),
        Variable("BasketHas")
    ]

    formulae_set6 = [
        ImplExpression(Variable("YuehBlackmailed"), Variable("YuehPacts")),
        ImplExpression(Variable("YuehPacts"), NegExpression(Variable("YuehLoyal"))),
        EqExpression(Variable("DukeRewards"), Variable("YuehLoyal")),
        AndExpression(Variable("YuehBlackmailed"), Variable("DukeRewards"))
    ]

    formulae_set_demo = [
        OrExpression(Variable("A"), Variable("B")),
        ImplExpression(Variable("B"), EqExpression(NegExpression(Variable("D")), Variable("C"))),
        EqExpression(NegExpression(Variable("A")), Variable("D")),
        Variable("C")
    ]

    # print pre_processing(formulae_set1)

    print_formulae_set(formulae_set1)
    print "Result is: %s" % make_tree(formulae_set1)

    print_formulae_set(formulae_set4)
    print "P1-Result is: %s" % make_tree(formulae_set4)

    print_formulae_set(formulae_set5)
    print "P2-Result is: %s" % make_tree(formulae_set5)

    print_formulae_set(formulae_set6)
    print "P3-Result is: %s" % make_tree(formulae_set6)

    print_formulae_set(formulae_set_demo)
    print "DEMO-Result is: %s" % make_tree(formulae_set_demo)


if __name__ == '__main__':
    main()
