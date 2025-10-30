"""
Script to create default admin user
Run this once to initialize the admin account
"""
import asyncio
import sys
import os

# Add backend directory to path
backend_dir = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, backend_dir)

# Load environment variables
try:
    from dotenv import load_dotenv
    env_path = os.path.join(backend_dir, '.env')
    load_dotenv(env_path)
    print(f"✅ Loaded environment from: {env_path}")
except ImportError:
    print("⚠️  python-dotenv not installed")

from backend.auth.service import AuthService

async def create_admin():
    """Create default admin user"""
    print("🔧 Initializing admin user creation...")
    
    auth_service = AuthService()
    await auth_service.create_default_admin()
    
    print("\n✅ Admin setup complete!")
    print("\n📧 Email: admin@finguard.com")
    print("🔑 Password: admin123")
    print("\n⚠️  IMPORTANT: Change the default password immediately after first login!")

if __name__ == "__main__":
    asyncio.run(create_admin())
