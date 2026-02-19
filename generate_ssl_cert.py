#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
إنشاء شهادة SSL ذاتية التوقيع للتطوير المحلي
Generate self-signed SSL certificate for local development
"""

import os
import sys
from datetime import datetime, timedelta

def generate_ssl_certificate():
    """إنشاء شهادة SSL ذاتية التوقيع"""
    
    print("=" * 100)
    print("🔒 إنشاء شهادة SSL ذاتية التوقيع")
    print("🔒 Generating Self-Signed SSL Certificate")
    print("=" * 100)
    
    try:
        from cryptography import x509
        from cryptography.x509.oid import NameOID
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.asymmetric import rsa
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.backends import default_backend
    except ImportError:
        print("\n❌ خطأ: مكتبة cryptography غير مثبتة")
        print("❌ Error: cryptography library not installed")
        print("\n📦 قم بتثبيتها باستخدام:")
        print("📦 Install it using:")
        print("\n   pip install cryptography\n")
        return False
    
    # إنشاء مجلد ssl إذا لم يكن موجود
    ssl_dir = os.path.join(os.path.dirname(__file__), 'ssl')
    if not os.path.exists(ssl_dir):
        os.makedirs(ssl_dir)
        print(f"\n✅ تم إنشاء مجلد: {ssl_dir}")
    
    cert_file = os.path.join(ssl_dir, 'cert.pem')
    key_file = os.path.join(ssl_dir, 'key.pem')
    
    print("\n1️⃣ إنشاء المفتاح الخاص (Private Key)...")
    print("   Generating private key...")
    
    # إنشاء المفتاح الخاص
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    
    print("   ✅ تم إنشاء المفتاح الخاص (2048 bit RSA)")
    
    print("\n2️⃣ إنشاء الشهادة (Certificate)...")
    print("   Generating certificate...")
    
    # معلومات الشهادة
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, u"SA"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"Riyadh"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, u"Riyadh"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"DED ERP System"),
        x509.NameAttribute(NameOID.COMMON_NAME, u"localhost"),
    ])
    
    # إنشاء الشهادة
    cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        private_key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.utcnow()
    ).not_valid_after(
        # صالحة لمدة سنة
        datetime.utcnow() + timedelta(days=365)
    ).add_extension(
        x509.SubjectAlternativeName([
            x509.DNSName(u"localhost"),
            x509.DNSName(u"127.0.0.1"),
            x509.DNSName(u"*.localhost"),
        ]),
        critical=False,
    ).sign(private_key, hashes.SHA256(), default_backend())
    
    print("   ✅ تم إنشاء الشهادة (صالحة لمدة سنة)")
    
    print("\n3️⃣ حفظ الملفات...")
    print("   Saving files...")
    
    # حفظ المفتاح الخاص
    with open(key_file, "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        ))
    print(f"   ✅ المفتاح الخاص: {key_file}")
    
    # حفظ الشهادة
    with open(cert_file, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))
    print(f"   ✅ الشهادة: {cert_file}")
    
    print("\n" + "=" * 100)
    print("✅ تم إنشاء شهادة SSL بنجاح!")
    print("✅ SSL Certificate generated successfully!")
    print("=" * 100)
    
    print("\n📋 معلومات الشهادة:")
    print("📋 Certificate Information:")
    print(f"   - المفتاح الخاص / Private Key: {key_file}")
    print(f"   - الشهادة / Certificate: {cert_file}")
    print(f"   - صالحة حتى / Valid until: {(datetime.utcnow() + timedelta(days=365)).strftime('%Y-%m-%d')}")
    print(f"   - النطاقات / Domains: localhost, 127.0.0.1")
    
    print("\n⚠️  ملاحظة مهمة:")
    print("⚠️  Important Note:")
    print("   هذه شهادة ذاتية التوقيع للتطوير المحلي فقط")
    print("   This is a self-signed certificate for local development only")
    print("   المتصفح سيظهر تحذير أمان - هذا طبيعي")
    print("   Browser will show security warning - this is normal")
    
    return True

if __name__ == '__main__':
    success = generate_ssl_certificate()
    sys.exit(0 if success else 1)

