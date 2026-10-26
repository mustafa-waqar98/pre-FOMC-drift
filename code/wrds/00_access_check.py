"""
Report which TAQ tables and years this WRDS account can read. Reads no price
data, only checks permissions. Run on WRDS: python3 00_access_check.py
"""
import wrds

db = wrds.Connection()

print("\nschemas starting with taq:")
print(db.raw_sql("select nspname from pg_namespace where nspname ~ '^taq' order by 1").to_string(index=False))

for schema in ["taq", "taqmsec"]:
    sql = ("select regexp_replace(table_name, '[0-9]{4,}', '#') as pattern, count(*) as n, "
           "min(table_name) as first, max(table_name) as last "
           "from information_schema.tables where table_schema = '%s' "
           "group by 1 order by 1" % schema)
    print("\ntable patterns in", schema)
    print(db.raw_sql(sql).to_string(index=False))


def first_table_per_year(schema):
    sql = ("select table_name from information_schema.tables where table_schema = '%s' "
           "and table_name ~ '^ctm?_[0-9]{8}$'" % schema)
    names = sorted(db.raw_sql(sql)["table_name"].tolist(), key=lambda x: x[-8:])
    out = {}
    for n in names:
        out.setdefault(n[-8:-4], n)
    return out


for schema in ["taq", "taqmsec"]:
    print("\nread access by year in", schema)
    for year, table in first_table_per_year(schema).items():
        try:
            db.raw_sql("select 1 from %s.%s limit 1" % (schema, table))
            print(year, table, "ok")
        except Exception as e:
            print(year, table, "DENIED" if "permission" in str(e) else str(e)[:80])
