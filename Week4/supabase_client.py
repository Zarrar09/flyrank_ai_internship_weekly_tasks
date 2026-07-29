import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_KEY or not SUPABASE_URL:
    raise RuntimeError("SUPABASE_KEY and SUPABASE_URL must be setup in .env")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)