from server import get_all_users, echo

# 🔧 Echo tool test
print("🔁 Echo Test:")
print(echo("Hello from test script"))

# 🧠 DB tool test
print("\n📦 Users from Database:")
users = get_all_users()
for user in users:
    print(f"ID: {user['id']}, Name: {user['name']}")
