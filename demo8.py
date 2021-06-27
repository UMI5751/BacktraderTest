#策略优化器
from __future__ import (absolute_import, division, print_function, unicode_literals)#向前兼容python2

import backtrader as bt
import datetime
import pandas as pd

#DualThrust Strategy
class DT_Line(bt.Indicator):#继承Indicator不是indicators或indicator

    lines = ('U', 'D')
    params = (('period', 2), ('k_u', 0.7), ('k_d', 0.7))#三个参数

    def __init__(self):
        self.addminperiod(self.p.period + 1)#指标最小生成周期，params中的period参数+1，eg要前两天数据计算出上轨下轨，第三天才能计算

    def next(self):
        HH = max(self.data.high.get(ago = -1, size = self.p.period))#这里不需要取data1，下面strategy调用的时候会传入data1
        LC = min(self.data.close.get(ago = -1, size = self.p.period))
        HC = max(self.data.close.get(ago = -1, size = self.p.period))
        LL = min(self.data.low.get(ago = -1, size = self.p.period))

        R = max(HH - LC, HC - LL)
        self.lines.U[0] = self.data.open[0] + self.p.k_u * R
        self.lines.D[0] = self.data.open[0] - self.p.k_d * R


class t_s(bt.Strategy):#继承bt.Strategy类
    params = (('period', 2), ('k_u', 0.7), ('k_d', 0.7))

    def __init__(self):
        #data1表示下面resample之后的日数据，data是主数据
        self.dataClose = self.data0.close#data0和data是等价的,这里不需要取[0]，next函数里面取
        self.D_line = DT_Line(self.data1, period = self.p.period, k_u = self.p.k_u, k_d = self.p.k_d)#可以修改indicator参数，.p就是.parameter
        self.D_line = self.D_line() #调用D_line()本身，会自动把原来每日级的line转成主数据时间级别（分钟级）的line
        self.D_line.plotinfo.plotmaster = self.data0 #每天产生一次信号，可以直接画在data1日线的图上面
        self.buy_signal = bt.indicators.CrossOver(self.dataClose, self.D_line.U)
        self.sell_signal = bt.indicators.CrossDown(self.dataClose, self.D_line.D)

    def start(self):
       pass

    def prenext(self):#目前暂时没有
        pass

    def next(self):#next的策略核心，如果是分钟线，每过1分钟调用一次，日线则每过一天调用一次，取决于数据间隔
        # 获取当前时间，9点31分开市，3点闭市，最后5分钟不做交易，防止持仓过夜
        if self.data.datetime.time() > datetime.time(9,33) and self.data.datetime.time() < datetime.time(14, 55):

            if not self.position and self.buy_signal[0] == 1:#如果没有仓位（空仓）且向上突破均线
                self.order = self.buy(size = 200)
            if not self.position and self.sell_signal[0] == 1:
                self.order = self.sell(size = 200)

            if self.getposition().size < 0 and self.buy_signal[0] == 1:#self.getposition().size 可以确定目前是多头还是空头
                self.order = self.close()#上穿均线了，如果之前有仓位（必定是空仓），则把之前的仓位先平掉，再开仓做多
                self.order = self.buy(size = 200)

            if self.getposition().size > 0 and self.sell_signal[0] == 1:
                self.order = self.close()
                self.order = self.sell(size = 200)

        if self.data.datetime.time() >= datetime.time(14, 55) and self.position:#self.position return bool值，是否持仓
            self.order = self.close()


    def stop(self):
        print('period: %s, k_u: %s, k_d: %s, final_value: %.2f' %
              (self.p.period, self.p.k_u, self.p.k_d, self.broker.getvalue())) #获取优化后的参数,broker.getvalue获取净值


if __name__ == '__main__':

    cerebro = bt.Cerebro()

    data0 = pd.read_csv('priceDataMin.csv')
    data0.dropna()

    #create data feed
    data0['time'] = pd.to_datetime(data0['time'])#必须转成时间戳格式
    data0.set_index('time', inplace=True)
    data0['openinterest'] = 0
    data0.dropna()
    brf_min = bt.feeds.PandasData(dataname = data0,
                                    fromdate = datetime.datetime(2021, 6, 1),
                                    todate = datetime.datetime(2021, 6, 25),
                                    timeframe = bt.TimeFrame.Minutes)

    #add data feed to cerebro
    cerebro.adddata(brf_min)
    cerebro.resampledata(brf_min, timeframe = bt.TimeFrame.Days)

    #add strategy
    cerebro.addstrategy(t_s)

    #策略优化器，里面放可迭代对象
    cerebro.optstrategy(
        t_s,
        period = range(1, 5),
        k_u = [n / 10.0 for n in range(2, 10)],
        k_d = [n/ 10.0 for n in range(2, 10)]
    )

    #run
    cerebro.run()

    #plot
    #cerebro.plot()
    #cerebro.plot(style = 'candle')


