"""
Script to add tenant_id to remaining models
This script updates all remaining model files with tenant_id support
"""

import re

# Models to update with their files
models_to_update = {
    'app/models_accounting.py': [
        'Account', 'JournalEntry', 'JournalEntryItem', 'Payment', 
        'BankAccount', 'CostCenter', 'BankTransaction', 'Expense'
    ],
    'app/models_hr.py': [
        'Employee', 'Department', 'Position', 'Attendance', 
        'Leave', 'LeaveType', 'Payroll'
    ],
    'app/models_pos.py': [
        'POSSession', 'POSOrder', 'POSOrderItem'
    ],
    'app/models_settings.py': [
        'SystemSettings', 'AccountingSettings'
    ],
    'app/models_crm.py': [
        'Lead', 'Interaction', 'Opportunity', 'Task', 'Campaign', 'Contact'
    ]
}

# Fields that should have unique constraints with tenant_id
unique_fields = ['code', 'number', 'name', 'email']

def add_tenant_id_to_model(file_path):
    """Add tenant_id to all models in a file"""
    
    print(f"\n{'='*60}")
    print(f"Processing: {file_path}")
    print(f"{'='*60}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find all class definitions
        class_pattern = r'class\s+(\w+)\(db\.Model\):'
        classes = re.findall(class_pattern, content)
        
        print(f"Found {len(classes)} models: {', '.join(classes)}")
        
        for class_name in classes:
            # Check if tenant_id already exists
            if f'class {class_name}' in content:
                class_section = content.split(f'class {class_name}')[1].split('class ')[0]
                
                if 'tenant_id' in class_section:
                    print(f"  ✓ {class_name} - Already has tenant_id")
                    continue
                
                # Find the id field and add tenant_id after it
                pattern = f'(class {class_name}\\(db\\.Model\\):.*?__tablename__ = .*?\\n.*?id = db\\.Column\\(db\\.Integer, primary_key=True\\))'
                
                replacement = r'\1\n    \n    # Multi-Tenant Support\n    tenant_id = db.Column(db.Integer, db.ForeignKey(\'tenants.id\'), nullable=True, index=True)'
                
                new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
                
                if new_content != content:
                    content = new_content
                    print(f"  ✓ {class_name} - Added tenant_id")
                else:
                    print(f"  ✗ {class_name} - Could not add tenant_id (pattern not matched)")
        
        # Write back
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"\n✅ Successfully updated {file_path}")
        
    except FileNotFoundError:
        print(f"\n❌ File not found: {file_path}")
    except Exception as e:
        print(f"\n❌ Error processing {file_path}: {str(e)}")

def main():
    print("\n" + "="*60)
    print("MULTI-TENANT MODEL UPDATER")
    print("="*60)
    print("\nThis script will add tenant_id to all remaining models")
    print("\nFiles to update:")
    for file_path, models in models_to_update.items():
        print(f"  - {file_path}: {len(models)} models")
    
    input("\nPress Enter to continue...")
    
    for file_path in models_to_update.keys():
        add_tenant_id_to_model(file_path)
    
    print("\n" + "="*60)
    print("✅ ALL MODELS UPDATED!")
    print("="*60)
    print("\nNext steps:")
    print("1. Review the changes in each file")
    print("2. Add unique constraints where needed")
    print("3. Run database migration")
    print("4. Test the application")

if __name__ == '__main__':
    main()

