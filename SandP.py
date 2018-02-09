import compundInvestment as cinv
import os
import re
import time
import random
from datetime import datetime
from datetime import timedelta
import plotly
from plotly.offline import plot
import plotly.graph_objs as go
import plotly.plotly as py
import math
import numpy as np
import scipy.stats
import Optimize

class Data():
    def __init__(self):
        self.sandp = self.loadSandP()
        self.gold = self.loadGold()
        self.Inflation = self.loadInflation()
        self.safe = self.loadSafe()

    def loadSandP(self):
        scriptDir = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(scriptDir,'SandP.csv'),'r') as csvFile:
            lines = [ele.replace('\n','').split(',') for ele in csvFile.readlines()]
            labels = lines[0]
            stockValues = [dict(zip(labels,ele)) for ele in lines[1:]]
        return stockValues

    def loadInflation(self):
        scriptDir = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(scriptDir,'inflation.csv'),'r') as csvFile:
            lines = [ele.replace('\n','').split(',') for ele in csvFile.readlines()]
            labels = lines[0]
            inflation = [dict(zip(labels,ele)) for ele in lines[1:]]
        return inflation

    def loadGold(self):
        scriptDir = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(scriptDir,'gold.csv'),'r') as csvFile:
            lines = [ele.replace('\n','').split(',') for ele in csvFile.readlines()]
            labels = lines[0]
            gold = [dict(zip(labels,ele)) for ele in lines[1:]]
            golds = sorted(gold, key=lambda x: datetime.strptime(x['Date'], '%Y'))
        return golds

    def loadSafe(self):
        scriptDir = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(scriptDir,'safe.csv'),'r') as csvFile:
            lines = [ele.replace('\n','').split(',') for ele in csvFile.readlines()]
            labels = lines[0]
            safe = [dict(zip(labels,ele)) for ele in lines[1:]]
        return safe

    def fixsandp(self):
        scriptdir = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(scriptdir, 'SandP.csv'), 'r') as csvfile:
            lines = [ele.replace('\n', '').split(',') for ele in csvfile.readlines()]
            labels = lines[0]
            labels = ','.join(labels) + '\n'
            lines = [
                [re.sub(r'([0-9]{1,2})/1/([0-9]{4})',
                        lambda x: str(x.group(2)) + "-" + "{0:0=2d}".format(int(x.group(1))) + str("-01"), ele[0])] +
                ele[1:]
                for ele in lines[1:]
                ]
        lines = [','.join(ele) for ele in lines]
        lines = labels + '\n'.join(lines)
        with open(os.path.join(scriptdir, 'SandP.csv'), 'w+') as csvfile:
            csvfile.write(lines)

    # get auxillary values takes a list of relevent returns, and produces a list of relevent inflation
    # and relevent tbill prices, corresponding 1-1 with the relevent returns dates
    # assumes theere are no missing data points
    # works in nlogn time (sorting time eff)
    def getAuxVals(self,releventReturns):
        n = len(releventReturns)
        RRS = sorted(releventReturns, key=lambda x: datetime.strptime(x['Date'], '%Y-%m-%d'))
        RRSyears = [datetime.strptime(ele['Date'], '%Y-%m-%d').year for ele in RRS]
        start = RRSyears[0]
        end = RRSyears[-1]
        tbill = sorted(
            list(filter(lambda x: end >= int(x['Year']) >= start,self.safe)),
            key=lambda x: x['Year'])
        infl = sorted(
            list(filter(lambda x: end >= int(x['Year']) >= start, self.Inflation)),
            key=lambda x: x['Year'])
        mint = int(tbill[0]['Year'])
        mini = int(infl[0]['Year'])
        maxt = int(tbill[-1]['Year'])
        maxi = int(infl[-1]['Year'])
        infloffset = 0
        tbilloffset = 0
        allinfl = []
        alltbill = []
        for ret in range(n):
            if RRSyears[ret] < mint:
                alltbill.append({'Year':RRSyears[ret], '10 Year Treasury Rate': None})
                tbilloffset += 1
            elif RRSyears[ret] > maxt:
                # no offset here.  If we are beyond the range of our tbills, we wont be in range of them at any futuree point
                alltbill.append({'Year': RRSyears[ret], '10 Year Treasury Rate': None})
            else:
                alltbill.append(
                    1 + float(tbill[ret-tbilloffset]['10 Year Treasury Rate'].replace('%',''))/100)
            if RRSyears[ret] < mini:
                allinfl.append({'Year':RRSyears[ret], 'Inflation': None})
                infloffset += 1
            elif RRSyears[ret] > maxi:
                # no offset here.  If we are beyond the range of our infl, we wont be in range of them at any futuree point
                allinfl.append({'Year': RRSyears[ret], 'Inflation': None})
            else:
                allinfl.append(
                    1 + float(infl[ret-infloffset]['Inflation'].replace('%',''))/100)
        return allinfl,alltbill

    # picks a n year span, returns inflation, s and p growth, and dividends for each year in the given span
    # and bond and tbill prices
    # [ { 'year':year, 'inflation':inflation', 'interest':interest, 'dividend':dividend}, ...]
    # O(nlogn).
    def generate(self, n=40, to=None, frm= None):
        stockValues = self.sandp
        year = random.randint(a=1940, b=2015 - n)
        to = to if to else datetime.strptime('{}-01-01'.format(year+n), '%Y-%m-%d')
        frm = frm if frm else datetime.strptime('{}-01-01'.format(year), '%Y-%m-%d')
        releventReturns = list(filter(
            lambda x: to > datetime.strptime(x['Date'], '%Y-%m-%d') > frm and
                      datetime.strptime(x['Date'], '%Y-%m-%d').month == 12, stockValues))

        obs = []
        infl,tbills = self.getAuxVals(releventReturns)
        rng = range(len(releventReturns))
        for index in rng:
            releventReturn = releventReturns[index]
            inflation = infl[index]
            tbill = tbills[index]
            obs.append({
                'year': datetime.strptime(releventReturn['Date'], '%Y-%m-%d').year,
                'inflation': inflation,
                'bond': tbill,
                'interest': 1+float(releventReturn['Return Percent']),
                'dividend': float(releventReturn['Dividend Yield'])
            })
        return obs

    # picks all 40 year spans, returns average inflation centered to inflCenter, average s and p growth centerd to irCenter,
    #  and dividends for each year in the given span
    # [ { 'year':year1, 'inflation':average_inflation', 'interest':average_interest, 'dividend':average_dividend}, ...]
    def genAv(self, n=40 ,irCenter=None, inflCenter=None, divCenter=None):
        releventReturns = list(filter( lambda x: datetime.strptime(x['Date'], '%Y-%m-%d').month == 12, self.sandp))
        stockValues = sorted(releventReturns,key=lambda x: datetime.strptime(x['Date'], '%Y-%m-%d').year)
        length = len(stockValues)
        mindate = datetime.strptime(stockValues[0]['Date'], '%Y-%m-%d').year
        maxdate = datetime.strptime(stockValues[-1]['Date'], '%Y-%m-%d').year
        # this assumes and doesnt check (for efficency) that there are no missing inflation dates,
        # and all s and p dates are also inflation dates
        infl = filter(lambda x: mindate <= datetime.strptime(x['Year'], '%Y').year <= maxdate, self.Inflation)
        infls = sorted(infl, key=lambda x: datetime.strptime(x['Year'], '%Y').year)
        infls = [float(ele["Inflation"].replace('%',''))/100 for ele in infls]
        returns = [float(ele['Return Percent']) for ele in stockValues]
        dividends = [float(ele['Dividend Yield']) for ele in stockValues]
        inflc = list(np.cumsum(infls))
        returnsc = list(np.cumsum(returns))
        #print(returns)
        devidendsc = list(np.cumsum(dividends))
        values = []
        for base in range(n):
            year = base + 1
            inflb = inflc[length - n - 1 + base] - inflc[max(base - 1,0)]
            returnsb = returnsc[length - n - 1 + base] - returnsc[max(base - 1,0)]

            devidendsb = devidendsc[length - n - 1 + base] - devidendsc[max(base - 1,0)]
            values.append({
                'year': year,
                'inflation': inflb/(length - n),
                'interest': returnsb/(length - n),
                'dividend': devidendsb/(length - n)
            })
        if irCenter:
            returnsa = sum([ele['interest'] for ele in values]) / n
            mod = returnsa - irCenter
            def f(x):
                x['interest'] -= mod
                return x
            values = list(map(f,values))
        if inflCenter:
            infla = sum([ele['inflation'] for ele in values]) / n
            mod = infla - inflCenter
            def g(x):
                x['inflation'] -= mod
                return x
            values = list(map(g, values))
        if divCenter:
            diva = sum([ele['dividend'] for ele in values]) / n
            mod = diva - divCenter
            def h(x):
                x['dividend'] -= mod
                return x
            values = list(map(h, values))
        return values

class Plot():
    def __init__(self, online=False):
        self.online = online # change this to go online v offline
        # use your own username and api key
        plotly.tools.set_credentials_file(username='louismillette', api_key='v0ARg8oEXazysSV53A5h')
    # takes data in list of lists:
    # [[x1,y1], ... , [xn,yn]]
    def LinePlotSimple(self,data,title,xaxis,yaxis, filename="basic-line"):
        trace = go.Scatter(
            x=[ele[0] for ele in data],
            y=[ele[1] for ele in data]
        )
        d = [trace]
        plot(d, filename=filename)
    # takes multiple series of data (in same chart).  X data is a list of x values. y data series is
    # [{'data':[y11, ..., y1n], 'mode': mode1, 'name': series name 1}, .. , {'data':[ym1, ..., ymn], 'mode': mode m, 'name': series name m}]
    # modes: lines, or lines + markers, or markers.
    def LinePlot(self, x, y, title, xaxis, yaxis, filename="multi-series-lines"):
        layout = go.Layout(
            title=title,
            xaxis=dict(
                title=xaxis,
                titlefont=dict(
                    family='Courier New, monospace',
                    size=18,
                    color='#7f7f7f'
                )
            ),
            yaxis=dict(
                title=yaxis,
                titlefont=dict(
                    family='Courier New, monospace',
                    size=18,
                    color='#7f7f7f'
                )
            )
        )
        data = []
        for dat in y:
            data.append(go.Scatter(
                x=x,
                y=dat['data'],
                mode=dat['mode'],
                name=dat['name']
            ))
        fig = go.Figure(data=data, layout=layout)
        if self.online:
            py.plot(fig,filename=filename)
        else:
            plot(fig, filename=filename)

    def LinePlotInterval(self, y, yreg=None, title="Chart Title", xaxis="X-Axis", yaxis="Y-Axis", filename="Linechart-range.html"):
        layout = go.Layout(
            title=title,
            xaxis=dict(
                title=xaxis,
                titlefont=dict(
                    family='Courier New, monospace',
                    size=18,
                    color='#7f7f7f'
                )
            ),
            yaxis=dict(
                title=yaxis,
                titlefont=dict(
                    family='Courier New, monospace',
                    size=18,
                    color='#7f7f7f'
                )
            )
        )
        data = []
        if yreg:
            for dat in yreg:
                data.append(go.Scatter(
                    x=dat['x'],
                    y=dat['data'],
                    mode=dat['mode'],
                    name=dat['name'],
                    line=go.Line(color=dat['color'])
                ))
        for dat in y:
            data.append(go.Scatter(
                x=dat['x'] + dat['x'][::-1],
                y=dat['upper'] + dat['lower'][::-1],
                fill='tonexty',
                fillcolor=dat['fillcolor'],
                showlegend=False,
                mode ='none',
                name=dat['name']
            ))
            data.append(go.Scatter(
                x=dat['x'],
                y=dat['data'],
                line=go.Line(color=dat['color']),
                mode='lines',
                name=dat['name'],
            ))
        fig = go.Figure(data=data, layout=layout)
        if self.online:
            py.plot(fig,filename=filename)
        else:
            plot(fig, filename=filename)

    # colormap is list of values and what color they should be.  For instance
    # [[[0,1], hexcolor1], ... ,[[7,'+'], hexcolor1]]].
    def heatmap(self,x,y,z,colormap=None, title='Title', ticks='Ticks',xaxis='Xlab', yaxis='Ylab', filename='heatmap.html'):
        layout = go.Layout(
            title=title,
            xaxis=dict(
                ticks=ticks,
                nticks=20,
                title=xaxis,
                titlefont=dict(
                    family='Courier New, monospace',
                    size=18,
                    color='#7f7f7f'
                )
            ),
            yaxis=dict(
                title=yaxis,
                titlefont=dict(
                    family='Courier New, monospace',
                    size=18,
                    color='#7f7f7f'
                )
            )
        )
        if colormap:
            zfloat = sorted([float(ele) for ele in z])
            zmax,zmin = max(zfloat), min(zfloat)
            cdf = 0
            colorscale = []
            zlength = zmax - zmin
            for color in colormap:
                if color[0][0] > zmax:
                    continue
                elif color[0][1] < zmin:
                    continue
                else:
                    c = color[0]
                    p = (min(zmax, c[1]) -  max(zmin, c[0]))/zlength
                    colorscale.append([cdf, color[1]])
                    break
            for color in colormap:
                if color[0][0] > zmax:
                    continue
                elif color[0][1] < zmin:
                    continue
                else:
                    c = color[0]
                    p = (min(zmax, c[1]) -  max(zmin, c[0]))/zlength
                    cdf += p
                    colorscale.append([cdf, color[1]])
            colorscale[-1][0] = 1
            trace = go.Heatmap(
                x=x,
                y=y,
                z=z,
                colorscale=colorscale,
            )
        else:
            trace = go.Heatmap(
                x=x,
                y=y,
                z=z,
                zauto=False,
                autocolorscale=False,
            )
        data = go.Data([trace])
        fig = go.Figure(data=data, layout=layout)
        if self.online:
            py.plot(fig,filename=filename)
        else:
            plot(fig, filename=filename)
    # takes list of datapoints, produces histogram.  Also fits an exp distr., if exp=True
    def Histogram(self,data, title="No Title", xaxis="No Title", yaxis="No Title", filename="Histogram", exp=False):
        if exp:
            alpha, loc, beta = scipy.stats.gamma.fit(data[10:])
            rvs = sorted(scipy.stats.gamma.rvs(alpha, loc=loc, scale=beta, size=100))
            height = scipy.stats.gamma.pdf(rvs, alpha, loc=loc, scale=beta)
            height = height * (30/max(height))
            trace2 = go.Scatter(
                x=[ele-10 for ele in rvs],
                y=height,
                mode='lines',
                name='Gamma Fit'
            )

        layout = go.Layout(
            title=title,
            xaxis=dict(
                title=xaxis,
                titlefont=dict(
                    family='Courier New, monospace',
                    size=18,
                    color='#7f7f7f'
                )
            ),
            yaxis=dict(
                title=yaxis,
                titlefont=dict(
                    family='Courier New, monospace',
                    size=18,
                    color='#7f7f7f'
                )
            )
        )
        trace1 = go.Histogram(
            x=data,
            name="Data"
        )
        if exp:
            fig = go.Figure(data=[trace1, trace2], layout=layout)
        else:
            fig = go.Figure(data=[trace1], layout=layout)
        if self.online:
            py.plot(fig,filename=filename)
        else:
            plot(fig, filename=filename)

# here we make a heat map of the multiplier of your money given the data provided, based on the
# state, income bracket, and fee provided
def Multiplier(data, state, incomebracket, fee=None, title=None):
    data = sorted(data, key=lambda x: datetime(year=x['year'], month=1, day=1))

    # not quite a decorator.  we want to run this on functions, changeing the data we give to them.
    def sudodec(function,data):
        def wrap(n):
            return function(n,data)
        return wrap

    def A(n):
        if n == 0:
            return 1
        else:
            return 0
    def alpha(n,data):
        return 1 + data[n-1]['interest']
    def infl(n, data):
        return 1 + data[n - 1]['inflation']
    def CGtaxes(s,e,n):
        if state == "Texas":
            if incomebracket == "middle":
                return 1.15
            elif incomebracket == "high":
                return 1.238
        elif state == "California":
            if incomebracket == "middle":
                return 1.2415
            elif incomebracket == "high":
                return 1.361
    def dividends(n, data):
        return data[n-1]['dividend']
    def fees(n):
        if fee:
            return 1-(fee/100)
        else:
            return 1-.0005 #typical vangaurd fee
    def divtaxes(n,t,multiplier):
        if state == "Texas":
            if incomebracket == "middle":
                return 1.15
            elif incomebracket == "high":
                return 1.238
        elif state == "California":
            if incomebracket == "middle":
                return 1.2415
            elif incomebracket == "high":
                return 1.361
    x, y, z = [],[],[]
    colors = [[[0.5,.75],'rgb(255,0,0)'],[[0.75,1],'rgb(255,255,255)'],
              [[1.0,3.0],'rgb(0,255,255)'],[[3.0,7.0],'rgb(0,0,255)'],
              [[7.0,30.0],'rgb(0,0,125)'], [[30.0,100.0],'rgb(0,0,0)']]
    for frm in data:
        for to in data:
            yearfrm = datetime(year=frm['year'], month=1, day=1)
            yearto = datetime(year=to['year'], month=1, day=1)
            if yearfrm > yearto:
                continue
            else:
                indexfrm = data.index(frm)
                indexto = data.index(to)
                newdata = data[indexfrm:indexto + 1]
                multiplier = cinv.compund(A,
                                          sudodec(alpha,newdata),
                                          sudodec(infl,newdata),
                                          CGtaxes, sudodec(dividends,newdata),
                                          divtaxes, fees, len(newdata),comma = True)
                x.append(frm['year'])
                y.append(to['year'])
                z.append(multiplier)
    plt = Plot()
    if incomebracket == 'middle':
        lbl = "50-100k"
    elif incomebracket == 'high':
        lbl = '500k+'
    if title:
        plt.heatmap(x, y, z, colormap=colors, title=title,
                    ticks="%", xaxis="Year Depositied Money", yaxis="Year Withdrawn Money",
                    filename=title)
    else:
        plt.heatmap(x,y,z,colormap=colors,title="{} {} CG Tax S&P500 Multiplier".format(state,lbl),
                    ticks="%", xaxis="Year Depositied Money", yaxis="Year Withdrawn Money",
                    filename="{} {} CG Tax S&P500 Multiplier".format(state,lbl))

    # print("Using the old rates: {}\n".format(old), "Using the new rates: {}".format(new))

def CompundMultiplier(allData, n, state="Texas", incomebracket="middle", fee=None):
    data = sorted(allData, key=lambda x: datetime(year=x['year'], month=1, day=1))
    datalength = len(data)
    dataSets = [data[e:e+n] for e in range(datalength - n)]
    # not quite a decorator.  we want to run this on functions, changeing the data (and other variables) we give to them.
    def sudodec(function, data, **kwargs):
        def wrap(n):
            return function(n, data, **kwargs)
        return wrap

    def A(n,data):
        if n == 0:
            return 1
        else:
            return 1 * data[n-1]

    # everything goes in an index
    def alphaIndex(n,data):
        return data[n-1]['interest']
    # useing "balanced" https://www3.troweprice.com/fb2/fbkweb/snapshot.do?ticker=RPBAX
    # useing average returns over its existance
    # everything goes in a safe (mutual) fund, returning 1.38% above inflation and a 2% fee
    def alphaSafe(n,data):
        return data[n-1]['interest']
    def alphaMix(n,data,coef,datalength):
        # we'll only use bonds/tbills when we can look at safe investements for all years
        if data[0]['bond']:
            # normallize our coef. each year
            v = np.array([n/datalength, (n/datalength)**2,n/datalength, (n/datalength)**2])
            multiplier = 1/(coef.T).dot(v)
            c = multiplier * (coef * v)# normalized multiplier
            dataslice = np.array([data[n-1]['interest'],data[n-1]['interest'],data[n-1]['bond'],data[n-1]['bond']])
            return (c.T).dot(dataslice)
        else:
            return data[n - 1]['interest']
    def infl(n, data):
        return data[n - 1]['inflation']
    def CGtaxes(s,t,multiplier):
        if state == "Texas":
            if incomebracket == "middle":
                return 1.15
            elif incomebracket == "high":
                return 1.238
        elif state == "California":
            if incomebracket == "middle":
                return 1.2415
            elif incomebracket == "high":
                return 1.361
    def CGtaxes401(s,t,multiplier):
        return 1
    def dividends(n, data):
        return data[n-1]['dividend']
    def fees(n):
        if fee:
            return 1-(fee/100)
        else:
            return 1-.0005 #typical vangaurd fee
    def divtaxes(n,t, multiplier):
        if state == "Texas":
            if incomebracket == "middle":
                return 1.15
            elif incomebracket == "high":
                return 1.238
        elif state == "California":
            if incomebracket == "middle":
                return 1.2415
            elif incomebracket == "high":
                return 1.361
    def divtaxes401(n,t,multiplier):
        return 1
    x, m1, m2, m3, m4, m5, m6 = [], [], [], [], [], [], []
    for set in dataSets:
        print('Applying new set')
        inflCumProd = list(np.cumprod([float(ele['inflation']) for ele in set]))
        yearfrm = datetime(year=set[0]['year'], month=1, day=1)
        # coef_good = Optimize.qn(set,minmax="Max").minimize()
        # coef_bad = Optimize.qn(set,minmax="Min").minimize()
        # print(coef_good,coef_bad)
        # multiplier1 = cinv.compund(sudodec(A,inflCumProd),
        #                           sudodec(alphaMix,set, coef=coef_good, datalength=n),
        #                           sudodec(infl,set),
        #                           CGtaxes, sudodec(dividends,set),
        #                           divtaxes, fees, n, comma=False)
        # multiplier2 = cinv.compund(sudodec(A,inflCumProd),
        #                           sudodec(alphaMix,set, coef=coef_bad, datalength=n),
        #                           sudodec(infl,set),
        #                           CGtaxes, sudodec(dividends,set),
        #                           divtaxes, fees, n,comma = False)
        # multiplier3 = cinv.compund(sudodec(A,inflCumProd),
        #                           sudodec(alphaMix,set, coef=coef_good, datalength=n),
        #                           sudodec(infl,set),
        #                           CGtaxes401, sudodec(dividends,set),
        #                           divtaxes401, fees, n, comma=False)
        # multiplier4 = cinv.compund(sudodec(A,inflCumProd),
        #                           sudodec(alphaMix,set, coef=coef_bad, datalength=n),
        #                           sudodec(infl,set),
        #                           CGtaxes401, sudodec(dividends,set),
        #                           divtaxes401, fees, n,comma = False)
        multiplier5 = cinv.compund(sudodec(A,inflCumProd),
                                  sudodec(alphaIndex,set),
                                  sudodec(infl,set),
                                  CGtaxes, sudodec(dividends, set),
                                  divtaxes, fees, n,comma = False)
        multiplier6 = cinv.compund(sudodec(A,inflCumProd),
                                  sudodec(alphaIndex,set),
                                  sudodec(infl,set),
                                   CGtaxes401, sudodec(dividends, set),
                                   divtaxes401, fees, n,comma=False)
        x.append(yearfrm)
        # m1.append(multiplier1)
        # m2.append(multiplier2)
        # m3.append(multiplier3)
        # m4.append(multiplier4)
        m5.append(multiplier5)
        m6.append(multiplier6)
    # plt = Plot()
    # plt.LinePlotInterval(y=[
    #     {
    #         'x':[ele.year for ele in x],
    #         'upper': m1,
    #         'lower': m2,
    #         'data':m5,
    #         'name': 'Safe+Index',
    #         'fillcolor': 'rgba(255,0,0,.4)',
    #         'color': 'rgb(0,0,0)'
    #     },
    # ],
    # # yreg=[
    # #     {
    # #         'x':[ele.year for ele in x],
    # #         'data':m1,
    # #         'mode':'lines',
    # #         'name':'Upper',
    # #         'color':'rgb(255,0,0)'
    # #     },
    # #     {
    # #         'x': [ele.year for ele in x],
    # #         'data': m2,
    # #         'mode': 'lines',
    # #         'name': 'Lower',
    # #         'color': 'rgb(255,0,0)'
    # #     },
    # # ],
    # xaxis='Year',yaxis='Multiplier', title='40 Year Safe+Index Multiplier', filename='40 Year Safe+Index Multiplier')
    # time.sleep(1)
    # plt.LinePlotInterval(y=[
    #     {
    #         'x': [ele.year for ele in x],
    #         'upper': m3,
    #         'lower': m4,
    #         'data': m6,
    #         'name': 'Safe + Index',
    #         'fillcolor': 'rgba(0,0,255,.4)',
    #         'color': 'rgb(0,0,0)'
    #     },
    # ],
    # # yreg=[
    # #     {
    # #         'x':[ele.year for ele in x],
    # #         'data':m3,
    # #         'mode':'lines',
    # #         'name':'Upper',
    # #         'color':'rgb(0,0,255)'
    # #     },
    # #     {
    # #         'x': [ele.year for ele in x],
    # #         'data': m4,
    # #         'mode': 'lines',
    # #         'name': 'Lower',
    # #         'color': 'rgb(0,0,255)'
    # #     },
    # # ],
    # xaxis='Year',yaxis='Multiplier', title='40 Year 401k Safe+Index Multiplier', filename='40 Year 401k Safe+Index Multiplier')
    # plt.Histogram(m6,title="Index Multiplier 401k", xaxis="Observations", yaxis="Frequency", exp=True, filename="Index Multiplier 401k")

    # print("Using the old rates: {}\n".format(old), "Using the new rates: {}".format(new))

def movingAverage(a, n=3):
    ret = np.cumsum(a, dtype=float)
    ret[n:] = (ret[n:] - ret[:-n])/n
    return a[:n] + list(ret[n:])

def plotInflation(inflation, gold):
    inflation = sorted(inflation, key=lambda x: datetime.strptime(x['Year'], '%Y'))
    gold = sorted(gold, key=lambda x: datetime.strptime(x['Date'], '%Y')) # different x!!!
    x = [datetime.strptime(ele['Year'], '%Y') for ele in inflation]
    infl = [ele['Inflation'] for ele in inflation]
    cpi = [float(ele['CPI'])/10 for ele in inflation]
    gld = [ele['Change'] for ele in gold]
    c = Plot()
    c.LinePlot(x = x,
               y = [{'data':infl, 'mode':'lines', 'name':"Inflation"},
                    {'data': cpi, 'mode': 'lines', 'name': "CPI / 10"},
                    {'data':gld, 'mode': 'lines', 'name': 'Gold'}],
               xaxis="Inflation Rate", yaxis="Date", title="Rate", filename="Inflation-CPI-line.html")

def plotSandP(sandp):
    sandpYears = list(filter(lambda x: datetime.strptime(x['Date'], '%Y-%m-%d').month == 12, sandp))
    sandpSorted = sorted(sandpYears, key=lambda x: datetime.strptime(x['Date'], '%Y-%m-%d'))
    x = [datetime.strptime(ele['Date'], '%Y-%m-%d') for ele in sandpSorted]
    div = [float(ele['Dividend Yield']) * 100 for ele in sandpSorted]
    total = [float(ele['Return Percent']) * 100 + float(ele['Dividend Yield']) * 100 for ele in sandpSorted]
    c = Plot()
    c.LinePlot(x = x,
               y = [{'data': div, 'mode': 'lines', 'name': "Dividends Yield"},
                    {'data': total, 'mode': 'lines', 'name': "Total Return"}],
               xaxis="Date", yaxis="Return/Yield", title="S and P 500 Nominal Rate of Return", filename="sandp500.html")

# data1 = loadSandP()
# data2 = loadInflation()
# data3 = loadGold()
# plotStuff(data2,data3)
#print(generate(data1,data2,40))
if __name__ == '__main__':
    P = Data()
    data = P.genAv()
    data1 = P.generate(frm=datetime.strptime('1875-01-01', '%Y-%m-%d'),
                       to=datetime.strptime('1905-01-01', '%Y-%m-%d'))
    data2 = P.generate(frm=datetime.strptime('1905-01-01', '%Y-%m-%d'),
                       to=datetime.strptime('1945-01-01', '%Y-%m-%d'))
    data3 = P.generate(frm=datetime.strptime('1945-01-01', '%Y-%m-%d'),
                       to=datetime.strptime('1985-01-01', '%Y-%m-%d'))
    data4 = P.generate(frm=datetime.strptime('1975-01-01', '%Y-%m-%d'),
                       to=datetime.strptime('2015-01-01', '%Y-%m-%d'))

    data5 = P.generate(frm=datetime.strptime('1920-01-01', '%Y-%m-%d'),
                       to=datetime.strptime('1960-01-01', '%Y-%m-%d'))
    data6 = P.generate(frm=datetime.strptime('1881-01-01', '%Y-%m-%d'),
                       to=datetime.strptime('1924-01-01', '%Y-%m-%d'))
    dataAll = P.generate(frm=datetime.strptime('1875-01-01', '%Y-%m-%d'),
                       to=datetime.strptime('2016-01-01', '%Y-%m-%d'))
    # Multiplier(data,state="Texas", incomebracket='middle', ir='old')
    # time.sleep(2)
    # Multiplier(data2,state="Texas", incomebracket='middle', ir='old')
    # time.sleep(2)
    # Multiplier(data3,state="Texas", incomebracket='middle', ir='old')
    # time.sleep(2)
    # Multiplier(data4,state="Texas", incomebracket='middle', ir='old', title=".05% Fee")
    # Multiplier(data4,state="Texas", incomebracket='middle', ir='old', fee=2, title="2% Fee")
    # Multiplier(data4,state="California", incomebracket='middle', ir='old')
    # Multiplier(data5,state="Texas", incomebracket='middle', ir='old')
    # time.sleep(2)
    # MultiplierVan(data1,state="Texas", incomebracket='middle', ir='old')
    # time.sleep(2)
    # Multiplier(data6, state="Texas", incomebracket='middle')

    # CompundMultiplier(allData=dataAll, n=10)
    CompundMultiplier(allData=dataAll, n=40)
    # CompundMultiplier(allData=dataAll, n=40)
    # time.sleep(1)
    # MultiplierVan(data,state="Texas", incomebracket='middle', ir='new')
    # time.sleep(1)
    # MultiplierVan(data,state="California", incomebracket='high', ir='new')
    # time.sleep(1)
    # MultiplierVan(data,state="Texas", incomebracket='high', ir='new')
    # time.sleep(1)
    #P.fixsandp()
    # plotInflation(P.Inflation, P.gold)
    # time.sleep(1)
    # plotSandP(P.sandp)
