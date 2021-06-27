from __future__ import (absolute_import, division, print_function, unicode_literals)#向前兼容python2

import backtrader as bt
import datetime
import pandas as pd

class three_bars(bt.Indicator):#继承Indicator不是indicators或indicator

    lines = ('up', 'down')

    def __init__(self):
        self.addminperiod(4)#最小周期4天，4天才能生成指标
        self.plotinfo.plotmaster = self.data#plotmaster表示和主图话画在一起，注释掉之后会分开画

    def next(self):
        #ago = -1表示从昨天开始算，取3天的数据（size = 3）
        self.lines[0][0] = max(max(self.data.close.get(ago = -1, size = 3)), max(self.data.open.get(ago = -1, size = 3)))
        self.lines.down[0] = min(min(self.data.close.get(ago = -1, size = 3)), min(self.data.open.get(ago = -1, size = 3)))


class MyStrategy(bt.Strategy):#继承bt.Strategy类
    def __init__(self):
        self.up_down = three_bars(self.data)#up_down本质是lines指标
        self.buy_signal = bt.indicators.CrossOver(self.data.close, self.up_down.up)#crossover是上穿
        self.sell_signal = bt.indicators.CrossDown(self.data.close, self.up_down.down)#crossdown是下穿
        self.buy_signal.plotinfo.plot = False#可以关闭buysignal的图， 也可以放在继承了indicator的类里面
        self.sell_signal.plotinfo.plot = False

    def start(self):
        print("start")

    def prenext(self):#目前暂时没有
        print("prenext")

    def next(self):#next的策略核心，如果是分钟线，每过1分钟调用一次，日线则每过一天调用一次，取决于数据间隔

        #没必要用以上的代码
        if not self.position and self.buy_signal[0] == 1:#如果没有仓位（空仓）且向上突破均线
            self.order = self.buy(size = 20)
        if not self.position and self.sell_signal[0] == 1:
            self.order = self.sell(size = 20)

        if self.getposition().size < 0 and self.buy_signal[0] == 1:#self.getposition().size 可以确定目前是多头还是空头
            self.order = self.close()#上穿均线了，如果之前有仓位（必定是空仓），则把之前的仓位先平掉，再开仓做多
            self.order = self.buy(size = 20)

        if self.getposition().size > 0 and self.sell_signal[0] == 1:
            self.order = self.close()
            self.order = self.sell(size = 20)



    def stop(self):
        print("stop")




cerebro = bt.Cerebro()

data0 = pd.read_csv(r'priceData.csv')

#create data feed
data0['tradeDate'] = pd.to_datetime(data0['tradeDate'])#必须转成时间戳格式
data0.set_index('tradeDate', inplace=True)
data0['openinterest'] = 0
data0.dropna()
data0 = data0.rename(columns={'turnoverVol' : 'volume'})#column重命名
data0 = data0.rename(columns={'openPrice' : 'open'})
data0 = data0.rename(columns={'highestPrice' : 'high'})
data0 = data0.rename(columns={'lowestPrice' : 'low'})
data0 = data0.rename(columns={'closePrice' : 'close'})
brf_daily = bt.feeds.PandasData(dataname = data0, fromdate = datetime.datetime(2020, 9, 16), todate = datetime.datetime(2021, 6, 25))
#fromdate回测起始时间

#add data feed to cerebro
cerebro.adddata(brf_daily)

#add strategy
cerebro.addstrategy(MyStrategy)

#run
cerebro.run()

#plot
#cerebro.plot()
cerebro.plot(style = 'candle')#画成蜡烛图

