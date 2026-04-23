import os
from datetime import timedelta
from flask import Flask
from flask_jwt_extended import JWTManager, create_access_token
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
# Use the same JWT secret as your app
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'default-dev-jwt-secret-key')
jwt = JWTManager(app)

def generate_admin_token():
    with app.app_context():
        # This creates a token that lasts for 6 months (180 days)
        expires = timedelta(days=180)
        additional_claims = {"role": "admin"}
        token = create_access_token(identity="admin", additional_claims=additional_claims, expires_delta=expires)
        
        print("\n" + "="*60)
        print("YOUR LONG-LIVED ADMIN TOKEN:")
        print("="*60)
        print(token)
        print("="*60)
        print("\nCopy this token and add it to your GitHub Secrets as 'ADMIN_TOKEN'")

if __name__ == "__main__":
    generate_admin_token()
