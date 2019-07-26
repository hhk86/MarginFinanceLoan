import cx_Oracle
import numpy as np
import pandas as pd
import datetime as dt
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sys


pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)


class OracleSql(object):
    '''
    Query data from database
    '''

    def __init__(self, pt=False):
        '''
        Initialize database
        '''
        self.host, self.oracle_port = '18.210.64.72', '1521'
        self.db, self.current_schema = 'tdb', 'wind'
        self.user, self.pwd = 'reader', 'reader'
        self.pt = pt

    def __enter__(self):
        '''
        Connect to database
        :return: self
        '''
        self.conn = self.__connect_to_oracle()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()

    def __connect_to_oracle(self):
        '''
        Connect to database
        :return: connection
        '''
        dsn = self.host + ':' + self.oracle_port + '/' + self.db
        try:
            connection = cx_Oracle.connect(self.user, self.pwd, dsn, encoding="UTF-8", nencoding="UTF-8")
            connection.current_schema = self.current_schema
            if self.pt is True:
                print('Connected to Oracle database successful!')
        except Exception:
            print('Failed on connecting to Oracle database!')
            connection = None
        return connection

    def query(self, sql: str) -> pd.DataFrame:
        '''
        Query data
        '''
        return pd.read_sql(sql, self.conn)

    def execute(self, sql: str):
        '''
        Execute SQL scripts, including inserting and updating

        '''
        self.conn.cursor().execute(sql)
        self.conn.commit()


class App(QWidget):

    def __init__(self, param_dict):
        super().__init__()
        self.left = 70
        self.top = 200
        self.width = 1800
        self.height = 400
        self.date = param_dict["date"]
        self.marginGroup = param_dict["size"]
        self.marginSorted = param_dict["change"]
        self.title = '转融通分析' + "        日期：" + self.date
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.createGroupTable()
        self.layout = QHBoxLayout()
        self.layout.addWidget(self.groupTable)

        self.createSortTable()
        self.layout.addWidget(self.sortTable)
        self.setLayout(self.layout)

        self.createSortTable2()
        self.layout.addWidget(self.sortTable2)
        self.setLayout(self.layout)

        # Show widget
        self.show()

    def createGroupTable(self):
        self.groupTable = QTableWidget()
        self.groupTable.resize(920, 240)
        self.groupTable.setColumnCount(3)
        self.groupTable.setRowCount(4)
        self.groupTable.setColumnWidth(0, 200)
        self.groupTable.setColumnWidth(4, 200)
        self.groupTable.setItem(0, 0, QTableWidgetItem(self.marginGroup.loc["沪深300", "endBalance"]))
        self.groupTable.setItem(0, 1, QTableWidgetItem(self.marginGroup.loc["沪深300", "balance_pct"]))
        self.groupTable.setItem(0, 2, QTableWidgetItem(self.marginGroup.loc["沪深300", "change"]))
        self.groupTable.setItem(1, 0, QTableWidgetItem(self.marginGroup.loc["中证500", "endBalance"]))
        self.groupTable.setItem(1, 1, QTableWidgetItem(self.marginGroup.loc["中证500", "balance_pct"]))
        self.groupTable.setItem(1, 2, QTableWidgetItem(self.marginGroup.loc["中证500", "change"]))
        self.groupTable.setItem(2, 0, QTableWidgetItem(self.marginGroup.loc["其他股票", "endBalance"]))
        self.groupTable.setItem(2, 1, QTableWidgetItem(self.marginGroup.loc["其他股票", "balance_pct"]))
        self.groupTable.setItem(2, 2, QTableWidgetItem(self.marginGroup.loc["其他股票", "change"]))
        self.groupTable.setItem(3, 0, QTableWidgetItem(self.marginGroup.loc["sum", "endBalance"]))
        self.groupTable.setItem(3, 1, QTableWidgetItem(self.marginGroup.loc["sum", "balance_pct"]))
        self.groupTable.setItem(3, 2, QTableWidgetItem(self.marginGroup.loc["sum", "change"]))
        self.groupTable.setHorizontalHeaderLabels(["金额（万元）", "百分比", "变化量（万元）"])
        self.groupTable.setVerticalHeaderLabels(["沪深300成分股", "中证500成分股", "其他股票", "合计"])
        self.groupTable.move(0, 0)


    def createSortTable(self):
        self.sortTable = QTableWidget()
        self.sortTable.setRowCount(10)
        self.sortTable.setColumnCount(5)
        for i in range(0, 10):
            for j in range(0, 5):
                self.sortTable.setItem(i, j, QTableWidgetItem(self.marginSorted.iloc[- i - 1, j]))
        self.sortTable.setHorizontalHeaderLabels(["股票名称", "股票代码", "变化量(万股)", "借出余额（万元）", "分类"])
        self.sortTable.setVerticalHeaderLabels(["变化量排名" + str(i) for i in range(1,11)])


    def createSortTable2(self):
        self.sortTable2 = QTableWidget()
        self.sortTable2.setRowCount(10)
        self.sortTable2.setColumnCount(5)
        for i in range(0, 10):
            for j in range(0, 5):
                self.sortTable2.setItem(i, j, QTableWidgetItem(self.marginSorted.iloc[i , j]))
        self.sortTable2.setHorizontalHeaderLabels(["股票名称", "股票代码", "变化量(万股)", "借出余额（万元）",  "分类"])
        self.sortTable2.setVerticalHeaderLabels(["变化量排名" + str(i) for i in range(1,11)])


def lowCaseDfColumns(df: pd.DataFrame) -> pd.DataFrame:
    '''
    :param df: pd.DataFrame
    :return: pd.DataFrame
    '''

    df.columns = [s.lower() for s in df.columns]
    return df


def dfItemToStr(df: pd.DataFrame) -> pd.DataFrame:
    '''convert all numbers in a dataframe to str, rounded to 2 digits.'''
    for label in df.index:
        for col in df.columns:
            if type(df.loc[label, col]) is float or type(df.loc[label, col]) is np.float64:
                df.loc[label, col] = str(round(df.loc[label, col], 2))
    return df


def calMarginLoanParam(date: str) -> dict:
    '''
    Get a df of Margin Finance Loans
    :param date: str, "yyyymmdd"
    :return: dict, dictionary of parameters
    '''
    tradingDay_list = getTradingDays("20120101", "20190719")
    date_lag1 = tradingDay_list[tradingDay_list.index(date) - 1]
    marginLoan = getMarginLoan(date)
    marginLoan_lag1 = getMarginLoan(date_lag1)
    marginLoan = pd.merge(marginLoan, marginLoan_lag1, left_index=True, right_index=True, how="left")
    marginLoan = marginLoan[["endVol_y", "balance_y", "sell_x", "repay_x", "endVol_x", "balance_x"]]
    marginLoan.columns = ["startVol", "startBalance", "sell", "repay", "endVol", "endBalance"]
    for label in marginLoan.index:
        if np.isnan(marginLoan.loc[label, "startVol"]):
            marginLoan.loc[label, "startVol"] = marginLoan.loc[label, "endVol"] + marginLoan.loc[label, "repay"] - \
                                                marginLoan.loc[label, "sell"]
            marginLoan.loc[label, "startBalance"] = marginLoan.loc[label, "endBalance"] / marginLoan.loc[
                label, "endVol"] * marginLoan.loc[label, "startVol"]
    marginLoan["change"] = marginLoan["endVol"].squeeze().sub(marginLoan["startVol"].squeeze())
    HS_list = getIndexConstituent(date, index="HS")
    CSI_list = getIndexConstituent(date, index="CSI")
    marginLoan["group"] = "其他股票"
    for label in marginLoan.index:
        if label in HS_list:
            marginLoan.loc[label, "group"] = "沪深300" #"HS"
        if label in CSI_list:
            marginLoan.loc[label, "group"] = "中证500"  #"CSI"
    marginGroup = marginLoan.groupby("group").sum()
    marginGroup["balance_pct"] = marginGroup.endBalance / marginGroup.endBalance.sum()
    marginSorted = marginLoan.sort_values(by="change")
    marginGroup = marginGroup[["endBalance", "change", "balance_pct"]]
    marginGroup.balance_pct *= 100
    marginGroup.loc["sum"] = [marginGroup.endBalance.sum(), marginGroup.change.sum(),
                                   marginGroup.balance_pct.sum()]
    marginGroup = dfItemToStr(marginGroup)
    marginSorted = marginSorted[["endVol", "change", "group"]]
    stockName_df = getStockName()
    marginSorted = pd.merge(marginSorted, stockName_df, left_index=True, right_index=True)
    marginSorted["code"] = marginSorted.index
    marginSorted.columns = ["endVol", "change", "group", "stockName", "code"]
    marginSorted = marginSorted[["stockName", "code",  "change", "endVol", "group"]]
    marginSorted = dfItemToStr(marginSorted)
    # for label in marginSorted:
    #     if marginSorted.loc[label, "group"] == "HS"
    param_dict = {"size": marginGroup, "change": marginSorted, "date": date}
    return param_dict


def getTradingDays(startDate: str, endDate: str) -> list:
    sql = \
        '''
        SELECT
        ''' + '''
	TRADE_DAYS 
    FROM
        asharecalendar 
    WHERE
        S_INFO_EXCHMARKET = 'SSE' 
        AND trade_days BETWEEN {} AND {}
    '''.format(startDate, endDate)
    with OracleSql() as oracle:
        tradingDays = oracle.query(sql)
    return list(tradingDays.TRADE_DAYS)


def getMarginLoan(date: str) -> pd.DataFrame:
    '''
    Get and calculate daily margin finance loan data.
    startVol = endvol + repay - sell.
    In Fact, the above calculation method is not accurate because it omits some repayments.
    Besides, the open price and close price of individual stocks is different. So it is hard to calculate the start balance in this way.
    Therefore, in function "getMarginLoanParam", a more accurate way is to replace the startVol with the previous day's endVol and use the previous balance as the start balance.

    :param date: str, "yyyymmdd"
    :return: pd.DataFrame
    '''

    sql = \
        '''
        SELECT
        ''' + '''
        S_INFO_WINDCODE, TRADE_DT, S_REFIN_SB_EOD_VOL, S_REFIN_SL_EOP_VOL,
        S_REFIN_SL_EOP_BAL, S_REFIN_REPAY_VOL
    FROM 
        AShareMarginTrade
    WHERE
        TRADE_DT = {}
        AND S_REFIN_SL_EOP_VOL IS NOT NULL
    ORDER BY
        S_INFO_WINDCODE
    '''.format(date)

    with OracleSql() as oracle:
        marginData = oracle.query(sql)
    marginData = lowCaseDfColumns(marginData)
    marginData.fillna(0, inplace=True)
    marginData.set_index("s_info_windcode", inplace=True)
    marginData.columns = ["trade_dt", "sell", "endVol", "balance", "repay"]
    marginData.endVol /= 10000
    marginData.sell /= 10000
    marginData.repay /= 10000
    marginData.balance /= 10000
    marginData["startVol"] = marginData.endVol + marginData.repay - marginData.sell
    marginData = marginData[["startVol", "sell", "repay", "endVol", "balance"]]
    return marginData


def getIndexConstituent(date: str, index: str) -> list:
    '''
    get CSI 500 constituent stocks' code list
    :param date: str, "yyyymmdd"
    :param index: str, "SH" for 沪深300 and "CSI" for 中证500
    :return: list
    '''
    if index == "CSI":
        sql = \
            '''
               SELECT
               ''' + '''
                    *
               FROM
                    aindexcsi500weight
               WHERE
                    TRADE_DT = {}
            '''.format(date)
    elif index == "HS":
        sql = \
            '''
               SELECT
               ''' + '''
                    *
               FROM
                    AIndexHS300Weight
               WHERE
                    TRADE_DT = {}
            '''.format(date)
    else:
        raise ValueError("Parameter Error!")
    with OracleSql() as oracle:
        SCI500WeightData = oracle.query(sql)
    return list(SCI500WeightData.S_CON_WINDCODE)


def getStockName() -> pd.DataFrame:
    sql = \
        '''
        SELECT
        ''' + '''
    S_INFO_WINDCODE, S_INFO_NAME as stockName
    FROM
    AShareDescription
    '''
    with OracleSql() as oracle:
        stockName_df = oracle.query(sql)
    stockName_df.set_index("S_INFO_WINDCODE", inplace=True)
    return stockName_df


if __name__ == '__main__':
    param_dict = calMarginLoanParam("20190719")
    app = QApplication(sys.argv)
    myTable= App(param_dict)
    myTable.show()
    app.exit(app.exec_())
