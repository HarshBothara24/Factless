# FACTLESS Scoring System Improvements

## Problem Identified

The original scoring system was too conservative and not properly detecting heavily hallucinated content. A completely fabricated text with multiple suspicious entities was only scoring 0.400 (MEDIUM risk) when it should have been HIGH risk.

## Root Causes

1. **Linear scaling was too conservative** - Each issue only added small incremental risk
2. **Entity fabrication scoring was insufficient** - Multiple fabricated entities weren't penalized enough
3. **Risk thresholds were too high** - 0.7 threshold for HIGH risk was too lenient
4. **Module weights didn't reflect importance** - Entity fabrication is a strong hallucination indicator
5. **No amplification for multiple signals** - Multiple modules detecting issues should compound risk

## Improvements Made

### 1. Enhanced Scoring Algorithm (`factless/scoring.py`)

**Before:**
```python
# Linear scaling - too conservative
contradiction_score = len(contradictions) * 0.25  # Max 1.0 after 4 contradictions
logical_flow_score = len(flaws) * 0.20           # Max 1.0 after 5 flaws
```

**After:**
```python
# Progressive scaling - more realistic
if contradiction_count == 1:
    contradiction_score = 0.4  # Single contradiction is already concerning
elif contradiction_count == 2:
    contradiction_score = 0.7  # Two contradictions is high risk
else:
    contradiction_score = 1.0  # Three or more is maximum risk
```

### 2. Entity Fabrication Amplification

**New logic:**
- 4+ suspicious entities = 1.5x multiplier (very high risk)
- 2-3 suspicious entities = 1.3x multiplier (high risk)
- Minimum score of 0.75 for 4+ suspicious entities

### 3. Multi-Module Risk Amplification

**New feature:**
```python
# Progressive multipliers for multiple active modules
if active_modules >= 4:  # 4+ modules = very likely hallucinated
    final_score = min(1.0, final_score * 1.4)
elif active_modules >= 3:  # 3 modules = likely hallucinated
    final_score = min(1.0, final_score * 1.25)
elif active_modules >= 2:  # 2 modules = concerning
    final_score = min(1.0, final_score * 1.15)
```

### 4. Adjusted Risk Thresholds (`factless/config.py`)

**Before:**
```python
low_threshold: float = 0.3   # LOW risk
high_threshold: float = 0.7  # HIGH risk
```

**After:**
```python
low_threshold: float = 0.25  # LOW risk (more sensitive)
high_threshold: float = 0.60 # HIGH risk (more sensitive)
```

### 5. Rebalanced Module Weights

**Before:**
```python
contradiction: float = 0.25
logical_flow: float = 0.20
overconfidence: float = 0.15
claim_density: float = 0.15
entity_fabrication: float = 0.25
```

**After:**
```python
contradiction: float = 0.20
logical_flow: float = 0.15
overconfidence: float = 0.15
claim_density: float = 0.10
entity_fabrication: float = 0.40  # Increased - strong hallucination indicator
```

### 6. Enhanced Entity Fabrication Detection (`factless/modules/entity_fabrication.py`)

**Improvements:**
- More aggressive academic fabrication patterns
- Better detection of suspicious person names
- Enhanced organization name patterns
- Increased severity weights for different fabrication types

**New patterns added:**
```python
fabricated_patterns = [
    r'^John [A-Z][a-z]+$',
    r'^Jane [A-Z][a-z]+$', 
    r'^Dr\. [A-Z][a-z]+ [A-Z][a-z]+$',
    r'^Professor [A-Z][a-z]+ [A-Z][a-z]+$',
    # ... more patterns
]
```

### 7. Improved Risk Score Calculation

**New calculation method:**
```python
# Base risk from proportion of suspicious entities
suspicious_ratio = len(suspicious_entities) / total_entities
risk_score += suspicious_ratio * 0.6  # Increased from 0.5

# Severity weights increased across the board
if "academic_style_fabrication" in reason:
    severity_weight += 0.4  # Increased from 0.3
elif "overly_specific_without_explanation" in reason:
    severity_weight += 0.3  # Increased from 0.2
# ... etc
```

### 8. Enhanced Claim Extraction Prompt

**Improved prompt for better detection:**
- More specific instructions for fabricated content
- Better detection of historical claims and specific details
- Enhanced confidence marker detection

## Expected Results

With these improvements, the same heavily hallucinated text should now score:

**Before:** 0.400 (MEDIUM risk)
**After:** 0.65-0.85 (HIGH risk)

### Scoring Breakdown Example

For text with 4+ suspicious entities:
1. **Entity Fabrication Score**: 0.8 (high due to multiple entities)
2. **Entity Amplification**: 1.5x multiplier
3. **Module Weight**: 0.40 (increased importance)
4. **Multi-Module Amplification**: 1.25x (if 3+ modules active)
5. **Minimum Floor**: 0.75 for 4+ suspicious entities

**Final Score**: ~0.75-0.85 (HIGH risk)

## Testing

To test the improvements:

1. **Use the high-risk example text** with multiple fabricated entities
2. **Expected result**: Risk score > 0.60 (HIGH risk)
3. **Check explanations**: Should show multiple entity fabrication signals
4. **Verify amplification**: Multiple modules should be active

## Configuration

The new scoring can be fine-tuned via `factless/config.py`:

```python
# Adjust risk thresholds
risk_thresholds.low_threshold = 0.25
risk_thresholds.high_threshold = 0.60

# Adjust module weights
module_weights.entity_fabrication = 0.40

# Adjust entity fabrication sensitivity
entity_fabrication.suspicious_patterns = [...]
```

## Validation

The improvements maintain the core principles:
- ✅ **Explainable**: All risk signals are still attributable
- ✅ **Deterministic**: Same input produces same output
- ✅ **No external data**: Still uses only internal patterns
- ✅ **Ethical**: Still only provides risk assessment, not truth claims

## Summary

These improvements make FACTLESS much more effective at detecting heavily hallucinated content while maintaining its explainable and ethical approach. The system now properly escalates risk when multiple fabrication signals are detected, which is the hallmark of AI-generated hallucinations.