#!/usr/bin/env python
import math
from functools import reduce
import operator
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

'''
compunds interest rate.  Returns list of compounded interest rate for all n periods
product from i to n of IR(i) for all i from 1 to n.  O(n) time
'''
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
    A:  A function that takes one argument, time, and gives back how much is entering the fund
        at the given time
    alpha: A function that takes one argument, time, and returns the interest rate for that
        time
    dividends:  A function that takes time, and returns the dividend yield percentage
    n:  The amount of time compounding (number of periods)
    infl:  A function that takes one argument, time, and gives back how much inflation is that period
    CGtaxes: the nominal tax rate on each contribution when removed
    divtaxes: tax rate on dividends earned in each period. function of period (n), optional argument t:
              total dividends being paid on, and optional argument inn: amount of other income in this period
    inflMultiplier: inflation multiplier for calculating taxes:  list that contains, for each compounding period,
                    how much money in that period is worth in todays terms (today being the last entry of inflation
                    in the inflation csv)

    All rates are to be given in the form of 1.06, for a rate of 6%.
    In the last year, it will not add money.
    Compounds from beggining of given year through end of last year given. A will be indexed one level higher then
    the rest of the functions, everything is compounded between money inputs into the fund.
    Money (A) is put in as if it were in todays CPI, and the inflation and interest rates from whatever time period are applied
    to it, accounting for inflation that occurs over the time period.
'''
def compund(A, alpha, infl, CGtaxes, dividends, divtaxes, fees, n, comma=True):

    # product of interest rates(calculate in memory to keep runtime O(n))
    int_rep = int(n)
    poi = IRcompunder(alpha, fees, n)
    s = A(0)
    all_taxes,all_fees, div_acc, infl_so_far = 0,0,[0],1
    # contribution-interest accumulation
    for m in range(0, int_rep):
        # this is so we can actively regress our true tax payment brackets back to the base year
        # we are not accounting for inflaion here per period, we are only useing this to account for tax brackets adjusting to inflation
        infl_so_far *= infl(m)
        # we aren't adding any money in at the end of the last period.
        # dividend taxes are paid as they are recieved
        if m == int_rep-1:
            div = dividends(m) * float(s)
            divtax = div * (divtaxes(m, t=div, multiplier=1/infl_so_far) - 1)
            s = (s * alpha(m) + div - divtax) * fees(m)
            all_taxes += divtax / infl_so_far
            all_fees += s * alpha(m) * (1 - fees(m)) / infl_so_far

        else:
            div = dividends(m) * s
            divtax = div * (divtaxes(m, t=div, multiplier=1/infl_so_far) - 1)
            s = (s * alpha(m) + div - divtax) * fees(m) + float(A(m+1))  # fees applied after div tax (assumption)
            all_taxes += divtax / infl_so_far
            all_fees += (s * alpha(m) + div - divtax) * (1 - fees(m)) / infl_so_far
            div_acc.append(div - divtax) # we'll pay CG taxes on div reinvestement
    # tax calculations (CG tax, div tax already accounted for)
    taxable_gains = 0
    for m in range(0, int_rep):
        # we won't tax dividends again.
        taxable_gains += (A(m)+div_acc[m]) * (poi[m] - 1)
    CGtax = taxable_gains * (CGtaxes(taxable_gains, multiplier=1/infl_so_far)-1)
    # print("Paid {} total in capital gains taxes".format(CGtax))
    all_taxes += CGtax/infl_so_far
    # print('paid {:,} in Capital Gains'.format(round(CGtax,2)))
    no_infl_total = round(s - CGtax, 2)
    infl_t = 1
    for m in range(0, int_rep-1):
        infl_t *= infl(m)
    total = round(no_infl_total / infl_t, 2)
    if comma == True:
        return "{:,}".format(total)
    return total,all_taxes,all_fees

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
buildFund takes average yearly compounded rates, and fills in missing years, returning a "best guess" as
to what the returns look like.
Fundreturns: <dict> {1987:.059, 2017:.07, ...} keys are the year-to-present average compound returns
         if the last year returns were 7%, it would be key:value of 2017:.07
returns: list of dict: [{"Date":1970-07-20, "Relevent Returns":.05},...]
'''
def buildFund(Fundreturns):
    dates = list(reversed(sorted(Fundreturns.keys())))
    leng = int(dates[0]) - int(dates[-1]) + 1
    keys = [str(ele) for ele in range(int(dates[-1]), int(dates[0]) + 1)]
    returns = dict(zip(keys,[1 for _ in range(leng)]))
    returns[dates[0]] = Fundreturns[dates[0]]
    i = 0
    while i < len(dates):
        i += 1
        try:
            dates[i]
        except:
            break
        compounding = list(range(int(dates[i]), int(dates[0]) + 1))
        ret =  {k: v for k, v in returns.items() if int(k) in compounding} # dict of our compounding dates
        phi =  {k: v for k, v in ret.items() if v != 1} # dict of dates already processed by earlier compounding averages
        unass_dates = [k for k, v in ret.items() if v == 1]
        num = len(compounding) * (Fundreturns[dates[i]] - 1) + 1
        denom = reduce(operator.mul, phi.values())
        m = num/denom
        rate = m**(1/(len(unass_dates)))
        for date in unass_dates:
            returns[date] = rate
    retFormat = []
    for k,v in returns.items():
        retFormat.append({"Date":k + '-01-01', "Relevent Returns":v-1})
    return retFormat


'''
Examples
v = compund(A = contribution, alpha = IR, n=45, infl = infl)
print(v)
val = reverse_compund(A = contribution, alpha = IR, target=5000000, infl = infl)
print(val)
'''
if __name__ == '__main__':
    print(buildFund({'2015':1.035, '2016':1.052, '2017':1.058, '2014':1.045, '2013':1.057, '2008':1.03, '1988':1.059}))