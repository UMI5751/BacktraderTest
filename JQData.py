from jqdatasdk import *
import pandas as pd



auth('name','passwd')

df = get_price(['510300.XSHG'],start_date='2021-06-01 10:00:00', end_date='2021-06-25 15:00:00', frequency='1m')

df.to_csv(path_or_buf=r"price.csv")