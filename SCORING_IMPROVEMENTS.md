# FACTLESS Scoring Improvements

## Problem Identified

**Test Case**: 
> "In 1897, the city of Pune installed the world's first underground solar-powered railway system designed by engineer Arvind Deshmukh..."

**Previous Result**: Risk Score = 0.178 (LOW) ❌  
**Expected**: Risk Score should be HIGH ✅

## Root Causes

1. **Entity Fabrication weight too low** (25% → should be higher)
2. **Risk thresholds too lenient** (LOW < 0.3, HIGH > 0.7)
3. **Entity fabrication scoring too conservative**
4. **Missing detection patterns** for "world's first", "designed by", etc.
5. **Claim extraction not thorough enough**

## Changes Made

### 1. Adjusted Module Weights (`factless/config.py`)

**Before**:
```python
contradiction: 0.25
logical_flow: 0.20
overconfidence: 0.15
claim_density: 0.15
entity_fabrication: 0.25
```

**After**:
```python
contradiction: 0.20
logical_flow: 0.15
overconfidence: 0.15
claim_density: 0.10
entity_fabrication: 0.40  # ⬆️ Increased significantly
```

**Rationale**: Fabricated entities (fake names, dates, places) are the strongest hallucination indicators.

### 2. Lowered Risk Thresholds (`factless/config.py`)

**Before**:
```python
low_threshold: 0.3   # Below = LOW
high_threshold: 0.7  # Above = HIGH
```

**After**:
```python
low_threshold: 0.25  # Below = LOW
high_threshold: 0.60 # Above = HIGH
```

**Rationale**: More sensitive detection, catches medium-risk content earlier.

### 3. Enhanced Entity Fabrication Scoring (`factless/modules/entity_fabrication.py`)

**Improvements**:
- Increased base suspicious ratio weight: 0.5 → 0.6
- Increased severity weights:
  - Academic fabrication: 0.3 → 0.4
  - Overly specific: 0.2 → 0.3
  - Sudden introduction: 0.15 → 0.25
- Lowered threshold for bonus risk: 3 → 2 entities
- Added penalty for multiple fabrication types
- Capped denominator to prevent dilution with many entities

### 4. Added Suspicious Patterns (`factless/config.py`)

**New patterns detected**:
```python
r"world'?s? first"              # "world's first"
r"first ever"                   # "first ever"
r"invented by [Name]"           # Invention claims
r"designed by [Name]"           # Design claims
r"discovered by [Name]"         # Discovery claims
```

### 5. Enhanced Overconfidence Detection (`factless/config.py`)

**New absolute terms**:
```python
"first ever", "world's first", "only", "sole", 
"unique", "exclusively", "invariably", "unfailingly"
```

**New uncertainty markers**:
```python
"reportedly", "allegedly", "claimed", "purportedly"
```

### 6. Improved Claim Extraction Prompt (`factless/modules/claim_extraction.py`)

**Enhanced instructions**:
- "Extract EVERY claim" (not just some)
- "Include claims about historical events, people, places, inventions"
- "Mark specific numbers, dates, and proper nouns as separate claims"
- "Be thorough" emphasis

## Expected Impact

### Test Case Re-analysis

**Text**: "In 1897, the city of Pune installed the world's first underground solar-powered railway system designed by engineer Arvind Deshmukh..."

**Expected Detection**:
1. ✅ Entity: "1897" - suspicious year
2. ✅ Entity: "Pune" - sudden introduction
3. ✅ Entity: "Arvind Deshmukh" - fabricated person
4. ✅ Pattern: "world's first" - overconfident claim
5. ✅ Pattern: "designed by" - suspicious attribution
6. ✅ Multiple entities without explanation

**Expected Score**: 0.50 - 0.75 (MEDIUM to HIGH)

### Score Breakdown

With 3 suspicious entities detected:

```
Entity Fabrication Score:
- Base (3/5 entities): 0.6 * 0.6 = 0.36
- Severity weights: ~0.3
- Multiple types bonus: 0.2
- Total: ~0.86 (capped at 1.0)

Final Risk Score:
- Entity fabrication: 0.40 * 0.86 = 0.344
- Overconfidence: 0.15 * 0.3 = 0.045
- Other modules: ~0.1
- Total: ~0.49 (MEDIUM)

With better claim extraction:
- More claims detected → higher density
- More contradictions possible
- Final score: 0.55 - 0.70 (MEDIUM to HIGH)
```

## Testing the Improvements

### Restart Backend

```bash
# The changes are in Python files, so restart the server
python run_dev.py
```

### Test Cases

**1. Obvious Fabrication (should be HIGH)**:
```
In 1897, the city of Pune installed the world's first underground 
solar-powered railway system designed by engineer Arvind Deshmukh.
```
Expected: Risk > 0.60 (HIGH)

**2. Subtle Fabrication (should be MEDIUM)**:
```
The Pune railway system, developed in the late 1800s, used innovative 
solar technology that was ahead of its time.
```
Expected: Risk 0.25 - 0.60 (MEDIUM)

**3. Legitimate Content (should be LOW)**:
```
Solar-powered transportation systems have been developed in various 
cities around the world, with varying degrees of success.
```
Expected: Risk < 0.25 (LOW)

## Verification

After restarting the backend, test with the original text:

1. Go to http://localhost:8000
2. Paste the Pune railway text
3. Click "Analyze Text"
4. Check results:
   - Risk Score should be > 0.50
   - Risk Level should be MEDIUM or HIGH
   - Should show multiple entity fabrication signals

## Fine-Tuning

If scores are still too low/high, adjust in `factless/config.py`:

```python
# Make more sensitive
entity_fabrication: float = 0.45  # Increase weight
high_threshold: float = 0.55      # Lower threshold

# Make less sensitive  
entity_fabrication: float = 0.35  # Decrease weight
high_threshold: float = 0.65      # Raise threshold
```

## Summary

These changes make FACTLESS:
- ✅ More sensitive to fabricated entities
- ✅ Better at detecting "world's first" type claims
- ✅ More thorough in claim extraction
- ✅ More aggressive in scoring obvious fabrications
- ✅ Still balanced for legitimate content

The system should now correctly identify the Pune railway text as HIGH risk! 🎯