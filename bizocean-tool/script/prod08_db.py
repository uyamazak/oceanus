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

db = postgresql.open("pq://select_only:hogehoge@192.168.87.8/sf2_bizocean")
#db = postgresql.open("pq://select_only:Ny6dSb7JEBiv@192.168.87.1/sf2_bizocean")


def get_query_result(table_name):
    del_column = ""
    if table_name == "member_del":
        del_column = """,
            delete_reason,
            m.delete_date
        """
    result = db.query.rows("""
    SELECT
    	m.member_id,
        (SELECT name FROM employee_scale as es WHERE m.employee_scale_id = es.employee_scale_id LIMIT 1) as employee_scale,
    	(SELECT name FROM prefecture as p WHERE m.company_prefecture_id = p.prefecture_id LIMIT 1) as prefecture,
        (SELECT name FROM job_specification as js WHERE m.job_specification_id1 = js.job_specification_id LIMIT 1) as job_spec1,
    	(SELECT name FROM industry as i WHERE m.industry_id = i.industry_id LIMIT 1) as industry,
        (SELECT name FROM annual_profit as ap WHERE m.annual_profit_id = ap.annual_profit_id LIMIT 1) as annual_profit,
    	m.gender,
    	m.mail_magazine_status,
        CAST(date_part('year', CURRENT_DATE) - m.birth_year AS INT) as age,
    	m.last_login_date,
    	m.create_date
        """
        + del_column +
        """
    FROM """
        + table_name +
    """ as m
    ORDER BY m.member_id ASC
    """)
    return result

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

def export_csv_gzip(table_name):
    result = get_query_result(table_name)
    JST = timezone(timedelta(hours=+9), 'JST')
    now = datetime.now()
    csv_fname = os.path.join(FILE_DIR, now.strftime(table_name + '_%Y-%m-%d-%H%M%S.csv'))
    gzip_fname = csv_fname + ".gz"

    with open(csv_fname, "wb") as f:
        print("export csv start")
        writer = csv.writer(f, lineterminator='\n', encoding="utf8")
        for row in result:
            val = convert2text(row)
            writer.writerow(val)
        print("export csv end")

    try:
        with open(csv_fname, 'rb') as f_in:
            with gzip.open(gzip_fname, 'wb') as f_out:
                print("export gzip start")
                f_out.writelines(f_in)

    except Exception as e:
        print("gzip error:{}".format(e))
        os.remove(gzip_fname)
    os.remove(csv_fname)

for table_name in ("member", "member_del"):
    export_csv_gzip(table_name)
