"""
Automatic Migration Runner
Runs the migration with automatic 'yes' responses
"""

import sys
import os
from unittest.mock import patch

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def mock_input(prompt):
    """Mock input function that always returns 'yes'"""
    print(prompt + "yes")
    return "yes"

if __name__ == '__main__':
    print("=" * 70)
    print("  AUTOMATIC MIGRATION RUNNER")
    print("=" * 70)
    print()
    print("This script will automatically run the migration with 'yes' responses")
    print()
    
    # Patch the input function
    with patch('builtins.input', side_effect=mock_input):
        try:
            # Import and run the migration
            from migrate_to_multitenant import main
            main()
        except Exception as e:
            print(f"\n[ERROR] Migration failed: {str(e)}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

