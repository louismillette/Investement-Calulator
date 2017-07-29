# Index Fund Application

The index fund application is a python module for the purpose of graphing the S and P 500, and various data visualizations it.<br>
The code is built on the SciPy statistics python stack; python 3.4, SciPy, NumPy, anaconda for the package manager, and plotly for the graphs.<br>


---
**NOTE**

None of this will work unless all applicable packages have been downloaded, and a plotly account is created; plotly credentials must be then hard coded into the __init__ of the plot graph.  SciPy is a great package but requires the anaconda package manager to work.

---

---
**NOTE**

For the code, go to https://github.com/louismillette/Investement-Calulator/tree/master

---

## Loading Data

The Data class loads in all the data.  Creating a data class instance loads all the data for the remainder of the project, minimizing run time by requiring just one call for multiple uses.  Surprisingly (or maybe not so much) loading the data into python takes the second longest time of all analysis functions and graphing.  The data instance loads in 5 sources of data with 4 different methods:

* `loadSandP(self)`:  loads the s and p 500 data from SandP.csv.  the data must have the same name and format of the SandP.csv file.  Returns a dictionary of date, return % values.
					  Return percent is formatted number, like 2.15 for 2.15% return that year.

* `loadInflation(self)`:  loads the inflation data from inflation.csv.  Same format as the S and P data

* `loadGold(self)`:  loads the gold data from gold.csv.  Same format as the S and P data

* `loadSafe(self)`:  loads the 10 year T bill data from safe.csv.  Same format as the S and P data

For the data to load properly, each csv must be named properly (as denoted above) and be in the same directory as the SandP.py file.<br>
generate(self, n=40, to=None, frm= None)<br>
takes in python datetime object arguments to and frm, generate picks a n year span, returns inflation, s and p growth, dividends, bond, and tbill prices for each year in the given span.
The format returned looks like this:
```
   [ { 'year':year, 'inflation':inflation', 'interest':interest, 'dividend':dividend}, ...]
```
after a couple speed hacks, it runs in O(nlogn) time.  Only works if there aren't holes in the data.

## Plotting with Plotly

All the plotting is done through the Plot class, using plotly.  However, plotly is a (free) service, and usage requires a user API key.  I have removed mine for my own security, but left a comment in the init of the Plot class where, if you are so inclined, you may put your key to make the code work.
Plotly can generate plots offline or online, so I have provided a class variable, online to set weather or not the graphs are generated to plotly’s online workspace or locally.
The following methods are ones I used to make all my charts, they act as wrappers around the plottly API that I can feed regular python data to.

### Simple Line Plot

```
# takes data in list of lists:
# [[x1,y1], ... , [xn,yn]]
LinePlotSimple(self,data,title,xaxis,yaxis, filename="basic-line")
```
Takes a list of [x,y] values, plots them.  requires x and y axis names and a title.

### Multi Line Plot

```
# takes multiple series of data (in same chart).  X data is a list of x values. y data series is
# [{'data':[y11, ..., y1n], 'mode': mode1, 'name': series name 1}, .. , {'data':[ym1, ..., ymn], 'mode': mode m, 'name': series name m}]
# modes: lines, or lines + markers, or markers.
LinePlot(self, x, y, title, xaxis, yaxis, filename="multi-series-lines"):
```
Generates a more complicated line plot, one with multiple series (but the same x values).<br>
x is a simple list of x values and y is a list of dictionaries with each data series.<br>

### Line Plot Interval
```
LinePlotInterval(self, y, yreg=None, title="Chart Title", xaxis="X-Axis", yaxis="Y-Axis", filename="Linechart-range.html")
```
Line plot interval plots a line plot (or multiple line plots) with or without an interval around them.  That is, a shaded region around the line provided, that is defined by a list of x and y coordinates.  y in this case is a list of data series, which are structured below:
```
{
    'x': list of x values,
    'upper': list of upper y values,
    'lower': list of lower y values,
    'data': list of y values,
    'name': 'Safe+Index',
    'fillcolor': 'rgba(255,0,0,.4)', # shaded region color
    'color': 'rgb(0,0,0)' # data line color
}
```
yreg is a list of data series that do not have a range (but also appear on the graph), and they are to be formatted like the data series in the multi line plot.

### Heat Map

```
# colormap is list of values and what color they should be.  For instance
# [.5,[[0,1], hexcolor1], ... ,[[7,'+'], hexcolor1]]]. 
def heatmap(self,x,y,z,colormap=None, title='Title', ticks='Ticks',xaxis='Xlab', yaxis='Ylab', filename='heatmap.html')
```

The x,y, and z data are each basic python lists, of equal length.  The Heatmap produced will take an i for 0 - length-of-lists, and for each i graph the corresponding x[i],y[i] with heat value z[i].  In other words, for a 10 by 10 grid, each x, y, and z list should be of length 100.<br>
If the colormap is left at none, plotly with take its best guess as to how you want the "heat" of the map to be represented ( the color of the squares).  Usually, it looks nice, however, if you want specific colors for specific data, you'll need the colormap.  Specifically, if you want all data points with z values between 5 and 10 to be red, add [[5,10], 'red'] to the colormap.  Don't forget to define a color definition for all ranges of data, if you choose to use the colormap.

### Histogram

```
# takes list of data points, produces histogram.  Also fits an exp distr., if exp=True
Histogram(self,data, title="No Title", xaxis="No Title", yaxis="No Title", filename="Histogram", exp=False)
```
The simplest graph: just give it a list of data points, and it spits out a histogram.  It fits a gamma distribution (within the exp family, easiest for SciPy to fit) using SciPy and NumPy, if exp=True

## Multiplier Heat Map

The Multiplier function, floating freely outside a class in the module, is the meat of this module.  It Produces a heatmap of multipliers, comparing date of entry vs date of exit for each year in the data.  The multipliers are how many times your initial investment you'll get back

### Basic Usage

```
# here we make a heat map of the multiplier of your money given the data provided, based on the
# state, income bracket, and fee provided
Multiplier(data, state, incomebracket, fee=None, title=None)
```

* data: the same data produced by a call to the generate() method of the data class.  It is built for use by this data, but does not require it.  Other data that is similarly formatted may also be use.

* state: only takes 'Texas' or 'California', as they are the 2 ends of the spectrum of capital gains taxes.

* incomebracket: 'middle' or 'high', represents the income bracket to be taxed at.  

* fee: the management fee on the fund (applied to running total, every year).  Should be given as 2 for a rate of 2%, or .5 for a rate of .5%.  Defaults to .05%, Vanguard’s index fund fee.

* title: title of the plot.  Default depends on state and income bracket given.

If using custom data, or just want more flexibility then the arguments provide, it's easy to change the options yourself.  The individual functions for all operations defined in the investment calculator are defined and easy to change and fit with custom values.  Each function defined in the Multiplier function takes an additional argument, data, and then for each data range in the heat map, a wrapper is applied to the induvial functions that provides them the data, and returns a function of just the period (except CGtaxes function.)

### Example
```
# first, we'll generate the yearly inflation, returns, gold, etc., from 1875 to 1905
P = Data()
data1 = P.generate(frm=datetime.strptime('1875-01-01', '%Y-%m-%d'),
                   to=datetime.strptime('1905-01-01', '%Y-%m-%d'))
# for the middle class, in Texas, the following 2 heatmaps compare the effect of a 2% fee to that of a normal
#.05% fee
Multiplier(data4,state="Texas", incomebracket='middle', title=".05% Fee")
Multiplier(data4,state="Texas", incomebracket='middle', fee=2, title="2% Fee")
```

## Compound Multiplier

The Compound Multiplier function produces 2 shaded line plots and a histogram: the shaded line plots are the n year multiplier (one with no taxes, one with an appropriate tax for the given state), for each x.  For instance, when n = 40, the y corresponding to each x is the 40 year multiplier starting in that year.  This histogram is of each of the n year multipliers. 

### Basic Usage

```
# allData should be the entire range of data provided in the format of calling generate in the data class.
# length of data must be greater then n.
# n = period of multiplier we are looking at
# state and income bracket determine the taxes applied
# fee defaults to .05%
CompundMultiplier(allData, n, state="Texas", incomebracket="middle", fee=None)
```

* allData: the same data produced by a call to the generate() method of the data class.  It is built for use by this data, but does not require it.  Other data that is similarly formatted may also be use.  Should be all the data, or at least the length of data should be greater than n

* n: the number of years being compounded, for all possible n length spans in the allData.  Must be less then the length of allData

* state: only takes 'Texas' or 'California', as they are the 2 ends of the spectrum of capital gains taxes.

* incomebracket: 'middle' or 'high', represents the income bracket to be taxed at.  

* fee: the management fee on the fund (applied to running total, every year).  Should be given as 2 for a rate of 2%, or .5 for a rate of .5%.  Defaults to .05%, Vanguard’s index fund fee.

* title: title of the plot.  Default depends on state and income bracket given.

If using custom data, or just want more flexibility then the arguments provide, it's easy to change the options yourself.  The individual functions for all operations defined in the investment calculator are defined and easy to change and fit with custom values.  Each function defined in the Multiplier function takes any number of additional arguments (in dictionary form **kwargs), and then for each data range in the heat map, a wrapper is applied to the induvial functions that provides them the arguments, and returns a function of just the period (except CGtaxes function.)

Please note, the number of graphs being plotted does not affect the run time

### Example
```
# first, we'll generate the yearly inflation, returns, gold, etc., from 1875 to 1905
P = Data()
dataAll = P.generate(frm=datetime.strptime('1875-01-01', '%Y-%m-%d'),
                       to=datetime.strptime('2016-01-01', '%Y-%m-%d'))
CompundMultiplier(allData=dataAll, n=40)
```

## Compound Multiplier Optimizer

Code in Optimize.py<br>
Therefore the compound multiplier takes so long: for each data set, it optimizes the formula using i for the current period, and n as given in the compound multiplier argument:<br>
$$ [\alpha_{1}(i/n)]A + [\alpha_{2}(i/n)^{2}]A + [\beta_{1}(i/n)]B + [\beta_{2}(i/n)^{2}]B \\ s.t.\\ \alpha_{1} + \alpha_{2} + \beta_{1} + \beta_{2} = 1$$
where the alphas and betas were the variables to minmax, and A was the index fund return for period i, and B was the 10-year T-bill yield for period i.
I didn't use \( \alpha_{1}(i/n) + \alpha_{2}(i/n)^{2} + \beta_{1}(i/n) + \beta_{2}(i/n)^{2} = 1 \space \forall i\), a more accurate condition, because it would have yielded an over determined system; instead I used the weaker condition in the formula above and divided the rate for each period by a standardizing constant 
$$ \phi = \frac{1}{\alpha_{1}(i/n) + \alpha_{2}(i/n)^{2} + \beta_{1}(i/n) + \beta_{2}(i/n)^{2}}  $$
so that i wasn't optimizing an un-realizable return, but had room for optimization.<br>

I optimized each rate with respect to the compound investment calculator function (fortunately, with some speed hacks, this runs in o(n) time or this would've taken quite a bit longer!) but quickly realized a Newtonian or range-space algorithm wasn't going to work.  Clearly the Jacobian and hessian are not well defined, and working with my feasible point calculation:
$$ Ax=b \space constraints \\ A^{t} = (Y \space Z)\binom{R}{0} ; \space R^{t}v=b \space \implies \space A(Yv + Zw)=b \space \forall w$$ 
Was going to be a pain in the ass.  Not only that, but small changes in and of the coefficients would not yield any noticeable effect in the multiplier; anything using hessians was a waste of time and any locally optimizing algorithm would almost always settle on the initial points provided; unless it was taking sizable steps.  I ended up using a basinhopping algorithm wrapping a SLSQP local minimization algorithum capped at 5 steps.  It would take large steps, and for each one, take 5 SLSQP steps locally (most of the time, returning the larger steps ending point, byt not always), approximately spanning the useable parts of the subspace of \( \mathbb{R}^{4} \) I was interested in.  It works quite effectively; generating a large range between the min and max for the optimized coefficients.  All optimizations and calculations applied useing scipy and numpy. 




