from copy import deepcopy

AND, OR, IMPL, EQ, NEG = "AND", "OR", "IMPL", "EQ", "NEG"
POS, NEC = "POS", "NEC"


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


class ImplExpression(Expression):
    def __init__(self, expr1, expr2):
        self.can_split = True
        self.operator = IMPL
        self.expr1 = expr1
        self.expr2 = expr2

    def __str__(self):
        return str(self.operator) + "(" + str(self.expr1) + "," + str(self.expr2) + ")"

    def expanded(self):
        return OrExpression(NegExpression(self.expr1), self.expr2)


class EqExpression(Expression):
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


class NegExpression(Expression):
    def __init__(self, expr):
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


# Modal operators

class PossibilityExpression(Expression):
    def __init__(self, expr):
        self.operator = POS
        self.expr = expr

    def __str__(self):
        return str(self.operator) + "(" + str(self.expr) + ")"


class NecessityExpression(Expression):
    def __init__(self, expr):
        self.operator = NEC
        self.expr = expr

    def __str__(self):
        return str(self.operator) + "(" + str(self.expr) + ")"


def apply_negation(expression):
    if isinstance(expression, NegExpression):
        return expression
    elif isinstance(expression, PossibilityExpression):
        return NecessityExpression(NegExpression(expression.expr))
    elif isinstance(expression, NecessityExpression):
        return PossibilityExpression(NegExpression(expression.expr))

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


##################################
def pos_var(name):
    return Variable(name)


def neg_var(name):
    return NegExpression(Variable(name))


def check(variable, world):
    for var in world["variables"]:
        if variable.__eq__(var):
            return True

    return False


def evaluate_world(expr, world):
    if isinstance(expr, PossibilityExpression):
        for child_world in world["children"]:
            val = evaluate_world(expr.expr, child_world)
            if val == True:
                return True
        return False
    elif isinstance(expr, NecessityExpression):
        for child_world in world["children"]:
            val = evaluate_world(expr.expr, child_world)
            if val == False:
                return False

        return True
    elif isinstance(expr, Variable) or (isinstance(expr, NegExpression) and isinstance(expr.expr, Variable)):
        return check(expr, world)
    elif isinstance(expr, NegExpression):
        return evaluate_world(apply_negation(expr.expr), world)
    elif isinstance(expr, AndExpression):
        left = evaluate_world(expr.expr1, world)
        right = evaluate_world(expr.expr2, world)
        return left and right
    elif isinstance(expr, OrExpression):
        left = evaluate_world(expr.expr1, world)
        right = evaluate_world(expr.expr2, world)
        return left or right
    elif isinstance(expr, ImplExpression) or isinstance(expr, EqExpression):
        return evaluate_world(expr.expanded(), world)


def main():
    print "Laborator 2 - KRR"

    expr = AndExpression(OrExpression(NegExpression(Variable("A")), Variable("B")),
                         OrExpression(Variable("C"), NegExpression(Variable("D"))))

    # print expr

    e1 = NegExpression(NecessityExpression(Variable("A")))
    e2 = NegExpression(PossibilityExpression(Variable("A")))

    # FIRST SET
    W0 = {"variables": [neg_var("p"), pos_var("q")]}
    W1 = {"variables": [pos_var("p"), neg_var("q")]}
    W2 = {"variables": [neg_var("p"), neg_var("q")]}
    W3 = {"variables": [pos_var("p"), pos_var("q")]}

    W0["children"] = [W1, W2]
    W1["children"] = [W2, W3]
    W2["children"] = [W3]
    W3["children"] = []

    print "\n############"
    print "RUN SET #1"

    my_expr = NecessityExpression(NecessityExpression(pos_var("q")))
    print "\nEvaluate: %s" % my_expr.__str__()
    print "Result: %s" % evaluate_world(my_expr, W0)

    # SECOND SET

    W0 = {"variables": [pos_var("D"), pos_var("W")]}
    W1 = {"variables": [pos_var("D"), pos_var("W"), neg_var("C"), pos_var("F"), pos_var("B")]}
    W2 = {"variables": [pos_var("D"), pos_var("W"), neg_var("F"), pos_var("C"), pos_var("B")]}
    W3 = {"variables": [pos_var("D"), pos_var("W"), neg_var("C"), neg_var("F"), pos_var("B")]}

    W0["children"] = [W1, W2, W3]
    W1["children"] = []
    W2["children"] = []
    W3["children"] = []

    print "\n############"
    print "RUN SET #2"

    f1 = NecessityExpression(ImplExpression(pos_var("D"), OrExpression(pos_var("C"), pos_var("B"))))
    print "\nEvaluate: %s" % f1.__str__()
    print "Result: %s" % evaluate_world(f1, W0)

    f2 = NecessityExpression(ImplExpression(pos_var("W"), OrExpression(pos_var("F"), pos_var("B"))))
    print "\nEvaluate: %s" % f2.__str__()
    print "Result: %s" % evaluate_world(f2, W0)

    f3 = NegExpression(PossibilityExpression(AndExpression(pos_var("C"), pos_var("F"))))
    print "\nEvaluate: %s" % f3.__str__()
    print "Result: %s" % evaluate_world(f3, W0)

    f4 = NecessityExpression(pos_var("B"))
    print "\nEvaluate: %s" % f4.__str__()
    print "Result: %s" % evaluate_world(f4, W0)


if __name__ == '__main__':
    main()
