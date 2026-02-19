"""
Check if admin user has delete expense permission
التحقق من أن المستخدم admin لديه صلاحية حذف المصروفات
"""
import sqlite3

# Connect to database
conn = sqlite3.connect('erp_system.db')
cursor = conn.cursor()

print("=" * 80)
print("🔍 التحقق من صلاحية حذف المصروفات")
print("🔍 Checking delete expense permission")
print("=" * 80)

# Check if permission exists
cursor.execute("SELECT id, name, name_ar FROM permissions WHERE name = 'accounting.expenses.delete'")
perm = cursor.fetchone()

if perm:
    print(f"\n✅ الصلاحية موجودة:")
    print(f"   ID: {perm[0]}")
    print(f"   Name: {perm[1]}")
    print(f"   Name AR: {perm[2]}")
    
    perm_id = perm[0]
    
    # Check if admin role has this permission
    cursor.execute("""
        SELECT r.id, r.name, r.name_ar
        FROM roles r
        JOIN role_permissions rp ON r.id = rp.role_id
        WHERE rp.permission_id = ?
    """, (perm_id,))
    
    roles = cursor.fetchall()
    
    if roles:
        print(f"\n✅ الأدوار التي لديها هذه الصلاحية:")
        for role in roles:
            print(f"   - {role[2]} ({role[1]})")
    else:
        print("\n⚠️ لا توجد أدوار لديها هذه الصلاحية!")
        
        # Add to admin role
        cursor.execute("SELECT id FROM roles WHERE name = 'admin'")
        admin_role = cursor.fetchone()
        
        if admin_role:
            print("\n➕ إضافة الصلاحية لدور admin...")
            cursor.execute("""
                INSERT INTO role_permissions (role_id, permission_id)
                VALUES (?, ?)
            """, (admin_role[0], perm_id))
            conn.commit()
            print("✅ تم إضافة الصلاحية لدور admin")
    
    # Check admin user
    cursor.execute("""
        SELECT u.id, u.username, u.role_id, r.name as role_name
        FROM users u
        LEFT JOIN roles r ON u.role_id = r.id
        WHERE u.username = 'admin'
    """)
    admin = cursor.fetchone()
    
    if admin:
        print(f"\n👤 المستخدم admin:")
        print(f"   ID: {admin[0]}")
        print(f"   Username: {admin[1]}")
        print(f"   Role ID: {admin[2]}")
        print(f"   Role Name: {admin[3]}")
        
        if admin[2]:
            # Check if this role has the permission
            cursor.execute("""
                SELECT COUNT(*) FROM role_permissions
                WHERE role_id = ? AND permission_id = ?
            """, (admin[2], perm_id))
            
            has_perm = cursor.fetchone()[0] > 0
            
            if has_perm:
                print(f"\n✅ المستخدم admin لديه صلاحية حذف المصروفات")
            else:
                print(f"\n⚠️ المستخدم admin ليس لديه صلاحية حذف المصروفات")
    else:
        print("\n⚠️ المستخدم admin غير موجود!")
        
else:
    print("\n❌ الصلاحية غير موجودة!")

conn.close()

print("\n" + "=" * 80)
print("✅ تم الانتهاء!")
print("=" * 80)

