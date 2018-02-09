# Home Made Annuity

The Home-Made Annuity is what I call an annuity made from another investment.  For example, investing a lump sum of money into the S and P 500 and pulling out $X every year.  The question I aim to answer is exactly how much should be deposited initially, given outflows of $X for n years, which is the present value of this annuity.

## Simplifying Assumptions

This model makes the following assumptions:

* The money received each year from the annuity is adjusted for inflation, but constant in base year dollars. 
* The present value of the annuity is positive
* The cash flows out are positive

This model uses the following variable definitions:

* \( \alpha_{i} \) is the return or interest in period i
* \( I_{i} \) is the inflation in period i
* \( d_{i} \) is the dividend payment in period i, after taxes (in dollars)
* \( f_{i} \) is the fee payment at period i ( in dollars)
* \( a_{n} \) is the present value of the annuity for n periods
* \( P \) is the money required out of the fund, in base year dollars, every year
* \( A \) is the money required out of the fund after accounting for taxes, in base year dollars, every year

Let \( \phi_{i} \) = \( \prod_{j=1}^{i}I_{j} \) and \( \psi_{i} \) = \( \prod_{j=1}^{i}\alpha_{j} \)

## General Model

The basic definition of the present value of an annuity: 

$$ a_{n,r} = \frac{1-(1+r)^{-n}}{r} $$

where n is the number of periods, and r is the rate (6% => r = 0.06).  This model is the closed form of the sum of annuity payments discounted at rate r in each period; however, it won't be needed.  The model takes into consideration the additional variates mentioned above.

The objective is to find out the amount that is needed to invest today, to pull out $X, adjusted for inflation, each year for n years.  Let \( s_{i} \) represent the annuity's value at period i, the initial investment, in 2 years, will be equal to:

$$ s_{0} = a_{2} $$
$$ s_{1} = a_{2} \cdot \alpha_{1} + d_{1} - f_{1} - A \cdot I_{1} $$ 
$$ s_{2} = (a_{2} \cdot \alpha_{1} + d_{1} - f_{1} - A \cdot I_{1}) \cdot \alpha_{2} + d_{2} - f_{2} - A \cdot I_{1} \cdot I_{2} $$

This starts to get nasty quickly.  What’s happening is that every year the fund appreciates by value \( \alpha_{i} \), \( d_{i} \) dividends enter the fund, \( f_{i} \) feed leave the fund, and A \( \cdot \) (some inflation) is withdrawn.  For this model the end value must equal 0, so that only what is required to make the yearly withdrawals is deposited in the beginning.  After doing this, the above formula can be solved in a more general sense to get an expression for \( a_{2} \).

$$ s_{2} = (a_{2} \cdot \alpha_{1} + d_{1} - f_{1} - A \cdot I_{1}) \cdot \alpha_{2} + d_{2} - f_{2} - A \cdot I_{1} \cdot I_{2} = 0 $$
$$ \implies a_{2} \cdot \alpha_{1} \cdot \alpha_{2} + d_{1} \cdot \alpha_{2} - f_{1} \cdot \alpha_{2} - A \cdot I_{1} \cdot \alpha_{2} + d_{2} - f_{2} - A \cdot I_{1} \cdot I_{2} = 0 $$
$$ \implies a_{2} \cdot \alpha_{1} \cdot \alpha_{2} = A \cdot I_{1} \cdot I_{2} + f_{2} - d_{2} + A \cdot I_{1} \cdot \alpha_{2} + f_{1} \cdot \alpha_{2} - d_{1} \cdot \alpha_{2} $$

$$ \implies a_{2} = \frac{A \cdot I_{1} \cdot I_{2} + f_{2} - d_{2}}{\alpha_{1} \cdot \alpha_{2}} + \frac{ A \cdot I_{1} + f_{1} - d_{1} }{\alpha_{1}} = \frac{A \cdot \phi_{2} + f_{2} - d_{2}}{\psi_{2}} + \frac{ A \cdot \phi_{1} + f_{1} - d_{1} }{\psi_{1}} $$
$$ = \sum_{i=1}^{2} {\frac{A \cdot \phi_{i} + f_{i} - d_{i}}{\psi_{i}}} $$

For the 2-period scenario, this is a nice compact solution in the form of a sum.  What about the n period scenario?  A rigorous proof by mathematical induction would suffice, but I thought about it for a while and the n period sum makes sense logically, so I'll leave it as a proof by observations that

$$ a_{n} = \sum_{i=1}^{n} {\frac{A \cdot \phi_{i} + f_{i} - d_{i}}{\psi_{i}}} $$

Not bad.  This looks strikingly similar to the original Present Value of an annuity formula, this one cannot be made compact as all rates are variable and change in this model (like they do in real life).  But there is still the problem of \( d_{i} and f_{i} \); recall that these numbers rely on the balance of the annuity lump sum in period i.  That is, they rely indirectly on \( a_{n} \).  This means there is no direct solution to the problem (or at least not one worth trying to derive, if it exists, it’s REALLY nasty), only a function of the solution that equals some constant.

## Dividends and Fees

How exactly is \( d_{i} \) defined?  Recall that it is the amount of money deposited in dividends at period i, not the percent return.  This number is unknown!  The dividend yield as a percent of the amount that is currently invested is, however, know.  The dividends cannot be taken out as a percent return in period i in the model because taxes must be paid on them before re-investing, so they are defined to be cash payments.  They also cannot be applied like the value A because they change in each period and are directly proportional how much money is currently in the fund.  The model fee's  \( f_{i}\)'s  are treated the same way, although the investor does not pay taxes on them.  It may be possible to view them more like the \( \alpha \)'s, but as the math unfolds, it will become clear that this adds no run time to the model.  For my own convenience, if I were to build the model as the vendor of the annuity, this model makes it easy to shift the tax burden to the fee's collected.

To find \( d_{i} \), \( B_{i} \) must first be derived, the balance of the annuity in the bank at period i.  To define that, the dividends in the prior period and the fees in the prior period are first required.  Assuming that \( D_{i} \): the dividend yield in period i and \( F_{i}\): the fee percent in period i are know:

$$ d_{i} = B_{i} \cdot D_{i} - t(\frac{B_{i} \cdot D_{i}}{\phi_{i}}) \cdot \phi_{i} $$
$$ f_{i} = B_{i} \cdot F_{i} $$
$$ B_{i} = (B_{i-1} - A \cdot \phi_{i-1} - f_{i-1} + d_{i-1}) \cdot \alpha_{i} $$
$$ B_{1} = \alpha_{1} \cdot a_{n} $$

## Tax Function

Taxes, in the real world, are progressively calculated by tax brackets, and the tax function t() reflects this.  The bracket function is a non-differentiable, not continuous, strictly increasing step function.  The tax function takes dollars in the base year and returns the amount of dollars that would be paid in federal and state capital gains tax.  The dollar amount input has to be deflated to the base year, and the tax amount returned has to be inflated to the \( i^{th} \) year when returned.  

A vs P:  P is defined as the amount desired each year, and A as the actual amount that must be pulled out of the fund to make that happen (both in base year dollars).  So how is A defined in a formula?  

$$ A = P + t(P) $$

Looks good.  Although, while taxes have been accounted for, tax on the taxes has not! If A is defined as above, less then P dollars will be returned.  The real formula is 

$$ A = P + t(P + t(P)) $$

Awesome problem solved.  Although ... now the tax on the tax increase that is being pulled out is increasing the tax, requiring more to be pulled out, to truly receive P dollars each year!  This will recurs infinitely, more, but a decreasing amount, of money will have to be pulled out of the fund to account for this difference; an approximation of A will have to suffice.

$$ A = P + t(P + t(P + ...)) \approx  P + t(P + t(P + t(P + t(P + T(P))))) $$

Probably, accuracy around a tenth or hundreth of a cent is good enough.

## Concise Model

With all the pieces in place, the exact form of the model comes into focus.  Recall the general formula for the value of the annuity:

$$ a_{n} = \sum_{i=1}^{n} {\frac{A \cdot \phi_{i} + f_{i} - d_{i}}{\psi_{i}}} $$
$$ \implies a_{n} - \sum_{i=1}^{n} {\frac{f_{i} - d_{i}}{\psi_{i}}} = \sum_{i=1}^{n} {\frac{A \cdot \phi_{i}}{\psi_{i}}} $$

Let \( \Phi(a_{n}) = a_{n} - \sum_{i=1}^{n} {\frac{f_{i} - d_{i}}{\psi_{i}}}\); this is the function of the solution, and the RHS of the equation above \( \sum_{i=1}^{n} {\frac{A \cdot \phi_{i}}{\psi_{i}}} \) will remain constant with respect to the solution; so it can be calculated once and then let equal C.  The new formula to solve is

$$ \Phi(a_{n}) = C $$

Instead of trying to solve it explicitly, because of the complexity, the proper \( a_{n} \) may be found with logarithmic convergence using a (kind of)Newtonian algorithm for guessing the solution.  This is possible because \( a_{n} \) is strictly positive and our objective function \( \Phi(a_{n}) \) is strictly increasing.

I've written out the general form of the solution algorithm in sudo-python.

## Algorithm

```
# first, calculate phi and psi (doable in o(n) time for number of periods), hold on to them
# next calculate C with this function, hold on to it as well.
def function1:
    C = 0
    for i in range(1,n+1):
        C += (A * phi[i])/psi[i]
    return C

# for our best guess, a_n
def function2:
    S2 = 0
    f = [0]
    d = [0]
    B = [alpha_1 * a_n]
    for i in range(1,n+1):
        B[i] = alpha[i]*(B[i-1] - A*phi[i-1] - f[i-1] + d[i-1])
        f[i] = B[i] * F[i]
        d[i] = B[i] * D[i] - t(B[i]*D[i]/phi[i])*phi[i]
        S2 += (f[i]-d[i])/psi[i]
    return S2

# make guesses until we get it right, narrow down choices logarithmically.
def function3:
    lowInitial = .01 # a reasonable lowest guess of the anuitys value
    highInitial = A * n * 10 # 10 times how much we're taking out.  Very high.
    lowGuess = function2(lowInitial)
    highGuess = function2(highInitial)
    while 1:
        newInitial = (highInitial + lowInitial)/2
        newGuess = function2(newInitial)
        if abs(newGuess-highGuess) > abs(newGuess-lowGuess):
            highInitial = newInitial
        else:
            lowInitial = newInitial
        # precision down to 1/1000 of a cent.  We can change this precision to improve performance
        if newGuess - C < .00001:
            return newGuess
```

# The Quick and Easy Way

Wow math sucks a lot.  This is a cool formula, but it's abstract; I certainly don't have a real world interpretation of the constant C nor the function \( \Phi(a_{n}) \).  After thinking about it, I decided there's a much simpler way to do this.  The function used to logarithmically pick a good solution to the LHS of the equation above can be repurposed to find the root of a recursively defined function that finds the value of the annuity at time i.  This is the same function from the general model:

$$ s_{2} = (a_{2} \cdot \alpha_{1} + d_{1} - f_{1} - A \cdot I_{1}) \cdot \alpha_{2} + d_{2} - f_{2} - A \cdot I_{1} \cdot I_{2} $$

Except re-defined recursively for period i:

$$ s_{i} = \alpha_{i} \cdot s_{i-1} + d_{i} - f_{i} - A_{i} \cdot \phi_{i} $$

\( \psi \) is no longer needed.  When the true value of the annuity is correct, \( s_{n} = 0 \) will hold.  Let this new recursively defined objective function of \( a_{n} \) be known as \( f(a_{n}) \).  Fortunately, f() is strictly increasing; the more one invests the more they receive (always true, unless somehow an investment was so bad it put its shareholders in debt). Guessing the \( a_{n} \) that satisfies this is just as easy as finding the \( a_{n} \) thats satisfies \( \Phi(a_{n}) = C \).

