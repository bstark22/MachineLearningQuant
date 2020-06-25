import numpy as np
import pandas as pd
from statsmodels.iolib.table import SimpleTable

class VolatilityCone:
    """Class to generate volatility cones for various tickers """
    def __init__(self, df):
        """
        :input df: Pandas DataFrame with required columns 
            'open', 'high', 'low', 'close', 'adj_close'
        The cone is generated over the entire date range of the df
            recommended to filter i.e. filter last 2 years
            VolatilityCone(df[df['date']>np.max(df['date'])-pd.Timedelta(days=720)])
        ex: 
            df = pandas DataFrame
            cone = VolatilityCone(df)
            cone.summary('c2c')
            cone.summary('park')
            cone.summary('gk')
            cone.summary('rsy')
        """
        self.df=df
    def _c2c(self, today_close, yesterday_close):
        """Close to close estimator"""
        return np.log(np.divide(today_close,yesterday_close))
    def _park(self, today_high, today_low, adjustment_factor):
        """Parkinson volatility estimator"""
        adj_high = adjustment_factor*today_high
        adj_low = adjustment_factor*today_low
        return np.multiply((1/(4*np.log(2))) , np.power(np.log(np.divide(adj_high,adj_low)),2))
    def _gk(self, today_close, today_open, today_high, today_low, adjustment_factor):
        """Garman-Klass volatility Estimator"""
        adj_open = today_open*adjustment_factor
        adj_close = today_close*adjustment_factor
        adj_high = today_high*adjustment_factor
        adj_low = today_low*adjustment_factor
        log_hl = np.log(np.divide(adj_high,adj_low))
        log_co = np.log(np.divide(adj_close,adj_open))
        log_oc = np.log(np.divide(adj_open,adj_close))
        return np.power(log_oc,2)+0.5*np.power(log_hl,2)-0.3862*np.power(log_co,2)
    def _rsy(self, today_close, today_open, today_high, today_low, adjustment_factor):
        """Rodgers-Satchell-Yoon volatility Estimator"""
        adj_open = today_open*adjustment_factor
        adj_close = today_close*adjustment_factor
        adj_high = today_high*adjustment_factor
        adj_low = today_low*adjustment_factor
        log_ho = np.log(np.divide(adj_high,adj_open))
        log_lo = np.log(np.divide(adj_low,adj_open))
        log_co = np.log(np.divide(adj_close,adj_open))
        return log_ho*(log_ho-log_co)+log_lo*(log_lo-log_co)
    def _yz(self, today_close, today_open, today_high, today_low, yesterday_close, yesterday_open, yesterday_high, yesterday_low):
        """Yang-Zhang volatility Estimator 
        This is not calculated at the individual record
        date but instead at volatility level. Its basically
        a weighted average of RS, RSY, C2C
        """
        pass
    def _adj_factor(self, close, adj_close):
        """Method to calculate adjustment factor from close prices"""
        return np.divide(adj_close,close)
    def volatility(self, evaluator,evaluator_type, time_period = 30):
        """Method to calculate volatility over time
        :input evaluator: volatility estimator method
        """
        if evaluator_type=='c2c':
            f=np.std
        else:
            f=np.mean
        e=evaluator
        record_cnt = len(e)
        output = []
        for i in range(0,record_cnt - time_period):
            output.append(np.sqrt(np.multiply(252,f(e[i:i+time_period]))))
        return np.asarray(output)
    def getEvaluator(self, getType='c2c'):
        """Method returns volatility estimations for every 
        possible date in dataframe"""
        adjustment_factor=self._adj_factor(self.df['close'].values,self.df['adj_close'])   
        eval_dict = {
            'c2c':lambda df : print('Close 2 Close method not implemented'),#self._c2c(df['close'][1:],df['close'][:-1]),
            'park':lambda df : self._park(df['high'],df['low'],adjustment_factor),
            'gk':lambda df : self._gk(df['close'],df['open'],df['high'],df['low'],adjustment_factor),
            'rsy':lambda df : self._rsy(df['close'],df['open'],df['high'],df['low'],adjustment_factor),
            'yz':lambda df : print('Yang Zhang volatility estimator not implemented')
        }
        return eval_dict.get(getType)(self.df)
    def summary(self,evaluator):
        tbl = SimpleTable(self.summary_data(evaluator),['30','60','90','120'],['max','75%','median','25%','min'],title="Volatility Cone")
        return tbl
    def summary_data(self,evaluator):
        volatility_estimator = self.getEvaluator(evaluator)
        v30 = self.volatility(volatility_estimator,evaluator,30)
        v60 = self.volatility(volatility_estimator,evaluator,60)
        v90 = self.volatility(volatility_estimator,evaluator,90)
        v120 = self.volatility(volatility_estimator,evaluator,120)
        data = [
            [np.max(v30),np.max(v60),np.max(v90),np.max(v120)],
            [np.percentile(v30,75),np.percentile(v60,75),np.percentile(v90,75),np.percentile(v120,75)],
            [np.percentile(v30,50),np.percentile(v60,50),np.percentile(v90,50),np.percentile(v120,50)],
            [np.percentile(v30,25),np.percentile(v60,25),np.percentile(v90,25),np.percentile(v120,25)],
            [np.min(v30),np.min(v60),np.min(v90),np.min(v120)]
        ]
        return data


    