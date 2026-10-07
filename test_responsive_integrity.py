import sys
import os
import re
from app import app

def test_responsive_markup():
    print("=== Testing Responsive Layout & HTML/CSS Integrity ===")
    client = app.test_client()

    pages_to_check = [
        ('/', ['dashboard-recent-table', 'dashboard-recent-cards']),
        ('/map', ['map-topbar', 'search-box', 'tambon-quick-select-wrap', 'bill-presets-grid', 'result-panel']),
        ('/history', ['history-header', 'history-desktop-card', 'history-mobile-container']),
        ('/report', ['report-desktop-table', 'report-mobile-cards']),
        ('/admin/login', ['page-wrapper', 'form-control']),
    ]

    for url, required_classes in pages_to_check:
        res = client.get(url)
        assert res.status_code in [200, 302], f"Failed to load {url}: {res.status_code}"
        html = res.data.decode('utf-8')
        for cls in required_classes:
            assert cls in html, f"Page {url} is missing responsive class: {cls}"
        print(f"  [OK] Page '{url}' has all responsive markers: {required_classes}")

    # Login as admin
    client.post('/admin/login', data={'username': 'admin', 'password': 'solarai2026'}, follow_redirects=True)

    admin_pages = [
        ('/admin/dashboard', ['admin-grid-charts', 'admin-recent-table', 'admin-recent-cards', 'admin-kpi-grid', 'admin-kpi-val', 'admin-model-metrics']),
        ('/admin/packages', ['packageModal', 'package-card']),
        ('/admin/audit', ['audit-desktop-card', 'audit-mobile-cards', 'audit-row', 'audit-mobile-card']),
        ('/settings', ['settings-form', 'cost_3kw', 'cost_20kw']),
    ]

    for url, required_classes in admin_pages:
        res = client.get(url)
        assert res.status_code == 200, f"Failed to load admin page {url}: {res.status_code}"
        html = res.data.decode('utf-8')
        for cls in required_classes:
            assert cls in html, f"Admin page {url} is missing responsive class: {cls}"
        print(f"  [OK] Admin page '{url}' has all responsive markers: {required_classes}")

    # Verify CSS contains corresponding media queries and rules
    with open('static/css/main.css', 'r', encoding='utf-8') as f:
        css = f.read()

    css_markers = [
        '@media (max-width: 768px)',
        '@media (min-width: 1025px)',
        '.history-mobile-container',
        '.audit-mobile-cards',
        '.report-mobile-cards',
        '.dashboard-recent-cards',
        '.bill-presets-grid',
        '.mobile-bottom-nav',
        '.admin-kpi-grid',
        '.admin-kpi-val',
    ]

    for marker in css_markers:
        assert marker in css, f"main.css is missing: {marker}"
        print(f"  [OK] main.css contains rule: '{marker}'")

    print("\n==================================================")
    print("ALL RESPONSIVE INTEGRITY & MARKUP CHECKS PASSED!")
    print("==================================================")

if __name__ == '__main__':
    test_responsive_markup()
