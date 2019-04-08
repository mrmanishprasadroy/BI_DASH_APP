import cx_Oracle
import pandas as pd
import numpy as np

conn_info = {
    'host': '10.182.50.108',
    # 'host': '10.18.1.80',
    'port': 1521,
    'user': 'JSWTPM',
    'psw': 'JSWTPM',
    'service': 'PRO.WORLD'
}

CONN_STR = '{user}/{psw}@{host}:{port}/{service}'.format(**conn_info)


class DB:

    def __init__(self):
        pass
         # self.conn = cx_Oracle.connect(CONN_STR)

    def query(self, query):
        try:
            conn = cx_Oracle.connect(CONN_STR)
            df = pd.read_sql_query(con=conn, sql=query)
            return df
        except cx_Oracle.DatabaseError as e:
            print(e)
            conn.close()
        finally:
            conn.close()

    def dict_to_df(self, query_result, date=True):
        items = {
            val: dict(query_result["records"][val])
            for val in range(query_result["totalSize"])
        }
        df = pd.DataFrame.from_dict(items, orient="index").drop(["attributes"], axis=1)

        if date:  # date indicates if the df contains datetime column
            df["CreatedDate"] = pd.to_datetime(df["CreatedDate"], format="%Y-%m-%d")  # convert to datetime
            df["CreatedDate"] = df["CreatedDate"].dt.strftime('%Y-%m-%d')  # reset string
            print(df.head())
        return df

    def get_production(self):
        query_text = """
                        SELECT  PT.COILIDOUT AS COILIDOUT,PT.COILIDIN_1 AS COILIDIN,PT.ALLOYCODE AS ALLOYCODE,PT.ENTRYTHICK, 
                        round(PT.EXITTHICK,2) as EXITTHICK , OT.ENTRYWIDTH,PT.ENTRYDIAMPDI,PT.EXITWEIGHTCALC as EXITWEIGHTMEAS,
                        TO_CHAR(FROM_TZ(PT.DTWELDED, 'UTC') AT TIME ZONE SESSIONTIMEZONE, 'DD.MM.YY hh24:mi') AS DTSTARTROLL,
                        TO_CHAR(FROM_TZ(PT.DTDEPARTURE, 'UTC') AT TIME ZONE SESSIONTIMEZONE, 'DD.MM.YY hh24:mi') AS DTDEPARTURE,
                        TO_CHAR(FROM_TZ(PT.DTENDROLLING, 'UTC') AT TIME ZONE SESSIONTIMEZONE, 'DD.MM.YY hh24:mi') AS DTENDROLLING,
                        (SELECT RZT.LENGTHPHASEEXIT FROM RESULT_ZONE_TAB RZT WHERE COILIDOUT = PT.COILIDOUT AND NZONE = 1) AS LENGTHPHASEEXIT,
                        (SELECT RZT.LENGTHTHICKTOL FROM RESULT_ZONE_TAB RZT WHERE COILIDOUT = PT.COILIDOUT AND NZONE = 1) AS LENGTHTHICKTOL
                        FROM PRODUCTION_TAB PT, ORDER_TAB OT WHERE PT.COILIDIN_1 = OT.COILID AND PT.ALLOYCODE = OT.ALLOYCODE
                     """
        try:
            query_result = self.query(query_text)
        except cx_Oracle.DatabaseError as e:
            print(e)
        # Fill Weight value to mean value or previous value
        query_result = query_result.replace('', np.nan)
        mean_weight = query_result['EXITWEIGHTMEAS'].mean(skipna=True)
        query_result.loc[query_result.EXITWEIGHTMEAS == 0, 'EXITWEIGHTMEAS'] = mean_weight
        query_result['EXITTHICK'] = query_result['EXITTHICK'].apply(lambda x: np.round(x, decimals=2))
        query_result['EXITWEIGHTMEAS'] = query_result['EXITWEIGHTMEAS'].apply(lambda x: np.round(x, decimals=2))
        print(query_result.head())
        return query_result

    def get_stoptime(self):
        query_text = """
                        SELECT NPLANTTYPE AS Plant,DTSTART, DTEND,NDELAYCODE,DELAYCOMMENT,COILID1,DTSTORE FROM STOP_TIME_TAB WHERE DTEND IS NOT NULL
                     """

        try:
            query_result = self.query(query_text)
        except cx_Oracle.DatabaseError as e:
            print(e)
        query_result.set_index(['DTSTORE'], inplace=True)
        print(query_result)
        return query_result
