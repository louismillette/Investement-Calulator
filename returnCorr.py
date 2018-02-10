import plugin
import datetime
import random
from scipy.stats.stats import pearsonr

class COR(plugin.Handler):
    def __init__(self):
        super().__init__()
        self.M = None
        self.alpha = None

    def generateM(self):
        data1 = self.generate(all=True, base="S and P 500")
        mdata, all_tax, all_fees, all_contributions = self.MultiplierPeriod(data=data1, state="texas", income=60000,
                                                                         contributions=7000, fee=0.0005,
                                                                         filing="single", taxdef=True, span=40)
        M = [[int(ele[0].split('/')[0]), ele[1]] for ele in mdata]
        self.M = M
        return self

    def generateAlpha(self):
        releventReturns = list(filter(lambda x: datetime.datetime.strptime(x['Date'], '%Y-%m-%d').month == 12, self.sandp))
        alpha = [[int(ele['Date'].split('-')[0]),float(ele['Return Percent'])] for ele in releventReturns]
        self.alpha = alpha
        return self

    def bootstrap(self, A, B):
        if not len(A) == len(B):
            raise Exception("A nad B must be the same length")
        AB = list(zip(A,B))
        boot_len = len(AB)
        corrs = []
        for i in range(100):
            obs_A = []
            obs_B = []
            for j in range(boot_len):
                rnum = random.randint(0,boot_len-1)
                obA,obB = AB[rnum]
                obs_A.append(obA)
                obs_B.append(obB)
            cor = pearsonr(obs_A,obs_B)[0]
            corrs.append(cor)
        return sorted(corrs)

    # yearLag (int) lagged corr between returns and end balance
    def corr(self, yearlag):
        oneYearReturns = self.alpha
        endBalance = self.M
        lastyear = max([ele[0] for ele in endBalance])
        oneYearReturns_adj = list(filter(lambda x: x[0] <= lastyear, oneYearReturns))
        i=0
        ilen = len(oneYearReturns_adj)
        while i < ilen:
            oneYearReturns_adj[i][1] = oneYearReturns[i+(40-yearlag)][1]
            i+=1
        A = [ele[1] for ele in oneYearReturns_adj]
        B = [ele[1] for ele in endBalance]
        # print(len(A))
        corrs = self.bootstrap(A,B)
        # print(corrs)
        low = corrs[2]
        high = corrs[97]
        return low, pearsonr(A,B)[0], high

    def corrMA(self, MAlag, yearlag):
        oneYearReturns = self.alpha
        endBalance = self.M
        lastyear = max([ele[0] for ele in endBalance])
        oneYearReturns_adj = list(filter(lambda x: x[0] <= lastyear, oneYearReturns))

        i=0
        ilen = len(oneYearReturns_adj)
        while i < ilen:
            MovA = sum([oneYearReturns[i+(40-yearlag) + ele][1] for ele in range(MAlag)])/MAlag
            oneYearReturns_adj[i][1] = MovA
            i+=1
        A = [ele[1] for ele in oneYearReturns_adj]
        B = [ele[1] for ele in endBalance]
        # print("A ", A)
        # print("B", B)
        corrs = self.bootstrap(A,B)
        # print(corrs)
        low = corrs[2]
        high = corrs[97]
        # print(low, pearsonr(A,B)[0], high)
        return low, pearsonr(A,B)[0], high

if __name__ == "__main__":
    C = COR()
    C.generateM()
    C.generateAlpha()

    # C.corr(1)
    s1 = []
    s2 = []
    zeros_j = []
    for j in range(1,41):
        low_j1, cor_j1, high_j1 = C.corr(j)
        s1.append([j, int(round(low_j1*100,2))/100, int(round(high_j1*100,2))/100])
        s2.append([j, int(round(cor_j1*100,2))/100])
        zeros_j.append([j, 0])
    print(s1)
    print(s2)
    print(zeros_j)
    print('\n')
    s3,s4,zeros_i = [],[],[]
    for i in range(5,41):
        low_i, cor_i, high_i = C.corrMA(5,i)
        s3.append([i,int(round(low_i*100,2))/100,int(round(high_i*100,2))/100])
        s4.append([i, int(round(cor_i*100,2))/100])
        zeros_i.append([i,0])
    print(s3)
    print(s4)
    print(zeros_i)

