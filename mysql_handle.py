# -*- coding: utf-8 -*-
"""
FileIntro: MySQL management

Created on Fri Jul 24 00:55:43 2020

@author: Archer Zhu
"""

'''
Intro:
    Open/Close mysql:
        CMD: net start mysql/ net stop mysql
'''

from sqlalchemy import create_engine
import pymysql
import logging


logger = logging.getLogger('SQL')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')  
ch = logging.StreamHandler()
logger.addHandler(ch)  
ch.setFormatter(formatter)  
#fh = logging.FileHandler('SQL.log')  
#fh.setFormatter(formatter)  
#logger.addHandler(fh)  

engine_local = create_engine('mysql+pymysql://root:121212@localhost:3306/usstock?charset=utf8') # for sqlalchemy engine
conn_local = {'host': "localhost", 'user': "root", 'password': "121212", 'db': 'usstock'} # for pymysql conn

def save_to_mysql(engine ,data, table, if_exists = 'append'):
    '''Use pd.DataFrame to upload table info(append method)
    engine: create_engine object, create_engine('mysql+pymysql://root:121212@localhost:3306/hulk?charset=utf8')
    data: pd.DataFrame
    table: table name in mysql
    if_exists: ‘fail’, ‘replace’, ‘append’
    '''
    conn = engine.connect()
    try:
        data.to_sql(name = table, con = conn, if_exists = if_exists, index = False)
    except Exception as e:
        logger.debug('Saving Ratio Error: {} \n {}'.format(repr(e),data))
#        conn.rollback()  # Connection object has no attribute rollback
    finally:
        conn.close()

def pymysql_execution(conn_info, sql):
    '''mysql query execution
    conn_info: {'host': "localhost", 'user': "root", 'password': "121212", 'db': 'Hulk'}
    sql: str
    '''
    # 目标数据库
    db_t = pymysql.connect(**conn_info)
    # 使用 cursor() 方法创建游标对象 cursor
    cursor_t = db_t.cursor()
    try:
        cursor_t.execute(sql)
        logger.info('pymysql_execution:Execution Success.')
    except Exception as e:
        logger.info('pymysql_execution:' + e)
#        print('Data already exists!', e)
#        pass
    # 提交事务
    db_t.commit()
    db_t.close()


#
## Engines(sqlalchemy)
#engine_upload = engine_local
## Engines(pymysql)
#conn_upload = conn_local
## SQL related
#sql_InsertIgnore_dirty = "INSERT IGNORE into dirtydata" \
#          "(metric_id, rquarter, stock_code, value, priority, unique_key, industry" \
#          ")SELECT metric_id, rquarter, stock_code, value, priority, unique_key, industry "\
#          "FROM datatemp"
#sql_InsertIgnore_ratio =    "INSERT IGNORE into fin_ratio_cn" \
#              "(Ratioid, rquarter, stock_code, unique_key, value" \
#              ")SELECT Ratioid, rquarter, stock_code, unique_key, value "\
#              "FROM ratiotemp"
#sql_truncate_data = "TRUNCATE TABLE datatemp" 
#sql_truncate_ratio = "TRUNCATE TABLE ratiotemp" 
#if flag_quarter == True:
#    sql_get_TA = "select stock_code, rquarter from cninfo_stockmetrics_0 where metric_id = '38' and rquarter in " + str(tuple(qlist))  #TAlist匹配rawdata
#else:
#    sql_get_TA = "select stock_code, rquarter from cninfo_stockmetrics_0 where metric_id = '38'" #TAlist匹配rawdata
#sql_get_f2 = "select stock_code, vary_date, f2 from stock_industry_code_cn where standard = '申银万国行业分类标准'"
#sql_get_ratio_cal = "select * from ratio_cal_method"
#sql_get_relevant_id = "select * from ratio_metric"

