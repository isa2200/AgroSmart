import MySQLdb
import sys

def check(user, password, port):
    try:
        db = MySQLdb.connect(host="localhost", user=user, passwd=password, port=port)
        print(f"SUCCESS: {user}@{port}")
        db.close()
        return True
    except Exception as e:
        print(f"FAIL: {user}@{port} - {e}")
        return False

print("Checking DB credentials...")
check("root", "", 3306)
check("agrosmart_user", "agrosmart_pass", 3306)
check("agrosmart_user", "", 3306)
