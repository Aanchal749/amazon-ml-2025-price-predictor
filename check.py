import pandas as pd
import numpy as np

# Load submission
sub = pd.read_csv('dataset/test_out.csv')

print("="*60)
print("SUBMISSION FILE VALIDATION")
print("="*60)

# Check 1: Correct shape
print(f"\n✓ Total predictions: {len(sub):,}")
print(f"  Expected: 75,000")
print(f"  Match: {'YES ✅' if len(sub) == 75000 else 'NO ❌'}")

# Check 2: Required columns
has_id = 'sample_id' in sub.columns
has_price = 'price' in sub.columns
print(f"\n✓ Has 'sample_id': {'YES ✅' if has_id else 'NO ❌'}")
print(f"✓ Has 'price': {'YES ✅' if has_price else 'NO ❌'}")

# Check 3: No missing values
missing_id = sub['sample_id'].isna().sum()
missing_price = sub['price'].isna().sum()
print(f"\n✓ Missing sample_ids: {missing_id} {'✅' if missing_id == 0 else '❌'}")
print(f"✓ Missing prices: {missing_price} {'✅' if missing_price == 0 else '❌'}")

# Check 4: All prices positive
negative = (sub['price'] < 0).sum()
zero = (sub['price'] == 0).sum()
print(f"\n✓ Negative prices: {negative} {'✅' if negative == 0 else '❌'}")
print(f"✓ Zero prices: {zero}")

# Check 5: Price statistics
print(f"\n📊 Price Distribution:")
print(f"  Min:    ${sub['price'].min():.2f}")
print(f"  Q25:    ${sub['price'].quantile(0.25):.2f}")
print(f"  Median: ${sub['price'].median():.2f}")
print(f"  Q75:    ${sub['price'].quantile(0.75):.2f}")
print(f"  Max:    ${sub['price'].max():.2f}")
print(f"  Mean:   ${sub['price'].mean():.2f}")

# Check 6: Unique sample_ids
unique_ids = sub['sample_id'].nunique()
print(f"\n✓ Unique sample_ids: {unique_ids:,}")
print(f"  All unique: {'YES ✅' if unique_ids == 75000 else 'NO ❌'}")

# Check 7: Sample predictions
print(f"\n🔍 First 10 Predictions:")
print(sub.head(10).to_string(index=False))

# Final verdict
print("\n" + "="*60)
all_checks = (
    len(sub) == 75000 and 
    has_id and has_price and 
    missing_id == 0 and missing_price == 0 and 
    negative == 0 and 
    unique_ids == 75000
)
if all_checks:
    print("🎉 ALL CHECKS PASSED - READY TO SUBMIT!")
else:
    print("⚠️  Some checks failed - review above")
print("="*60)