from monitor import *


sql = \
    '''
       SELECT
       ''' + '''
            S_INFO_WINDCODE, TRADE_DT, S_REFIN_SB_EOD_VOL, S_REFIN_SL_EOP_VOL,
        S_REFIN_SL_EOP_BAL, S_REFIN_REPAY_VOL
       FROM
            AShareMarginTrade
       where
            TRADE_DT = 20190719
    '''
sql = \
'''
SELECT
''' + '''
S_INFO_CODE, S_INFO_NAME
FROM
AShareDescription
'''
with OracleSql() as oracle:
    data = oracle.query(sql)
# print(data.head())
# print(data.columns)
# print(len(data))
# print(data)


sql = \
    '''
    SELECT
    ''' + '''
    a.trade_dt,
    a.s_con_windcode,
    b.S_INFO_WINDCODE,
    b.S_INFO_NAME,
    a.tot_shr,
    a.free_shr_ratio,
    a.shr_calculation,
    a.closevalue,
    a.open_adjusted,
    a.weight 
    FROM
    aindexcsi500weight a, ASHAREDESCRIPTION b 
    WHERE
    trade_dt = {} 
    AND a.S_CON_WINDCODE = b.S_INFO_WINDCODE  
'''.format("20190719")
with OracleSql() as oracle:
    daily500Data = oracle.query(sql)
print(daily500Data)
