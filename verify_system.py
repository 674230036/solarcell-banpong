"""
System verification script - checks all calculations and bugs.
"""
import sys
sys.path.insert(0, r'c:\xampp\htdocs\Solasell10-5-main\Solasell10-5-main')
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
import predict as pr
import financial_engine as fe

print('=== TEST 1: Basic Predict (5kW baseline) ===')
result = pr.analyze_location(13.8264, 99.8780, electricity_rate=4.50)
print('annual_kwh (5kW):', result['annual_kwh'])
print('current_daily:', result['current_daily'])
print('confidence:', result['confidence'])
print('suitability:', result['suitability'])

print()
print('=== TEST 2: Financial Engine - Bill 5000 ===')
fin = fe.calculate_financials(result, 5000)
print('Recommended kW:', fin['recommended']['kw'])
print('monthly_save:', fin['monthly_save'])
print('annual_save:', fin['annual_save'])
print('breakeven:', fin['breakeven'])
print('roi:', fin['roi'])
print('monthly_bill:', fin['monthly_bill'])
print('remaining_bill:', fin['remaining_bill'])

print()
print('=== TEST 3: Bill 3000 (should rec 3kW) ===')
fin3 = fe.calculate_financials(result, 3000)
print('Recommended kW:', fin3['recommended']['kw'])
print('monthly_save:', fin3['monthly_save'])
print('annual_save:', fin3['annual_save'])
print('breakeven:', fin3['breakeven'])

print()
print('=== TEST 4: Savings Cap Check ===')
fin_small = fe.calculate_financials(result, 1500)
print('Bill: 1500, monthly_save:', fin_small['monthly_save'], '| cap OK:', fin_small['monthly_save'] <= 1500)
print('remaining_bill:', fin_small['remaining_bill'], '| non-negative OK:', fin_small['remaining_bill'] >= 0)

print()
print('=== TEST 5: ROI Manual Validation ===')
for s in fin['systems']:
    manual_roi = round((s['annual_save'] / s['cost']) * 100, 1) if s['cost'] > 0 else 0
    manual_bp = round(s['cost'] / s['annual_save'], 1) if s['annual_save'] > 0 else 99
    roi_ok = abs(manual_roi - s['roi']) < 0.2
    bp_ok = abs(manual_bp - s['breakeven']) < 0.2
    print(f"  {s['kw']}kW: ROI={s['roi']}% (calc={manual_roi}) OK={roi_ok}, BP={s['breakeven']}y (calc={manual_bp}) OK={bp_ok}")

print()
print('=== TEST 6: Prediction Sanity - Different Locations ===')
locs = [
    (13.8264, 99.8780, 'Ban Pong Center'),
    (13.8160, 99.8770, 'Tambon Ban Pong'),
    (13.8560, 99.8240, 'Tambon Nong Pla Mo'),
    (13.9120, 99.8820, 'Tambon Krab Yai'),
]
for lat, lng, name in locs:
    r = pr.analyze_location(lat, lng, electricity_rate=4.50)
    print(f"  {name}: daily={r['current_daily']:.2f} kWh, annual={r['annual_kwh']:.0f} kWh, conf={r['confidence']}%")

print()
print('=== TEST 7: Seasonal Data Completeness ===')
ss = result['seasonal_summary']
total_pct = ss['summer']['share_pct'] + ss['rainy']['share_pct'] + ss['winter']['share_pct']
print('Summer:', ss['summer']['kwh'], 'kWh,', ss['summer']['share_pct'], '%')
print('Rainy: ', ss['rainy']['kwh'], 'kWh,', ss['rainy']['share_pct'], '%')
print('Winter:', ss['winter']['kwh'], 'kWh,', ss['winter']['share_pct'], '%')
print('Total %:', total_pct, '(should be ~100)')

print()
print('=== TEST 8: Monthly Data Completeness ===')
md = result['monthly_data']
print('Monthly records:', len(md), '(should be 12)')
for m in md:
    print(f"  {m['month_short']}: {m['daily_kwh']:.2f} kWh/day, {m['monthly_kwh']:.1f} kWh/month")

print()
print('=== TEST 9: Hourly Profile ===')
hp = result['hourly_profile']
total_hp = sum(h['kwh'] for h in hp)
print('Total hourly kWh:', round(total_hp, 2), '(should match daily:', result['current_daily'], ')')
print('Peak hour:', max(hp, key=lambda x: x['kw'])['hour'], '(should be around 12:00)')

print()
print('=== TEST 10: Model Info ===')
mi = pr.get_model_info()
print('Type:', mi['type'])
print('R2:', mi['r2'])
print('RMSE:', mi['rmse'])
print('MAE:', mi['mae'])
print('Features:', len(mi['features']))
print('N estimators:', mi['n_estimators'])

print()
print('=== ALL TESTS DONE ===')
