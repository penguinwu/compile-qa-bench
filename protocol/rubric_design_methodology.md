# Rubric Design Methodology: From Direct Scoring to Label-Based Decomposition

**Project:** PT2 Documentation Evaluation
**Authors:** Owl (Evaluation Methodologist), Peng Wu
**Date:** 2026-04-14
**Status:** Validated on 60 cases (40 Act, 20 Diag), pending full deployment

---

## 1. The Problem We Were Solving

### 1.1 Starting Point: Direct Ordinal Scoring

Our initial rubric (v2.0–v2.8) asked scorers to assign ordinal scores directly:
- Diagnosis: 0–3 ("how well did the agent diagnose the root cause?")
- Actionability: 0–3 ("how actionable is the guidance?")
- Fabrication: binary ("did the agent fabricate information?")

Each level had text descriptions and examples. Scorers read the guidance, considered the criteria, and produced a number.

### 1.2 What Went Wrong

Through 8 rubric iterations (v2.0 → v2.8), we improved score boundary definitions, added worked examples, created bright-line tests, and ran calibration rounds. Despite this:

| Dimension | Target κ | Achieved κ (Track 1) | Achieved κ (Track 2) |
|-----------|----------|----------------------|----------------------|
| Diagnosis | ≥ 0.80 | 0.415 | 0.863 |
| Actionability | ≥ 0.80 | 0.486 | 0.885 |
| Fabrication | ≥ 0.80 | 0.000 | 1.000 |

Track 2 (doc-restricted) passed. Track 1 (unrestricted) failed badly. The same rubric, same scorers, same calibration — but Track 1's richer, more detailed responses created more room for scorer interpretation.

### 1.3 The Key Insight: Classification vs. Synthesis

When we analyzed the 8 largest Actionability disagreements (|Δ| ≥ 2), we found something surprising: **both scorers agreed on the underlying observations but disagreed on how to combine them into a score.**

Example (J6-4, Act):
- Owl: "The fix works standalone, but it's interchangeable across similar cases." → Act=1
- Raven: "The fix works standalone." → Act=3

Both scorers saw the same two facts: (1) the fix works standalone and (2) it's interchangeable. But the rubric had a priority rule (standalone > interchangeability) that Owl overrode based on judgment, while Raven applied mechanically.

This is a **synthesis problem**, not a classification problem. The scorers weren't disagreeing about what they observed — they were disagreeing about the weight and priority of their observations when combining them into a single number.

**Lesson 1: When scorer disagreements are dominated by synthesis problems (how to combine observations), adding more examples or sharper boundary definitions won't help. The fix is to separate classification from synthesis.**

## 2. The Solution: Label-Based Decomposition

### 2.1 Core Architecture

Instead of asking scorers to produce a score directly, we decomposed the task into two steps:

1. **Classification:** Assign binary labels (true/false) to observable features of the guidance. Each label has a bright-line test.
2. **Synthesis:** Apply a deterministic formula to map labels → score. The formula encodes priority rules that scorers no longer need to apply through judgment.

### 2.2 Why Binary Labels

We considered several granularities:
- **10+ labels** (Peng's initial suggestion): Too many — you'd move disagreement from "what score?" to "which labels apply?"
- **4–5 binary labels per dimension** (what we chose): Each label is a simple yes/no question. Binary questions are inherently easier to agree on than ordinal placement.
- **Fewer than 4**: Insufficient discrimination — the formula couldn't spread scores across the full range.

**Lesson 2: Start with the minimum number of binary labels that span the score range. You can always add labels if κ is low on specific ones, but removing labels is harder.**

### 2.3 Bright-Line Tests

Every label has a bright-line test — a concrete, mechanical check that a scorer can apply without judgment:

| Label | Bright-line test |
|-------|------------------|
| `standalone_fix` | Give ONLY this guidance to a new dev who's never seen the issue. Resolved without other resources? |
| `has_imperative` | Does the guidance contain a verb in imperative mood directed at the developer? |
| `case_specific` | Swap onto a different issue from a different category. Still makes sense? If yes → false. |
| `is_template` | Verbatim identical to another case's response? |
| `names_mechanism` | Can you grep the PyTorch source for the named mechanism? |
| `causal_chain` | Does the explanation have at least one "because"/"which causes"/"due to"? |

**Lesson 3: A label without a bright-line test is just a smaller version of the original scoring problem. The bright-line test IS the label — everything else is description.**

### 2.4 Formula Design

The formula encodes priority rules that were previously left to scorer judgment:

**Actionability:**
```
standalone_fix → Act=3     (priority: standalone trumps everything)
imperative + specific → Act=2
imperative + generic → Act=1
else → Act=0
```

**Diagnosis:**
```
count = sum(subsystem, mechanism, causal_chain, case_specific)
count ≥ 3 → Diag=3
count = 2 → Diag=2
count = 1 → Diag=1
count = 0 → Diag=0
(If inconsistent with resolution → capped at 1)
```

**Lesson 4: The formula itself becomes a design decision you debate once (at rubric design time), not 160 times (during scoring). This is the real win — you move the subjectivity from a per-case judgment to a one-time design choice.**

## 3. The Validation Process

### 3.1 Pilot Design

We validated on small, stratified samples before committing to full re-scoring:

1. **Track 1 Act pilot (20 cases):** 10 from prior disagreements + 10 from agreements. This ensures the pilot covers both easy and hard cases.
2. **Track 2 Act pilot (20 cases):** Random sample from doc-restricted cases. Tests label diversity — Track 2 should (and did) show more variation.
3. **Track 1 Diag pilot (20 cases):** 10 from Diag 2/3 boundary + 5 agreements + 5 other disagreements. Focuses on the known problem area.

**Lesson 5: Always include prior agreement cases in your pilot. If the new method breaks cases that already worked, you haven't improved — you've traded one problem for another.**

### 3.2 Blind Scoring

Both scorers scored labels independently, without access to prior scores or each other's labels. This is essential — if you let scorers see prior scores, you can't distinguish genuine agreement from anchoring bias.

### 3.3 Calibration

After computing initial κ, we examined disagreements and made calibration decisions:

**Act calibration (resolved 3/3 disagreements):**
- "Is a version upgrade a standalone fix?" → Yes, if the guidance names the specific version (e.g., "upgrade to PyTorch 2.2+").
- "Is 'avoid feature X' a standalone fix?" → Yes, if the guidance provides the specific avoidance action.
- Root insight: standalone_fix means "can the developer act without further research," not "does it fix the root cause." Workarounds that are immediately actionable count.

**Diag calibration (resolved 2/2 disagreements):**
- "Does referencing a specific issue number make a response case-specific?" → Yes.
- "Is investigation methodology ('how to bisect') the same as causal chain ('why it broke')?" → No. Methodology explains how to find the cause; causal chain explains what the cause is.

**Lesson 6: Calibration decisions are reusable rules, not case-specific patches. Each calibration session should produce a rule that can be applied to future cases without the calibrators being present. Write the rule, not just the decision.**

### 3.4 Results

| Metric | Direct Scoring | Labels Pre-Cal | Labels Post-Cal |
|--------|---------------|----------------|-----------------|
| Act κ (40 cases) | 0.429 | 0.769 | 1.000 |
| Diag κ (20 cases) | 0.182 | 0.643 | 1.000 |

## 4. Unexpected Findings

### 4.1 Labels Exposed Systematic Scorer Bias

When I (Owl) scored Diagnosis with labels, 16/20 cases changed from my direct scoring. Most moved from Diag=2 to Diag=3. The labels forced me to acknowledge that these cases DID name specific mechanisms and DID have causal chains — I had been scoring them Diag=2 based on a vague feeling of "not specific enough" that the labels couldn't justify.

**Lesson 7: Labels don't just improve inter-rater reliability — they improve intra-rater consistency. If your own label-derived score disagrees with your direct score, your direct score was probably wrong.**

### 4.2 Track Differences Validate Label Design

Track 1 (unrestricted) and Track 2 (doc-restricted) showed different label distributions:

| Label | Track 1 (20 cases) | Track 2 (20 cases) |
|-------|--------------------|--------------------|
| standalone_fix | 9/20 true | 0/20 true |
| has_imperative | 20/20 true | 10/20 true |
| case_specific | 19/20 true | 12/20 true |
| is_template | 0/20 true | 8/20 true |

Track 1 guidance is always imperative, always specific, never a template. Track 2 guidance is often descriptive, sometimes generic, frequently templated. The labels correctly capture this difference, and the formula produces the right score distribution for each track.

**Lesson 8: If all your labels have the same value across cases, the label isn't discriminating — it's a constant. This isn't necessarily a design flaw (Track 1 guidance IS always imperative), but you should verify on a different population before concluding.**

### 4.3 Formula Ceiling Effects Are Informative

19/20 Track 1 Diag cases scored Diag=3 with labels. Initially this felt like a formula problem ("it can't distinguish quality within Diag=3"). But comparing with Raven's direct scores showed they ALSO scored most of these as Diag=3. The ceiling was real — Track 1's unrestricted agent genuinely produces high-quality diagnoses.

**Lesson 9: A ceiling effect in the label-derived scores is a signal, not a bug. If everything scores high, the interesting variation is elsewhere (like Act or Fab), and you should focus calibration effort where the formula actually discriminates.**

### 4.4 The Kappa Paradox Is Real

Diag label-level κ values were low (0.000 to 0.444) despite 85–95% agreement. This is the well-known kappa paradox: when base rates are extreme (19/20 true), even high agreement produces low κ because expected chance agreement is also high.

**Lesson 10: Don't evaluate individual labels on κ alone when prevalence is extreme. Use agreement rate alongside κ, and evaluate the derived score (which combines labels and has more balanced distribution) as the primary reliability metric.**

## 5. Fabrication: The Remaining Challenge

Fabrication didn't need label decomposition — it's already binary. But κ = 0.580 after introducing a detector-first workflow, down from 0.000 (Raven never checked) but still failing.

Root cause: two complementary blind spots:
1. **Automated detector** catches name-based fabrication (non-existent configs, env vars, imports)
2. **Manual review** catches semantic fabrication (wrong function signatures, fabricated issue references, non-existent APIs with plausible names)

Neither is complete alone. The fix is requiring both checks, with adjudication for disagreements.

**Lesson 11: When your dimension has two distinct failure modes (name-based vs. semantic fabrication), a single process can't catch both. Design the workflow to combine complementary detection methods, not to rely on either one alone.**

## 6. Meta-Lessons for Rubric Design

### 6.1 The Rubric Design Loop

```
Define criteria → Score sample → Compute IAA → Analyze disagreements
     ↑                                                    ↓
     ← ← ← ← ← Revise rubric ← ← ← ← ← ← ← ← ← ← ←
```

Most teams iterate on step "Revise rubric" by adjusting descriptions, adding examples, and sharpening boundaries. We did this for 8 iterations (v2.0–v2.8) with diminishing returns.

The breakthrough came from changing the loop itself: instead of revising the rubric, we **restructured the scoring task** from "assign a number" to "classify features, then compute."

**Lesson 12: If you've iterated the rubric 3+ times and κ hasn't improved, the problem isn't the rubric's content — it's the rubric's structure. Consider decomposing the scoring task rather than refining it.**

### 6.2 When to Use Label-Based Scoring

Label decomposition works best when:
- Disagreements are synthesis problems (scorers agree on observations but differ on combination)
- The scoring dimension can be decomposed into 3–6 independent observable features
- Bright-line tests exist for each feature (observable, not judgment-based)
- You can write a deterministic formula that encodes your priority rules

It works less well when:
- Disagreements are genuine perceptual differences (scorers see different things)
- The dimension is holistic and resists decomposition (e.g., "writing quality")
- The number of relevant features exceeds 8–10 (label fatigue)

### 6.3 Cost-Benefit

| | Direct Scoring | Label-Based Scoring |
|---|---|---|
| Design effort | Lower | Higher (labels + formula + calibration) |
| Scorer effort per case | Lower (one judgment) | Higher (4–5 judgments + rationales) |
| Reliability (κ) | Variable, often below target | High after calibration |
| Transparency | Low (opaque number) | High (rationale per label) |
| Debuggability | Hard (which part of the score is wrong?) | Easy (which label is wrong?) |

The upfront investment in label design pays for itself in reduced calibration rounds, fewer disagreements to adjudicate, and more trustworthy results.
