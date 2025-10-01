import json
import os
import hashlib

def load_users():
    """Load user credentials from JSON file"""
    users_file = "data/users.json"
    if not os.path.exists(users_file):
        # Create default users if file doesn't exist
        default_users = {
            "zookeeper": {
                "keeper1": "ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f"  # password123
            },
            "doctor": {
                "doctor1": "b573179ece8c943543550573a9e61f720f48726fddd5b9416cfdc9f351b5972a"  # medpass456
            },
            "admin": {
                "admin1": "435fc140b59fca670b54716967ac7db477ebfe39f136c73b6e38a573d76face0"  # adminpass789
            }
        }
        os.makedirs("data", exist_ok=True)
        with open(users_file, "w") as f:
            json.dump(default_users, f, indent=2)
        return default_users
    
    with open(users_file, "r") as f:
        return json.load(f)

def hash_password(password):
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def authenticate_user(username, password, role):
    """Authenticate user credentials"""
    users = load_users()
    
    if role not in users:
        return False
    
    if username not in users[role]:
        return False
    
    hashed_password = hash_password(password)
    return users[role][username] == hashed_password

def get_user_role(username):
    """Get user role by username"""
    users = load_users()
    for role, user_dict in users.items():
        if username in user_dict:
            return role
    return None

def add_user(username, password, role):
    """Add new user (admin function)"""
    users = load_users()
    
    if role not in users:
        users[role] = {}
    
    hashed_password = hash_password(password)
    users[role][username] = hashed_password
    
    with open("data/users.json", "w") as f:
        json.dump(users, f, indent=2)
    
    return True
