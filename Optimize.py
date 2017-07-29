import numpy as np
from scipy import linalg, optimize
import math
import compundInvestment as cinv
# the point of this class is to fit in with our sandp.py data generated.
# {
#     'year': year,
#     'inflation': infl,
#     'interest': interest,
#     'dividend': dividend,
#     'bond': bond,
#     'tbill': tbill
# }
class qn():
    # takes all the data to analyze
    # f(y) = product(y_i)
    # we'll define the hessian and jacobian manually
    # we'll apply contrainst dirctly to function, before applying scipy minnimizer (via null/basic)
    # if minmax is "Max", gives best coeficents. If "Min", gives worst.

                                                                                 
    def __init__(self,data, minmax="Max"):
        self.data = data
        self.minmax = minmax
        self.datalength = len(data)
        self.bounds = self.getbounds()
        #self.x0 = np.array([.5,.4,.097,.01,.01,.01])
        self.x0 = np.array([0,0,1/6,1/6])
    def cFunc(self,vec):
        A = np.array([[1,1,1,1]])
        return A.dot(vec)-1
    # accept or reject a bashin step.
    def accept_test(self,f_new, x_new, f_old, x_old):
        for v in x_new:
            if v < 0:
                return False
            if v > 1:
                return False
        return True

    # objective function to optimize (minimize, so we put a (-) in front)
    # product of all vector objects (after aplying appropriate null space method multiplication)
    def objective(self, vec):
        # not quite a decorator.  we want to run this on functions, changeing the data we give to them.
        def sudodec(function, data):
            def wrap(n):
                return function(n, data)
            return wrap
        def A(n, data):
            if n == 0:
                return 1
            else:
                return 1 * data[n - 1]
        def alpha(n, data):
            # WARNING we assume bonds and tbills data is available for all years in the given data
            m1 = n/self.datalength
            m2 = (n/self.datalength)**2
            p1 = vec[0]*m1 + vec[1]*m2
            p2 = vec[2]*m1 + vec[3]*m2
            phi = p1 + p2
            IND = p1*(1+data[n-1]['interest'])
            BND = p2*(1+data[n - 1]['bond'])
            return (IND + BND)/phi
        def infl(n, data):
            return 1 + data[n - 1]['inflation']
        def CGtaxes(s, e, n):
            return 1.15
        def dividends(n, data):
            return data[n - 1]['dividend']
        def fees(n):
            return 1 - .0005  # typical vangaurd fee
        def divtaxes(n):
            return 1.15
        inflCumProd = list(np.cumprod([1 + float(ele['inflation']) for ele in self.data]))
        multiplier = cinv.compund(sudodec(A, inflCumProd),
                                  sudodec(alpha, self.data),
                                  sudodec(infl, self.data),
                                  CGtaxes, sudodec(dividends, self.data),
                                  divtaxes, fees, self.datalength, comma=False)
        if self.minmax == "Max":
            return -multiplier
        elif self.minmax == "Min":
            return multiplier
    # upper bound is implied by constraints (if all xi's are > 0 and sum to 1, none may be greater then 1)
    def getbounds(self):
        return [(0,1) for _ in range(4)]

    def minimize(self):
        q = optimize.basinhopping(
            func=self.objective,
            x0=self.x0,
            accept_test=self.accept_test,
            niter=50,
            minimizer_kwargs={
                'bounds':self.bounds,
                'constraints':{
                    'type':'eq',
                    'fun':self.cFunc
                },
                'options':{'disp': False, 'iprint': 1, 'maxiter': 5}
            }
        )
        return q.x

if __name__ == "__main__":
    import time
    data = [{'dividend': 0.041488162, 'year': 1975, 'inflation': 0.091, 'tbill': 0.0599, 'interest': 0.222436604, 'bond': 0.0361}, {'dividend': 0.038681948, 'year': 1976, 'inflation': 0.057, 'tbill': 0.049699999999999994, 'interest': 0.080941565, 'bond': 0.1598}, {'dividend': 0.049776167, 'year': 1977, 'inflation': 0.065, 'tbill': 0.0513, 'interest': -0.096146435, 'bond': 0.0129}, {'dividend': 0.052752055, 'year': 1978, 'inflation': 0.076, 'tbill': 0.0693, 'interest': 0.064930748, 'bond': -0.0078000000000000005}, {'dividend': 0.052411874, 'year': 1979, 'inflation': 0.113, 'tbill': 0.09939999999999999, 'interest': 0.081135292, 'bond': 0.0067}, {'dividend': 0.046142322, 'year': 1980, 'inflation': 0.135, 'tbill': 0.11220000000000001, 'interest': 0.203787196, 'bond': -0.029900000000000003}, {'dividend': 0.05355412, 'year': 1981, 'inflation': 0.10300000000000001, 'tbill': 0.14300000000000002, 'interest': -0.069172932, 'bond': 0.08199999999999999}, {'dividend': 0.04928264, 'year': 1982, 'inflation': 0.061, 'tbill': 0.1101, 'interest': 0.188405797, 'bond': 0.3281}, {'dividend': 0.043126521, 'year': 1983, 'inflation': 0.032, 'tbill': 0.08449999999999999, 'interest': 0.139293139, 'bond': 0.032}, {'dividend': 0.045775076, 'year': 1984, 'inflation': 0.043, 'tbill': 0.09609999999999999, 'interest': -0.011418269, 'bond': 0.1373}, {'dividend': 0.038109021, 'year': 1985, 'inflation': 0.035, 'tbill': 0.07490000000000001, 'interest': 0.208041958, 'bond': 0.2571}, {'dividend': 0.033306516, 'year': 1986, 'inflation': 0.019, 'tbill': 0.0604, 'interest': 0.194044188, 'bond': 0.24280000000000002}, {'dividend': 0.036556017, 'year': 1987, 'inflation': 0.037000000000000005, 'tbill': 0.0572, 'interest': -0.088846881, 'bond': -0.0496}, {'dividend': 0.035262206, 'year': 1988, 'inflation': 0.040999999999999995, 'tbill': 0.0645, 'interest': 0.103792415, 'bond': 0.08220000000000001}, {'dividend': 0.031726908, 'year': 1989, 'inflation': 0.048, 'tbill': 0.08109999999999999, 'interest': 0.221443588, 'bond': 0.1769}, {'dividend': 0.036775665, 'year': 1990, 'inflation': 0.054000000000000006, 'tbill': 0.0755, 'interest': -0.033002912, 'bond': 0.062400000000000004}, {'dividend': 0.031402023, 'year': 1991, 'inflation': 0.042, 'tbill': 0.056100000000000004, 'interest': 0.193615779, 'bond': 0.15}, {'dividend': 0.028440915, 'year': 1992, 'inflation': 0.03, 'tbill': 0.0341, 'interest': 0.04701019, 'bond': 0.09359999999999999}, {'dividend': 0.026998605, 'year': 1993, 'inflation': 0.03, 'tbill': 0.0298, 'interest': 0.07058337, 'bond': 0.1421}, {'dividend': 0.028932973, 'year': 1994, 'inflation': 0.026000000000000002, 'tbill': 0.039900000000000005, 'interest': -0.037632931, 'bond': -0.08039999999999999}, {'dividend': 0.022438453, 'year': 1995, 'inflation': 0.027999999999999997, 'tbill': 0.0552, 'interest': 0.320945728, 'bond': 0.2348}, {'dividend': 0.02004709, 'year': 1996, 'inflation': 0.028999999999999998, 'tbill': 0.050199999999999995, 'interest': 0.209677419, 'bond': 0.0143}, {'dividend': 0.016106071, 'year': 1997, 'inflation': 0.023, 'tbill': 0.050499999999999996, 'interest': 0.255996972, 'bond': 0.09939999999999999}, {'dividend': 0.013612873, 'year': 1998, 'inflation': 0.016, 'tbill': 0.0473, 'interest': 0.235311825, 'bond': 0.1492}, {'dividend': 0.011682112, 'year': 1999, 'inflation': 0.022000000000000002, 'tbill': 0.0451, 'interest': 0.144069765, 'bond': -0.0825}, {'dividend': 0.012224535, 'year': 2000, 'inflation': 0.034, 'tbill': 0.0576, 'interest': -0.066400578, 'bond': 0.1666}, {'dividend': 0.013747565, 'year': 2001, 'inflation': 0.027999999999999997, 'tbill': 0.036699999999999997, 'interest': -0.142779063, 'bond': 0.0557}, {'dividend': 0.017871839, 'year': 2002, 'inflation': 0.016, 'tbill': 0.0166, 'interest': -0.211390884, 'bond': 0.1512}, {'dividend': 0.016092316, 'year': 2003, 'inflation': 0.023, 'tbill': 0.0103, 'interest': 0.206286837, 'bond': 0.0038}, {'dividend': 0.016210672, 'year': 2004, 'inflation': 0.027000000000000003, 'tbill': 0.0123, 'interest': 0.058886377, 'bond': 0.0449}, {'dividend': 0.017605996, 'year': 2005, 'inflation': 0.034, 'tbill': 0.0301, 'interest': 0.06827435, 'bond': 0.0287}, {'dividend': 0.017565411, 'year': 2006, 'inflation': 0.032, 'tbill': 0.046799999999999994, 'interest': 0.107677148, 'bond': 0.0196}, {'dividend': 0.018746366, 'year': 2007, 'inflation': 0.028999999999999998, 'tbill': 0.0464, 'interest': 0.038661386, 'bond': 0.10210000000000001}, {'dividend': 0.032351064, 'year': 2008, 'inflation': 0.038, 'tbill': 0.0159, 'interest': -0.363515043, 'bond': 0.201}, {'dividend': 0.02018228, 'year': 2009, 'inflation': -0.004, 'tbill': 0.0014000000000000002, 'interest': 0.282816146, 'bond': -0.1112}, {'dividend': 0.018308055, 'year': 2010, 'inflation': 0.016, 'tbill': 0.0013, 'interest': 0.104976949, 'bond': 0.08460000000000001}, {'dividend': 0.021257601, 'year': 2011, 'inflation': 0.032, 'tbill': 0.0003, 'interest': -0.030640408, 'bond': 0.1604}, {'dividend': 0.021971609, 'year': 2012, 'inflation': 0.021, 'tbill': 0.0005, 'interest': 0.093581325, 'bond': 0.0297}, {'dividend': 0.019355231, 'year': 2013, 'inflation': 0.015, 'tbill': 0.0007000000000000001, 'interest': 0.221142934, 'bond': -0.091}, {'dividend': 0.019199034, 'year': 2014, 'inflation': 0.016, 'tbill': 0.0005, 'interest': 0.127258061, 'bond': 0.1075}]
    start = time.time()
    QI = qn(data)
    res = QI.minimize()
    end = time.time()
    print(res)
    print('Seconds: {}'.format(end-start))




