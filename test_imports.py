#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_manager.settings')
django.setup()

# Test imports
try:
    from projects import views
    print("✅ Views module imported successfully")
    
    # Check for required functions
    required_functions = [
        'dashboard', 'project_list', 'create_project', 'project_detail',
        'edit_project', 'delete_project', 'project_members', 'invite_member', 'project_board'
    ]
    
    missing_functions = []
    for func_name in required_functions:
        if hasattr(views, func_name):
            print(f"✅ {func_name} - Found")
        else:
            print(f"❌ {func_name} - Missing")
            missing_functions.append(func_name)
    
    if missing_functions:
        print(f"\n❌ Missing functions: {missing_functions}")
    else:
        print("\n✅ All required functions are present")
        
    # Test the safe_delete import
    try:
        from projects.safe_delete import safe_delete_project
        print("✅ safe_delete_project imported successfully")
    except Exception as e:
        print(f"❌ Error importing safe_delete_project: {e}")
        
except Exception as e:
    print(f"❌ Error importing views: {e}")
    import traceback
    traceback.print_exc()
