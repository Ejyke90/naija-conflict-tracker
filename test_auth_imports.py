#!/usr/bin/env python3
"""
Test script to check if auth.py has any import or syntax errors.
"""

import sys
import os

# Add backend path
sys.path.append('/Users/ejikeudeze/AI_Projects/naija-conflict-tracker/backend')

try:
    from app.api.v1.endpoints.auth import register, login
    print("✅ Auth endpoints imported successfully")
    
    from app.repositories.user_repository import user_repo
    print("✅ User repository imported successfully")
    
    # Test if sync methods exist
    if hasattr(user_repo.__class__, 'get_by_email_sync'):
        print("✅ get_by_email_sync method exists")
    else:
        print("❌ get_by_email_sync method missing")
        
    if hasattr(user_repo.__class__, 'create_user_sync'):
        print("✅ create_user_sync method exists")
    else:
        print("❌ create_user_sync method missing")
        
    if hasattr(user_repo.__class__, 'update_last_login_sync'):
        print("✅ update_last_login_sync method exists")
    else:
        print("❌ update_last_login_sync method missing")
        
    print("✅ All imports and methods validated successfully")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()