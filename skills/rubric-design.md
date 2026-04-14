# Skill: Rubric Design

How to design a scoring rubric that two independent scorers can apply consistently.

## Core Principles

### 1. Separate Independent Dimensions

Never conflate orthogonal judgments into a single score. If scorers disagree, ask: are they weighing the same question differently, or answering different questions?

Example: "Did the agent get the right answer?" and "Can the user act on it?" are independent. A correct diagnosis with no actionable guidance is Diagnosis=3, Actionability=0. Forcing both into one score guarantees disagreement.

### 2. Every Boundary Needs a Bright-Line Test

A bright-line test is an observable property of the text — not a judgment call. Replace subjective terms with mechanical tests.

| Subjective (causes disagreement) | Bright-line (reproducible) |
|---|---|
| "meaningful guidance" | "contains at least one imperative verb directed at user" |
| "materially closer" | "user can identify a next step they could NOT have identified before" |
| "right area, imprecise" | "asserts a case-specific causal chain referencing user's symptom" |
| "generic advice" | "same text would appear in response to a different case" |

The interchangeability test is your best friend: "Would this same [score/text/advice] apply to a different case?" If yes, it's the lower level.

### 3. Audit Boundaries Proactively

Don't wait for kappa to reveal fuzziness. For each boundary in your rubric, ask:
- Is there a mechanical test? (SHARP)
- Are there subjective terms requiring scorer judgment? (ADEQUATE at best)
- Are there common response patterns that fall exactly on the boundary with no clear rule? (FUZZY)

Fix FUZZY boundaries before scoring. Fix ADEQUATE boundaries after the first scoring round reveals disagreement clusters.

### 4. Priority Rules for Conflicting Tests

When two rules apply to the same case, the rubric MUST state which takes priority. Example: "Template responses contain imperatives. The template rule overrides the imperative test — template = Act=0 regardless of imperatives."

Never leave priority implicit.

## Scale Design

### Level Count

Use the minimum levels that capture meaningful distinctions. More levels = more boundary disputes.

- 4 levels is typical for ordinal dimensions (0-3)
- Some levels may be empty on a given dataset — that's fine if the scale is designed for measuring improvement over time
- Binary dimensions (yes/no) are best for clear-cut properties (fabrication)

### Empty Middle Levels

If both scorers skip a middle level (e.g., Diag=2 used in 4/160 cases by one scorer, 0/160 by the other), the level's definition is too vague. Options:
1. Sharpen the boundary with a brighter-line test
2. Accept it's empty on this dataset but keep it for future measurement sensitivity

Choose based on whether the dataset will change. If you're measuring improvement over time, keep the level.

### Granularity vs Agreement Tradeoff

High kappa with a coarse scale (binary) is easy but useless for measuring improvement. Low kappa with a fine scale (0-10) means the rubric isn't reliable. Find the sweet spot: enough granularity to detect real improvement, tight enough for κ≥0.80.

## Anti-Patterns

### Subjective Anchors
"The agent provides useful information" — what's useful? To whom? Define in terms of observable properties.

### Implicit Scoring Interactions
"If fabrication is detected, cap the overall score at 1" — this creates hidden dependencies. Score each dimension independently, apply caps in analysis.

### Undefined Resolution for Track/Context Differences
A doc-restricted agent saying "docs don't cover this" is a correct diagnosis (Diag=3). An unrestricted agent saying the same thing is a failure (Diag=1). The rubric must explicitly define how context/constraints affect scoring.

## Checklist: Before Deploying a Rubric

- [ ] Each dimension answers exactly one question
- [ ] Every boundary has a bright-line test or worked example
- [ ] No subjective terms without operational definitions
- [ ] Edge cases are explicitly handled (gap acknowledgment, template responses, "file a bug")
- [ ] Priority rules stated for any conflicting tests
- [ ] Track/context rules specified (if applicable)
- [ ] At least 3 worked examples per dimension, including boundary cases
