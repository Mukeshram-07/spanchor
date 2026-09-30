# Regression Gate Validation - Quick Reference 🎯

## The Fix in 30 Seconds

**Before**:
```python
policy = {"mean_recall@5": 0.05}  # ✗ Wrong - aggregate name
```

**After**:
```python
policy = {"recall@5": 0.05}  # ✓ Correct - per-query name
```

**Result**: Regression correctly detected, exit code 1 ✅

---

## Key Concepts

### Per-Query Detection
- Each query is evaluated independently
- If ANY query regresses beyond threshold → exit code 1
- Aggregate improvements cannot mask individual regressions

### Policy Keys
- Must match per-query metric names (e.g., `recall@5`)
- NOT aggregate names (e.g., `mean_recall@5`)
- Wrong policy keys = silent failure to detect regressions

### Exit Codes
- `0` = No queries regressed (PASS)
- `1` = At least one query regressed (FAIL)

---

## Files Changed

1. **run_validation.py** - Fixed policy dict
2. **README.md** - Updated documentation
3. **test_comparison_regression_gate.py** - Added 16 tests

## Files to Know

1. **src/spanchor/comparison/compare.py** - The core logic (already correct)
2. **examples/real_world_validation/** - Validation scenarios

---

## Verification

```bash
# All tests pass
pytest tests/unit/ -q
# Result: 751 passed ✅

# Regression scenario (19 regressions)
python examples/real_world_validation/run_validation.py
# Result: Exit code 1 ✅

# Passing scenario (0 regressions)  
python examples/real_world_validation/run_passing_validation.py
# Result: Exit code 0 ✅
```

---

## Common Mistakes to Avoid

❌ Using aggregate metric names in policy:
```python
policy = {"mean_recall@5": 0.05}  # Won't work!
```

✅ Use per-query metric names:
```python
policy = {"recall@5": 0.05}  # Correct!
```

---

## For CI/CD Integration

```bash
python run_validation.py
if [ $? -eq 0 ]; then
  echo "Quality gate PASSED"
else
  echo "Quality gate FAILED - regressions detected"
  exit 1
fi
```

---

## Status

✅ All 751 tests passing  
✅ Both PASS and FAIL scenarios work  
✅ Documentation updated  
✅ Production ready

**Ready to merge** 🚀

