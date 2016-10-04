# -*- coding: utf-8 -*-

# import csv
import unicodecsv as csv
import postgresql
from datetime import datetime, timezone, timedelta
import gzip
import io
import os
import sys
import math
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

FILE_DIR = os.environ["FILE_DIR"]

db = postgresql.open("pq://select_only:4v|Jsxb7u!6VJ4auBba)PZ%pm+htw7*nDtqPhiv@192.168.87.8/sf2_bizocean")
#db = postgresql.open("pq://select_only:Ny6dSb7JEBiv@192.168.87.1/sf2_bizocean")

TABLES =[
    {"file_name":"member",
     "sql":"""
        SELECT
    	    m.member_id,
            (SELECT name FROM employee_scale as es WHERE m.employee_scale_id = es.employee_scale_id LIMIT 1) as employee_scale,
    	    (SELECT name FROM prefecture as p WHERE m.company_prefecture_id = p.prefecture_id LIMIT 1) as prefecture,
            (SELECT name FROM managerial_position as mp WHERE m.managerial_position_id = mp.managerial_position_id LIMIT 1) as managerial_position,
            (SELECT name FROM job_specification as js WHERE m.job_specification_id1 = js.job_specification_id LIMIT 1) as job_spec1,
    	    (SELECT name FROM industry as i WHERE m.industry_id = i.industry_id LIMIT 1) as industry,
            (SELECT name FROM annual_profit as ap WHERE m.annual_profit_id = ap.annual_profit_id LIMIT 1) as annual_profit,
    	    m.gender,
    	    m.mail_magazine_status,
            CAST(date_part('year', CURRENT_DATE) - m.birth_year AS INT) as age,
    	    m.last_login_date,
    	    m.create_date
        FROM
            member as m
        ORDER BY
            m.member_id ASC
     """},
    {"file_name":"member_del",
     "sql":"""
        SELECT
            m.member_id,
            (SELECT name FROM employee_scale as es WHERE m.employee_scale_id = es.employee_scale_id LIMIT 1) as employee_scale,
            (SELECT name FROM prefecture as p WHERE m.company_prefecture_id = p.prefecture_id LIMIT 1) as prefecture,
            (SELECT name FROM managerial_position as mp WHERE m.managerial_position_id = mp.managerial_position_id LIMIT 1) as managerial_position,
            (SELECT name FROM job_specification as js WHERE m.job_specification_id1 = js.job_specification_id LIMIT 1) as job_spec1,
            (SELECT name FROM industry as i WHERE m.industry_id = i.industry_id LIMIT 1) as industry,
            (SELECT name FROM annual_profit as ap WHERE m.annual_profit_id = ap.annual_profit_id LIMIT 1) as annual_profit,
            m.gender,
            m.mail_magazine_status,
            CAST(date_part('year', CURRENT_DATE) - m.birth_year AS INT) as age,
            m.last_login_date,
            m.create_date,
            delete_reason,
            m.delete_date
        FROM
            member_del as m
        ORDER BY
            m.member_id ASC
    """},
    {"file_name":"product",
     "sql":"""
        SELECT
            product_id,
            name,
            price,
            original_maker_id,
            create_date
        FROM
            product
        WHERE
            file_status='public'
    """},
    {"file_name":"product_category",
     "sql":"""
        SELECT
            product_category_id,
            product_id,
            category_id
        FROM
            product_category
    """},
    {"file_name":"category",
     "sql":"""
        SELECT
            category_id,
            parent_category_id,
            category_name,
            level,
            rank,
            del_flg
        FROM
            category;
    """},

]

def convert2text(row):
    result_row = []
    r_append = result_row.append
    for i in row:
        if not i:
            r_append("")
        elif isinstance(i, int):
            r_append(str(math.floor(i)))
        elif isinstance(i, str):
            r_append(i)
        elif isinstance(i, bytes):
            r_append(i.decode("utf-8"))
        else:
            r_append(str(i))

    return result_row

def export_csv_gzip(file_name, sql):
    result = result = db.query.rows(sql)
    JST = timezone(timedelta(hours=+9), 'JST')
    now = datetime.now()
    csv_fname = os.path.join(FILE_DIR, now.strftime(file_name + '.csv'))
    gzip_fname = csv_fname + ".gz"
    if os.path.isfile(gzip_fname):
        os.remove(gzip_fname)
    with open(csv_fname, "wb") as f:
        print(file_name + " export csv start")
        writer = csv.writer(f, lineterminator='\n', encoding="utf8")
        for row in result:
            val = convert2text(row)
            writer.writerow(val)
        print(file_name + " export csv end")

    try:
        with open(csv_fname, 'rb') as f_in:
            with gzip.open(gzip_fname, 'wb') as f_out:
                print(file_name + " export gzip start")
                f_out.writelines(f_in)

    except Exception as e:
        print(filename + "gzip error:{}".format(e))
        if os.path.isfile(gzip_fname):
            os.remove(gzip_fname)
    if os.path.isfile(csv_fname):
        os.remove(csv_fname)

for data in TABLES:
    export_csv_gzip(data["file_name"], data["sql"])
