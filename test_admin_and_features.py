import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding='utf-8')

import app as flask_app

def test_admin_suite():
    print("=== Testing Admin & Security Suite ===")
    flask_app.app.config['TESTING'] = True
    client = flask_app.app.test_client()

    # 1. Test unauthenticated access to admin dashboard -> redirect
    r = client.get('/admin/dashboard')
    assert r.status_code == 302, f"Expected redirect, got {r.status_code}"
    print("  [OK] Protected admin routes redirect unauthenticated users")

    # 2. Test Admin Login (Invalid)
    r_bad = client.post('/admin/login', data={'username': 'admin', 'password': 'wrongpassword'})
    assert r_bad.status_code == 200
    print("  [OK] Invalid login rejected")

    # 3. Test Admin Login (Valid)
    r_login = client.post('/admin/login', data={'username': 'admin', 'password': 'solarai2026'}, follow_redirects=True)
    assert r_login.status_code == 200
    assert 'แผงควบคุมผู้ดูแลระบบ' in r_login.data.decode('utf-8')
    print("  [OK] Admin login successful & dashboard loaded")

    # 4. Test Admin Packages Page
    r_pkg_page = client.get('/admin/packages')
    assert r_pkg_page.status_code == 200
    print("  [OK] Admin Packages CRUD page accessible")

    # 5. Test Add Package API
    new_pkg_data = {
        'kw': 7.5,
        'name': 'Solar Rooftop 7.5 kW (Custom Pro)',
        'cost': 195000,
        'inverter': 'Huawei SUN2000-8KTL',
        'panels': 'Tier-1 Mono 585W',
        'warranty_inverter': '10 ปี',
        'warranty_panel': '25 ปี',
        'recommended_bill_range': '6,000 – 9,000 บาท/เดือน',
        'description': 'แพ็กเกจพิเศษสำหรับทดสอบระบบ',
        'is_active': True
    }
    r_add = client.post('/api/admin/packages', json=new_pkg_data)
    assert r_add.status_code == 200
    res_add = r_add.get_json()
    pkg_id = res_add['package']['id']
    assert res_add['package']['kw'] == 7.5
    print(f"  [OK] Added solar package: {pkg_id}")

    # 6. Test Update Package API
    update_data = {
        'name': 'Solar Rooftop 7.5 kW (Updated Name)',
        'cost': 189000,
        'kw': 7.5,
        'inverter': 'Sungrow 8kW Inverter',
        'panels': 'Tier-1 Mono 585W',
        'warranty_inverter': '10 ปี',
        'warranty_panel': '25 ปี',
        'recommended_bill_range': '6,000 – 9,000 บาท/เดือน',
        'description': 'อัปเดตข้อมูลสำเร็จ'
    }
    r_up = client.put(f'/api/admin/packages/{pkg_id}', json=update_data)
    assert r_up.status_code == 200
    res_up = r_up.get_json()
    assert res_up['package']['cost'] == 189000
    print("  [OK] Updated solar package successfully")

    # 7. Test Delete Package API
    r_del = client.delete(f'/api/admin/packages/{pkg_id}')
    assert r_del.status_code == 200
    print("  [OK] Deleted test solar package successfully")

    # 8. Test Admin Audit Page
    r_audit = client.get('/admin/audit')
    assert r_audit.status_code == 200
    assert 'บันทึกการทำงานระบบ' in r_audit.data.decode('utf-8')
    print("  [OK] Admin Audit Trail accessible")

    # 9. Test Logout
    r_logout = client.get('/admin/logout', follow_redirects=True)
    assert r_logout.status_code == 200
    print("  [OK] Admin logout successfully")

    # 10. Verify protected route is locked again
    r_locked = client.get('/admin/dashboard')
    assert r_locked.status_code == 302
    print("  [OK] Protected route relocked after logout")

    print("\n==============================================")
    print("ALL 10 ADMIN & ROLE TESTS PASSED PERFECTLY!")
    print("==============================================")

if __name__ == '__main__':
    test_admin_suite()
