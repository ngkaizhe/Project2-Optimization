from typing import List
from method.golden_section import golden_section, build_var_dict
from arrai.arrai import Arrai
from Equation import Equation
from Exception.explosion import Explosion
from decimal import Decimal

MAXIMUM = 99999999
MINIMUM = -99999999
ERROR = 0.0000001
# total iteration
MAX_ITERATION = 10000


def powell(equation_str: str, vars_form: List[str], initial_point: List[float], interval: List[List[float]]):
    answer = ''
    equation = Equation(equation_str)
    var_count = len(vars_form)

    # check input type whether correct or not
    if (len(initial_point) == var_count == len(interval)) is False:
        Explosion.POWELL_LENGTH_INTERVAL_INITIAL_POINT_NOT_SAME_AS_INPUT_EQUATION.bang()
    for i in interval:
        if len(i) == 2 is False:
            Explosion.POWELL_LENGTH_INTERVAL_MUST_BE_ONLY_TWO.bang()

    X = Arrai(initial_point)
    every_point = [Arrai(initial_point).transpose()]
    S = Arrai.identity((var_count, var_count))

    # build dict
    vars_dict = build_var_dict(vars_form, X[0])
    # answer += ('First loop: f(%s)= %s\n\n' % (X[0], equation.eval_normal_form(vars_dict)))

    for i in range(MAX_ITERATION):
        # check break situation:
        # distance between X[i] and X[i-1] smaller than error value
        if i > 0:
            if Arrai.norm([Arrai(X[i]) - Arrai(X[i - 1])]) < ERROR:
                break

        P = Arrai(X[i])
        # save the value of alphas
        alphas = Arrai.zeros((1, var_count))

        for j in range(var_count):
            alpha_lb, alpha_ub = get_lb_ub(interval, P[j], S[j])
            alphas = alphas.set_col(j, Arrai(golden_section(equation, vars_form, alpha_lb, alpha_ub, P[j], S[j])))
            P.insert_row(Arrai(P[j]) + alphas[0][j] * Arrai(S[j]))

            vars_dict = build_var_dict(vars_form, P[j + 1])
            answer += ('i=%s\nj=%s\nalpha=%s\nf(%s)=%.4f\n\n' %
                       (i, j, alphas[0][j], Arrai(P[j + 1]), equation.eval_normal_form(vars_dict)))
            every_point.append(Arrai(P[j + 1]).transpose())

        # The new displacement vector(summation alphas[i]*S[i] from 0 to var_count-1) becomes a new search vector
        sn = Arrai(P[var_count]) - Arrai(P[0])
        X.insert_row(Arrai(P[var_count]))

        # get the index to replaced, index = argmax alphas[k]*||S[k]|| for all k
        value = Arrai.norm([Arrai(S[0])]) * alphas[0][0]
        index = 0
        for k in range(1, var_count):
            temp_value = Arrai.norm([Arrai(S[k])]) * alphas[0][k]
            if temp_value > value:
                index = k

        S.delete_row(index)
        S.insert_row(sn)
        answer += ('New S{%s}\n\n' % S)

    # answer += ('X Set = {%s}\n\n' % X)
    # build dict
    vars_dict = build_var_dict(vars_form, X[len(X)-1])
    answer += ('\n%s = %sf(%s)= %.6f\n\n' % (vars_form, Arrai(X[len(X)-1]), Arrai(X[len(X)-1]), equation.eval_normal_form(vars_dict)))
    return answer, every_point


# return the lower_bound and the upper_bound of the alpha
def get_lb_ub(interval: List[List[float]], pi: List[float], si: List[float]):
    total = len(interval)
    list_lower_bound = []
    list_upper_bound = []

    for k in range(total):
        if abs(si[k]) > 0.0000001:
            temp_low = Decimal(interval[k][0]) - pi[k]
            temp_low /= si[k]
            temp_high = Decimal(interval[k][1]) - pi[k]
            temp_high /= si[k]

            if si[k] < 0:
                temp_low, temp_high = temp_high, temp_low

            list_lower_bound.append(temp_low)
            list_upper_bound.append(temp_high)

    # no upper bound and lower found for alpha, return 0 instead
    if len(list_upper_bound) == 0 or len(list_lower_bound) == 0:
        return 0, 0

    lower_bound = list_lower_bound[0]
    upper_bound = list_upper_bound[0]
    for i in range(1, len(list_lower_bound)):
        if list_lower_bound[i] > lower_bound:
            lower_bound = list_lower_bound[i]

    for i in range(1, len(list_upper_bound)):
        if list_upper_bound[i] < upper_bound:
            upper_bound = list_upper_bound[i]

    return lower_bound, upper_bound


if __name__ == '__main__':
    # print('Q1: x^2+x-2*x^0.5')
    # answer1, X = powell(equation_str='x^2+x-2*x^0.5', vars_form=['x'], initial_point=[50.0], interval=[[0.0, 70.0]])
    # print(answer1)
    # print(X)
    # print('Q2: sin(3x)+cos(x)')
    # answer1, every_point1 = powell(equation_str='sin(3*x)+cos(x)', vars_form=['x'], initial_point=[1], interval=[[0.3, 3]])
    # print(answer1)
    # print(every_point1)
    print('Q3: 7 + x^2 - 3*x*y + 3.25*y^2 - 4*y')
    answer1, every_point1 = powell(equation_str='7+x^2-3*x*y+3.25*y^2-4*y', vars_form=['x', 'y'], initial_point=[50.0, 30.0], interval=[[-50, 70], [-70, 70]])
    print(answer1)
    # print(every_point1)
    # print('Q4: x^2+y^2')
    # answer1, every_point1 = powell(equation_str='x^2+y^2', vars_form=['x', 'y'], initial_point=[-50.0, 30.0], interval=[[-50, 70], [-70, 70]])
    # print(answer1)
    # print(every_point1)
    pass

