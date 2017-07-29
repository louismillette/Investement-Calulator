#!/usr/bin/env python
import math
'''
compoundInvestment.py
    A simple one file module for compound investment stratigies using vanilla python.  Using custom functions
    for the inflation, interest rates, and money added in a give period (as well as the period), comes up with
    an acurate estimate for total wealth accumulation.  Also has a reverse compund, given everything except periods
    but given end cash, says how much must time to accumulate this much cash.
'''

__author__ = "Louis Millette"
__copyright__ = "Copyright 2017, ME"
__credits__ = ["Louis_Millette"]
__license__ = "Use freely, credit me"
__version__ = "1.0.1"
__maintainer__ = "Louis Millette"
__email__ = "louismillette1@edu.uwaterloo.ca"
__status__ = "Production"

# compunds interest rate.  Returns list of compounded interest rate for all n periods
# product from i to n of IR(i) for all i from 1 to n.  O(n) time
def IRcompunder(alpha,fee,n):
    i = n
    IRs = []
    running = 1
    while i >= 1:
        running *= alpha(i) * fee(i)
        IRs.append(running)
        i -= 1
    return list(reversed(IRs))

'''
compund(A, alpha, infl, CGtaxes, dividends, divtaxes, fees, n,comma = True) -> <int>
    compund takes 2 functions of one parameter (A and alpha), and returns the total
    compund amount over 2 n periods. O(n) time.

    A:  A function that takes one argument, time, and gives back how much is entering the fund
        at the given time
    alpha: A function that takes one argument, time, and returns the interest rate for that
        time
    dividends:  A function that takes time, and returns the dividend yield percentage
    n:  The amount of time compounding (number of periods)
    infl:  A function that takes one argument, time, and gives back how much inflation is that period
    CGtaxes: the nominal tax rate on each contribution when removed
    divtaxes: tax rate on dividends earned in each period. function of period (n).

    All rates are to be given in the form of 1.06, for a rate of 6%.
    All dividends are to be given in the form of .06, for a dividend of 6% of the initial investement
    in the last year, it will not add money
'''

def compund(A, alpha, infl, CGtaxes, dividends, divtaxes, fees, n,comma = True):
    # product of interest rates(calculate in memory to keep runtime O(n))
    int_rep = int(n)+1
    poi = IRcompunder(alpha,fees,n)
    s = A(0)
    t = 0
    # contribution-interest accumulation
    for m in range(1,int_rep):
        # we aren't adding any money in at the end of the last period.
        if m == int_rep-1:
            div = dividends(m) * s * (2 - divtaxes(m))
            s = s*alpha(m)*fees(m) + div
        else:
            div = dividends(m) * s * (2 - divtaxes(m))
            s = (s * alpha(m) + div) * fees(m) + float(A(m))
    # tax calculations
    for m in range(0, int_rep-1):
        if (poi[m] - 1) < 0:
            #if you make capital losses, the goverment won't give you an "anti tax"
            continue
        else:
            # we won't tax dividends again.
            t += A(m)*(poi[m] - 1)*(CGtaxes(A(m), A(m)*poi[m-1], m)-1)
    # print('paid {:,} in Capital Gains'.format(round(t,2)))
    no_infl_total = round(s-t,2)
    infl_t = 1
    for m in range(1, int_rep):
        infl_t *= infl(m)
    total = round(no_infl_total / infl_t,2)
    if comma == True:
        return "{:,}".format(total)
    return total

'''
reverse_compund(A,alpha,infl,target) -> <int>
    compund takes 3 functions of one parameter (A alpha, and infl), and a target amount.
    It returns the number of years it will take to reach that target

    A:  A function that takes one argument, time, and gives back how much is entering the fund
        at this time
    alpha: A function that takes one argument, time, and returns the interest rate for that
        time
    target: the amount of money desired

    infl:  A function that takes one argument, time, and gives back how much inflation is that period
'''
def reverse_compund(A,alpha,infl, CGtaxes, fees,target):
    lower = 0.0
    upper = 250.0
    while 1:
        guess = round((lower+upper)/2,15)
        guess_result = round(compund(A = A, alpha=alpha,infl = infl, CGtaxes=CGtaxes, fees=fees, n = guess, comma=False),5)
        if abs(guess_result - target) < .0001 or upper - lower < .00000000001:
            return round(guess,3)
        else:
            if guess_result > target:
                upper = guess
            elif guess_result < target:
                lower = guess
            else:
                return round(guess,3)


'''
Examples
v = compund(A = contribution, alpha = IR, n=45, infl = infl)
print(v)
val = reverse_compund(A = contribution, alpha = IR, target=5000000, infl = infl)
print(val)
'''
if __name__ == '__main__':
    def contribution(n):
        if n == 0:
            return 100000
        else:
            return 0
            # return 5000 * (1.02 ** n)

    def IRnew(n):
        if n < 11:
            return 1.04 + 4 * math.sin(n) / 100
        else:
            return 1.065 + 4 * math.sin(n) / 100

    def IRold(n):
        return 1.10 + 5 * math.sin(n) / 100

    def infl(n):
        return 1.02

    # capital gains taxes
    # percent taxed on each contribution gains when sold (ALWAYS nominal) (assumes selling period at end of n periods)
    # s = initial amount, e = end amount, n = spaciofic period
    def CGtaxes(s, e, n):
        return 1.15

    def rothIRA(s, e, n):
        return 1

    # dividends returned
    def divs(n):
        return .03
    # rate at which dividends are taxed
    def divtaxes(n):
        return 1.15
    # Fees paid in each period.  This is calculated at returned percent times the current
    # value of investements (as calculated for an ETF of index fund).  Generally, a flat rate.
    def fees(n):
        return 1 - .0077
    v = compund(A = contribution, alpha = IRnew, CGtaxes=CGtaxes, fees=fees, n=40, infl = infl, dividends=divs, divtaxes=divtaxes)
    #vOld = reverse_compund(A = contribution, alpha = IRold, CGtaxes=CGtaxes, fees=fees, infl = infl, target=1000000)
    #vNew = reverse_compund(A=contribution, alpha=IRnew, CGtaxes=CGtaxes, fees=fees, infl=infl, target=1000000)
    #print(vOld)
    #print(vNew)
    print(v)