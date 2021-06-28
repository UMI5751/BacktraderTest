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


if __name__ == '__main__':

    cerebro = bt.Cerebro(stdstats = False)#关闭默认的observer，即取消默认的cash，value,买卖点的图
    #cerebro.addobserver(bt.observers.TimeReturn)#给出每天的return
    cerebro.addobserver(bt.observers.Value)#画出净值图
    cerebro.addobserver(bt.observers.BuySell)#画出买卖点
    cerebro.addobserver(bt.observers.Trades)#画出每次交易盈利情况
    cerebro.addobserver(bt.observers.DrawDown)#回撤情况
    #observer每天都会生成一个值，和当天数据并列
    #Analyzer是独立的，在writer写出的文件的最后出现，进行统计计算

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
    cerebro.adddata(brf_daily, name = 'brf')#给datafeed命名
    #cerebro.broker.setcommission(commission=2.0, margin=2000, mult=300)

    #add strategy
    cerebro.addstrategy(MyStrategy)
    cerebro.broker.setcash(200000.0)#设置初始资金20000

    #futures mode
    cerebro.broker.setcommission(commission=2.0, margin=2000, mult=10, name = 'brf')
    cerebro.broker.set_slippage_perc(perc = 0.0005)
    cerebro.broker.set_filler(bt.broker.fillers.FixedBarPerc(perc = 0.1))#设置每根bar最多只能成交这根bar的1/10，剩余的分散交易到后面的bar上
    #cerebro.broker.set_filler(bt.broker.fillers.FixedSize(size = 1))固定每根bar只能成交1手

    cerebro.addanalyzer(bt.analyzers.DrawDown)
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer)
    cerebro.addanalyzer(bt.analyzers.SharpeRatio)
    cerebro.addanalyzer(bt.analyzers.Transactions)

    cerebro.addwriter(bt.WriterFile, csv = True, out = 'result.csv')

    #run

    res = cerebro.run()[0] #会返回分析结果,如果有两个策略，则分开分析

    pyfolio = res.analyzers.getbyname('pyfolio')#获取pyfolio的分析结果，包括交易，杠杆率信息
    returns, positions, transactions, gross_lev = pyfolio.get_pf_.items()

    returns.to_hdf('return.h5', key = 'data')
    positions.to_hdf('positions.h5', key='data')
    transactions.to_hdf('transactions.h5', key='data')

    print('DrawDown', res.analyzers.drawdown.get_analysis()) #打印drawdown结果，返回一个dict类型
    #print('max drawdown %s %%' % res['max']['drawdown'])
    print('TradeAnalyzer', res.analyzers.tradeanalyzer.get_analysis())#获取analyzer中traderanalyzer的结果


    #plot
    #cerebro.plot()
    cerebro.plot(style = 'candle')#画成蜡烛图







