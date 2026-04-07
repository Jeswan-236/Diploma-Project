import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load env
env_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path=env_path)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Supabase credentials not found")
    exit(1)

print("🔗 Connecting to Supabase...")

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("✅ Connected successfully!")
    
    # Get all users
    response = supabase.table("users").select("*").execute()
    users = response.data
    
    print(f"\n👥 Total users: {len(users)}")
    
    if users:
        print("\n📋 Users in database:")
        print("-" * 80)
        for user in users:
            admin_badge = "👑 ADMIN" if user.get('is_admin') else "👤 USER "
            profile_data = "✓" if user.get('profile_data') else "✗"
            print(f"{admin_badge} | {user['username']:20} | {user['email']:30} | Profile: {profile_data}")
        print("-" * 80)
        
        # Show sample user columns
        if users:
            sample = users[0]
            print("\n🔍 User record structure:")
            for key, value in sample.items():
                value_preview = str(value)[:50] if value else "NULL"
                print(f"  • {key}: {type(value).__name__} = {value_preview}")
    else:
        print("  No users found in database")
    
    print("\n✅ Database scan complete")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
