import json

# client side login and register
def client_login():
    # ask client for username and password
    username = input('Username: ')
    password = input('Password: ')
    return username, password

def client_register():
    # ask client for username and password
    username = input('Username: ')
    password = input('Password: ')
    return username, password

# server side client account validation
def validate_client(username, password):
    # check if username and password matches an account
    # return True if valid, False otherwise
    json_filename = 'accounts.json'

    try:
        with open(json_filename, 'r') as f:
            accounts = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return False
    
    if username in accounts:
        if accounts[username]['password'] == password:
            return True
    
    return False

# server side client account registration
def register_client(username, password):
    # register client account
    # return True if successful, False otherwise
    json_filename = 'accounts.json'

    try:
        with open(json_filename, 'r') as f:
            accounts = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        accounts = {}
    
    if username in accounts:
        print(f"Username: '{username}' already exists. Registration failed.")
        return False
    
    accounts[username] = {'password': password}

    with open(json_filename, 'w') as f:
        json.dump(accounts, f, indent=4)
    
    print(f"Username: '{username}' successfully registered.")
    return True