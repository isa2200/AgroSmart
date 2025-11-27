try:
    import MySQLdb  # type: ignore
except Exception:
    import pymysql
    pymysql.install_as_MySQLdb()