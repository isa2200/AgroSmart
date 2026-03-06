
import MySQLdb
import sys

def check(host, port, user, password):
    print(f"Testing {user}:{password}@{host}:{port} ...", end=" ")
    try:
        db = MySQLdb.connect(host=host, user=user, passwd=password, port=port)
        print("SUCCESS")
        db.close()
        return True
    except Exception as e:
        print(f"FAILED: {e}")
        return False

creds = [
    ("agrosmart_user", "agrosmart_pass"),
    ("root", "super_root_password"),
    ("root", ""),
    ("root", "root"),
    ("agrosmart_user", ""),
]

ports = [3306, 3307]

found = False
for port in ports:
    for user, password in creds:
        if check("localhost", port, user, password):
            print(f"FOUND VALID CREDENTIALS: {user}:{password}@{port}")
            found = True
            break
    if found:
        break

if not found:
    print("No valid credentials found.")
