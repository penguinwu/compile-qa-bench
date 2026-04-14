# Skill: Inter-Annotator Agreement (IAA) Validation

How to validate a scoring rubric through iterative inter-annotator agreement testing. Proven workflow — took a rubric from κ=0.027 to κ=0.843 over 5 iterations.

## The Workflow

### Step 1: Calibrate Small (20 cases)

Both scorers independently score 20 cases. Include known-easy cases (sanity check) and known-hard cases (stress test).

Target: κ≥0.60 on each dimension. If below, the rubric has fundamental ambiguity — fix before proceeding.

### Step 2: Full Scoring (all cases)

Both scorers independently score the full dataset. CRITICAL: both must use the SAME rubric version. Mixed-version scoring produces meaningless kappa.

### Step 3: Compute Weighted Kappa

Use Cohen's weighted kappa with linear weights for ordinal scales. Use simple kappa for binary dimensions.

```python
def weighted_kappa(a, b, num_categories):
    n = len(a)
    cm = [[0]*num_categories for _ in range(num_categories)]
    for i in range(n):
        cm[a[i]][b[i]] += 1
    row_m = [sum(cm[i]) for i in range(num_categories)]
    col_m = [sum(cm[i][j] for i in range(num_categories)) for j in range(num_categories)]
    observed = sum(abs(i-j)/(num_categories-1) * cm[i][j] / n
                   for i in range(num_categories) for j in range(num_categories))
    chance = sum(abs(i-j)/(num_categories-1) * row_m[i]*col_m[j] / n**2
                 for i in range(num_categories) for j in range(num_categories))
    return 1 - observed / chance if chance > 0 else 1.0
```

Interpretation: <0.20 poor, 0.21-0.40 fair, 0.41-0.60 moderate, 0.61-0.80 substantial, 0.81-1.00 near-perfect.

### Step 4: Build Confusion Matrix

The confusion matrix shows WHERE scorers disagree, not just how much. Look for:
- **Off-diagonal clusters**: large blocks of disagreement at specific score pairs
- **Asymmetric disagreement**: one scorer systematically higher/lower
- **Empty levels**: scores both scorers skip (broken category)

### Step 5: Root-Cause Each Disagreement Cluster

For each large off-diagonal cluster, pull 5-10 cases and compare rationales. Ask:
- Are scorers reading the same text differently? → Rubric boundary is fuzzy
- Is one scorer misapplying the rubric? → Scorer error, not rubric problem
- Are both applying the rubric correctly but it gives ambiguous guidance for this pattern? → Add a bright-line rule

Distinguish rubric fixes from scorer corrections. Don't change the rubric to match one scorer's interpretation — that's overfitting.

### Step 6: Add Bright-Line Rule

Write a mechanical test that resolves the specific ambiguity. The test must:
- Reference observable properties of the text (not scorer judgment)
- Include 2+ examples showing cases on each side of the boundary
- State priority if it conflicts with existing rules

### Step 7: Both Scorers Re-Score

BOTH scorers must re-score with the updated rubric. Never compare Scorer-A-v2.6 against Scorer-B-v2.5 as a final result. Intermediate comparisons are fine for development, but the validation kappa requires both on the same version.

Re-scoring is cheap (minutes for 160 cases with LLM scorers). Just do it.

### Step 8: Iterate

Repeat steps 3-7 until κ≥0.80 on all dimensions. Typical: 3-5 iterations.

## What to Report

For each iteration, record:
- Rubric version and what changed
- Kappa per dimension (with progression table)
- Confusion matrix
- Disagreement clusters identified and how they were resolved
- Score distributions per scorer

## Kappa Progression Example (from this project)

| Version | Diagnosis κ | Actionability κ | Key Change |
|---------|------------|----------------|------------|
| v2.2 | 0.501 | 0.027 | Initial — different rubric versions |
| v2.3 | 0.501 | 0.461 | Template response rule |
| v2.4 | 0.466 | 0.475 | Boundary rules (Rocky re-scored properly) |
| v2.5 | 0.621 | 0.653 | Causal assertion + imperative verb tests |
| v2.6 | 0.843 | 0.657 | Case-specific causal chain + template override |

## Anti-Patterns

### Keyword Matching for Scoring
Never score by programmatically matching keywords in responses. Scoring requires reading the response and applying judgment. Keyword matching overfits to surface patterns and inflates kappa artificially. We learned this the hard way — keyword-matched kappa was 0.825, real kappa was 0.466.

### Iterating Rubric Against One Scorer
If you analyze disagreements and adjust the rubric to move Scorer A's scores toward Scorer B's, you're overfitting. The rubric change must be principled (fix a genuine ambiguity), and BOTH scorers must re-score.

### Mixed-Version Comparisons
Scorer A on v2.5 vs Scorer B on v2.6 is not a valid kappa. The rules changed — of course they disagree. Always use same version for validation.

### Ignoring Score Distribution
κ=0.85 on a binary scale where 95% of cases are one class is less impressive than κ=0.85 on a 4-level scale with balanced distribution. Check entropy alongside kappa.

### Ignoring Granularity
If both scorers put 97% of scores in two levels (effectively binary), the 4-level scale isn't earning its keep on THIS dataset. Keep it if you need measurement sensitivity for future improvement, but report the effective resolution honestly.
