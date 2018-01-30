# Reverse Engineering Mutual Funds 

Mutual Funds provided by banks and financial institutions like this one https://www.cibc.com/en/personal-banking/investments/mutual-funds/growth-funds/balanced-fund.html can be a bit misleading.  Instead of providing how much the fund grew in each year, they'll provide average compound returns for a handful of years.  In order to compare them to index funds that provide clearer information, one must parse out the information

When you see something like "the 5-year compounded average is 5.7%" what is really being said is 
$$ \frac{\prod_{i=1}^{5}(1 + r_{i}) - 1}{5} = 0.057 $$

where \( r_{i} \) is the return in period i.  When multiple such expressions are given, multiple formulas must be satisfied simultaneously, giving us a good base to estimate what the missing returns might be.  For, say, a 30-year mutual fund with compounding averages given for 1,5,10, and 30 years, these formulas look like this:
$$ r_{30} = \phi_{1} $$
$$ r_{25} \cdot r_{26} \cdot r_{27} \cdot r_{28} \cdot r_{29} \cdot r_{30} = 5 \cdot \phi_{5} + 1  $$ 
$$ r_{20} \cdot r_{21} \cdot ... \cdot r_{30} = 10 \cdot \phi_{10} + 1  $$
$$ r_{1} \cdot r_{2} \cdot ... \cdot r_{30} = 30 \cdot \phi_{30} + 1  $$

Here, the phi's are the average compound rates given by the fund.  In this scenario, each equation can be solved in the simplest way possible by assuming all previously undefined rates are the same.  For our mutual funds, this is as good a guess as any that satisfy the equations.  For the rest of this doc, I’ll refer to \( r_{i} \) instead of \( 1 + r_{i} \) to make it clearer.  For each equation of the n most recent returns, d the set of already defined rates, and u the set of undefined rates:

$$ \frac{n \cdot \phi_{n} + 1}{\prod_{\forall d}r_{i}} = \prod_{\forall u} r_{j} \space\space where \space\space r_{i} = r_{j} \space \forall i,j \space in \space u $$
$$let \space\space \gamma = \frac{n \cdot \phi_{n} + 1}{\prod_{\forall d}r_{i}}$$
$$ r_{j} =  \sqrt[u]{\gamma} $$

Where that last root is the uth root of gamma (really the size of u).  So, for each equation we must work with, we can reverse engineer rates between each period of years given by the financial institution.  In python:


```
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
        rate = round(m**(1/(len(unass_dates))),7)
        for date in unass_dates:
            returns[date] = rate
    retFormat = []
    for k,v in returns.items():
        retFormat.append({"Date":k + '-12-01', "Return Percent":v-1, "Dividend Yield": 0})
    return retFormat
```
