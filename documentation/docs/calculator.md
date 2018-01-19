# Compound Calculator

The project consists of the original calculator, and the S and P 500 application of it.
This page covers the application of the original investment calculator.

---
**NOTE**

For the code, go to <a href="https://github.com/louismillette/Investement-Calulator/tree/master">here</a>

---

## Basic Usage

The compound calculator, in compoundinvestement.py runs on python 3.4 but has no dependencies.

The compound function takes 8 arguments, and 1 optional argument:

compund(A, alpha, infl, CGtaxes, dividends, divtaxes, fees, n,comma = True):

* `A:  A function that takes one argument, the nth period, and gives back how much is entering the fund
    at the given period`

* `alpha: A function that takes one argument, period n, and returns the interest rate at the given period`

* `dividends:  A function that takes the period, n, and returns the dividend yield percentage; as in the 
               percentage of the total investment that is received in dividends`

* `n:  The amount of time compounding (number of periods)`

* `infl:  A function that takes one argument, n, and gives back how much inflation is that period`

* `CGtaxes: A function that takes 3 required arguments:`
	* `s: The amount initially invested`
	* `e: The amount worth at the end`
	* `n: the current period`
	`return the capital gains tax on that investment, in that particular period`

* `divtaxes: A function that takes one argument, n, and returns the dividend taxes in the period`

* `comma(optional): if True, the returned number will be comma delimited
All rates are to be given in the form of 1.06, for a rate of 6%.<br>
All dividends are to be given in the form of .06, for a dividend of 6% of the initial investment<br>
in the last year, no money is added, the money already compounding will continue to compound.<br>
## Example
	def contribution(n):
        if n == 0:
            return 100000
        else:
            return 0
            # return 5000 * (1.02 ** n)
    def IR(n):
        if n < 11:
            return 1.04 + 4 * math.sin(n) / 100
        else:
            return 1.065 + 4 * math.sin(n) / 100
    def infl(n):
        return 1.02
    # capital gains taxes
    # percent taxed on each contribution gains when sold (ALWAYS nominal) (assumes selling period at end of n periods)
    # s = initial amount, e = end amount, n = specific period
    def CGtaxes(s, e, n):
        return 1.15
    # dividends returned
    def divs(n):
        return .03
    # rate at which dividends are taxed
    def divtaxes(n):
        return 1.15
    # Fees paid in each period.  This is calculated at returned percent times the current
    # value of investments (as calculated for an ETF of index fund).  Generally, a flat rate.
    def fees(n):
        return 1 - .0077
    # Leaving comma=true, to return value formatted
    v = compund(A = contribution, alpha = IR, CGtaxes=CGtaxes, fees=fees, n=40, infl = infl, dividends=divs, divtaxes=divtaxes)
    print(v)
    # will return 848,004.78
