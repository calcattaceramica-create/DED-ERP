"""
Add expense delete permission
إضافة صلاحية حذف المصروفات
"""
import sqlite3

# Connect to database
conn = sqlite3.connect('erp_system.db')
cursor = conn.cursor()

print("=" * 80)
print("🔧 إضافة صلاحية حذف المصروفات")
print("🔧 Adding expense delete permission")
print("=" * 80)

# Check if permission already exists
cursor.execute("SELECT id, name, name_ar FROM permissions WHERE name = 'accounting.expenses.delete'")
existing = cursor.fetchone()

if existing:
    print(f"\n✅ الصلاحية موجودة بالفعل: {existing[1]} - {existing[2]}")
    print(f"✅ Permission already exists: {existing[1]} - {existing[2]}")
else:
    print("\n➕ إضافة صلاحية جديدة...")
    print("➕ Adding new permission...")
    
    # Add the permission
    cursor.execute("""
        INSERT INTO permissions (name, name_ar, module)
        VALUES ('accounting.expenses.delete', 'حذف المصروفات', 'accounting')
    """)
    conn.commit()
    
    # Get the new permission ID
    cursor.execute("SELECT id FROM permissions WHERE name = 'accounting.expenses.delete'")
    perm_id = cursor.fetchone()[0]
    
    print(f"✅ تم إضافة الصلاحية بنجاح (ID: {perm_id})")
    print(f"✅ Permission added successfully (ID: {perm_id})")
    
    # Add permission to admin role
    print("\n🔗 ربط الصلاحية بدور admin...")
    print("🔗 Linking permission to admin role...")
    
    # Get admin role
    cursor.execute("SELECT id FROM roles WHERE name = 'admin'")
    admin_role = cursor.fetchone()
    
    if admin_role:
        role_id = admin_role[0]
        
        # Check if already linked
        cursor.execute("""
            SELECT id FROM role_permissions 
            WHERE role_id = ? AND permission_id = ?
        """, (role_id, perm_id))
        
        if not cursor.fetchone():
            cursor.execute("""
                INSERT INTO role_permissions (role_id, permission_id)
                VALUES (?, ?)
            """, (role_id, perm_id))
            conn.commit()
            print(f"✅ تم ربط الصلاحية بدور admin")
            print(f"✅ Permission linked to admin role")
        else:
            print("ℹ️  الصلاحية مربوطة بالفعل بدور admin")
            print("ℹ️  Permission already linked to admin role")
    else:
        print("⚠️ دور admin غير موجود!")
        print("⚠️ Admin role not found!")

# Also add accounting.expenses.create permission if missing
print("\n🔍 التحقق من صلاحية إضافة المصروفات...")
print("🔍 Checking expense create permission...")

cursor.execute("SELECT id FROM permissions WHERE name = 'accounting.expenses.create'")
if not cursor.fetchone():
    print("➕ إضافة صلاحية إضافة المصروفات...")
    cursor.execute("""
        INSERT INTO permissions (name, name_ar, module)
        VALUES ('accounting.expenses.create', 'إضافة المصروفات', 'accounting')
    """)
    conn.commit()
    
    # Link to admin role
    cursor.execute("SELECT id FROM permissions WHERE name = 'accounting.expenses.create'")
    perm_id = cursor.fetchone()[0]
    
    cursor.execute("SELECT id FROM roles WHERE name = 'admin'")
    admin_role = cursor.fetchone()
    
    if admin_role:
        cursor.execute("""
            INSERT INTO role_permissions (role_id, permission_id)
            VALUES (?, ?)
        """, (admin_role[0], perm_id))
        conn.commit()
        print("✅ تم إضافة صلاحية إضافة المصروفات")
else:
    print("✅ صلاحية إضافة المصروفات موجودة")

conn.close()

print("\n" + "=" * 80)
print("✅ تم الانتهاء!")
print("✅ Done!")
print("=" * 80)

