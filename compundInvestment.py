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
__version__ = "1.0.2"
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
    all_taxes,all_fees, div_acc, infl_so_far, contributions = 0,0,[0],1,0
    # contribution-interest accumulation
    m,taxable_gains = 0,0
    while m < int_rep:
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
            s = (s * alpha(m) + div - divtax) * fees(m) + float(A(m+1))*infl_so_far  # fees applied after div tax (assumption)
            all_taxes += divtax / infl_so_far
            all_fees += (s * alpha(m) + div - divtax) * (1 - fees(m)) / infl_so_far
            div_acc.append(div - divtax) # we'll pay CG taxes on div reinvestement
        # we won't tax dividends again.
        contributions += float(A(m + 1)) # we're adding the same amount in base year dollars every year
        taxable_gains += (float(A(m+1))*infl_so_far + div_acc[m]) * (poi[m] - 1)
        m += 1
    # tax calculations (CG tax, div tax already accounted for)
    CGtax = taxable_gains * (CGtaxes(taxable_gains, multiplier=1/infl_so_far)-1)
    CGtax = CGtax if CGtax > 0 else 0
    # print("Paid {} total in capital gains taxes".format(CGtax))
    all_taxes += CGtax/infl_so_far
    # print('paid {:,} in Capital Gains'.format(round(CGtax,2)))
    no_infl_total = round(s - CGtax, 2)
    total = round(no_infl_total / infl_so_far, 2)
    contributions = round(contributions, 2)
    if comma == True:
        return "{:,}".format(total)
    return total,all_taxes,all_fees, contributions

'''
annuity(A, alpha, infl, CGtaxes, dividends, divtaxes, fees, n,comma = True) -> <int>
    P:  An int, the amount (in base year dollars) to be withdrawn each year.
    alpha: A function that takes one argument, time, and returns the interest rate for that
        time
    dividends:  A function that takes time, and returns the dividend yield percentage
    n:  The amount of time compounding (number of periods)
    infl:  A function that takes one argument, time, and gives back how much inflation is that period
    CGtaxes: the nominal tax rate on each contribution (to be given in base year dollars) when removed
    divtaxes: tax rate on dividends earned in each period. function of period (n), optional argument t:
              total dividends being paid on, and optional argument inn: amount of other income in this period
    fees: function that takes time, and returns fee percent in that period.
    inflMultiplier: (list of int) product of inflations up to the length of the list for each point in the list.
                    first will be I1 2nd with be I1*I2, and last will be I1*I2*...*In.
    alphaMultiplier: (list of int) product of returns up to the length of the list for each point in the list.
                first will be a1 2nd with be a1*a2, and last will be a1*a2*...*an.

    - All rates are to be given in the form of 1.06, for a rate of 6%.
    - Starts removing amount yearly, starting after first appreciation and dividend payment.
    - Money removed in each period is adjusted for inflation.  That is, the calculator will assume that
      in the last period, your taking out what you took out in the first period, adjusted for n years of inflation.
    - Anuity is a class instead of a function becuase of the number of moving parts and helpers.  The init, however,
      acts as a function, executing appropriate functions internally and setting the result
'''
class Annuity():
    def __init__(self, P, alpha, dividends, n, infl, CGtaxes, divtaxes):
        # create class variables
        self.alhpa = alpha
        self.dividends = dividends
        self.n = n
        self.infl = infl
        self.CGtaxes = CGtaxes
        self.divtaxes = divtaxes
        # generate psi/phi
        self.psi = [1]
        self.phi = [1]
        for i in range(1,n+1):
            self.psi.append(self.psi[i-1]*alpha[i])
        for i in range(1,n+1):
            self.phi.append(self.phi[i-1]*infl[i])
        # generate A, the amount to take out every time before inflation
        self.A = P
        for i in range(20):
            # 20 is arbitrary, simply a measure of accuracy
            self.A = P + CGtaxes(self.A)
        # Generate C, the RHS of the equation
        self.C = self.calcConst(self.A, self.phi, self.psi, n)

    # calculates the constant of the equation (RHS), that wont change.
    # we'll try to make the LHS match it
    def calcConst(self, A, phi, psi, n):
        c = sum([A*phi[i]/psi[i] for i in range(1,n+1)])
        return c

    # takes ANR (our guess at the present vvalue of the anuity) and spits out LHS of the equation
    # ANR is perfect guess if it equals C exactly
    def calcGuess(self,ANR, alpha, phi, psi, A, n, dividends, fees, divtaxes):
        S = 0
        f = [0]
        d = [0]
        B = [alpha[1]*ANR]
        for i in range(1,n+1):
            B.append(alpha(i)*(B[i-1]-A*phi[i-1]-f[i-1]+d[i-1]))
            f.append(fees(i)*B[i])
            d.append(B[i]*dividends(i)-divtaxes(B[i]*dividends(i)/phi[i])*phi[i])
            S += (f[i]-d[i])/psi[i]
        return S
    # finds good solution in log time, returns that solution
    # we'll take advantage of the strictly increaseing nature of the LHS function
    # our guess's will take O(nlogm) for m "level of percision"
    def gen_annuity(self):
        lowInitial = .01 # a reasonable lowest guess of the anuitys value
        highInitial = self.A * self.n * 10 # 10 times how much we're taking out.  Very high.
        lowGuess = self.calcGuess(lowInitial, self.alhpa, self.phi, self.psi, self.A, self.n, self.dividends, self.fees, self.divtaxes)
        highGuess = self.calcGuess(highInitial, self.alhpa, self.phi, self.psi, self.A, self.n, self.dividends, self.fees, self.divtaxes)
        while 1:
            newInitial = (highInitial + lowInitial)/2
            newGuess = self.calcGuess(newInitial, self.alhpa, self.phi, self.psi, self.A, self.n, self.dividends, self.fees, self.divtaxes)
            if abs(newGuess-highGuess) > abs(newGuess-lowGuess):
                highInitial = newInitial
            else:
                lowInitial = newInitial
            # precision down to 1/1000 of a cent.  We can change this precision to improve performance
            print(newGuess-self.C)
            if newGuess - self.C < .00001:
                return newGuess


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