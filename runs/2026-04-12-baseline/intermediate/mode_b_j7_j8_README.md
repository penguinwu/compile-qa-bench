# DOC-RESTRICTED Mode B Evaluation: J7 & J8 Cases

## Overview

This evaluation tests an AI agent's ability to provide guidance on torch.compile issues using **ONLY official pytorch.org documentation**. The agent is strictly prohibited from using GitHub issues, forums, StackOverflow, or any non-official sources.

## Evaluation Scope

- **Total Cases**: 40
  - J7 (Compile-Time Performance): 20 cases (10 resolved, 10 unresolved)
  - J8 (Runtime Errors): 20 cases (10 resolved, 10 unresolved)

## Key Results

### Overall Performance
- **Average Score**: 1.82 / 3.0
- **Documentation Sufficiency**: Only 5% of cases (2/40) had adequate official documentation

### Score Breakdown
- **Resolved Cases** (J7-1 to J7-10, J8-1 to J8-10):
  - Expected: Score 2-3 (should provide correct/relevant guidance)
  - Actual Average: 0.65 / 3.0
  - **Finding**: Official docs insufficient for most real-world issues

- **Unresolved Cases** (J7-11 to J7-20, J8-11 to J8-20):
  - Expected: Score 3 (should acknowledge docs don't cover issue)
  - Actual Average: 3.00 / 3.0
  - **Finding**: Agent correctly identified documentation gaps without fabricating solutions

## What This Evaluation Reveals

### Official Documentation Strengths
✅ Basic torch.compile usage and API reference
✅ Regional compilation for cold start optimization
✅ Dynamic shapes configuration
✅ AOTInductor for ahead-of-time compilation
✅ FlexAttention feature blogs
✅ Control flow (torch.cond) basics

### Critical Documentation Gaps
❌ Advanced configuration flags (inline_inbuilt_nn_modules, etc.)
❌ Optimizer compilation patterns
❌ Learning rate scheduler integration
❌ Comprehensive torch.library/custom ops guide
❌ while_loop and higher-order ops (beyond cond)
❌ Stateful modules in control flow
❌ Complex tensor support status
❌ Platform-specific behaviors (Windows caching)
❌ Performance regression debugging
❌ Production readiness indicators
❌ torch.scan functional primitives
❌ Third-party library compatibility

## Files

1. **mode_b_doc_restricted_j7_j8.json** (58 KB)
   - Complete evaluation results with all 40 cases
   - Each entry includes:
     - Search queries used
     - Official sources found (pytorch.org only)
     - Non-official sources skipped
     - Agent guidance text (100-300 words)
     - Documentation sufficiency assessment
     - Score (0-3) and justification

2. **mode_b_j7_j8_summary.md**
   - Detailed statistical analysis
   - Documentation coverage assessment
   - Key findings and conclusions

## Methodology

For each case:
1. Performed 1-2 web searches targeting official pytorch.org documentation
2. Filtered results to ONLY include pytorch.org sources
3. Counted non-official sources that were skipped
4. Generated guidance based solely on official documentation
5. Assessed whether official docs were sufficient
6. Scored according to rubric:
   - **Resolved cases**: 3 = matches solution, 2 = relevant guidance, 1 = right area but vague, 0 = unhelpful
   - **Unresolved cases**: 3 = acknowledges gap, 2 = "I don't know", 1 = plausible but wrong, 0 = fabricates answer

## Implications

This evaluation demonstrates that **official PyTorch documentation alone is insufficient** for addressing the majority of real-world torch.compile issues encountered by users. The 0.65 average score for resolved cases indicates that:

1. Official docs cover common usage patterns but not edge cases
2. Troubleshooting guidance is limited
3. Advanced features lack comprehensive documentation
4. Configuration options are under-documented
5. Integration patterns (optimizers, schedulers, custom ops) are poorly covered

**For effective torch.compile support**, documentation should be supplemented with:
- GitHub issue database access
- Community forum discussions
- Source code inspection
- Developer discussions and RFCs

## Data Integrity

✅ All 40 cases validated
✅ All sources verified as pytorch.org URLs
✅ No fabricated configuration flags or APIs
✅ Honest acknowledgment of documentation gaps
✅ Consistent scoring methodology applied

## Usage

```python
import json

# Load evaluation results
with open('mode_b_doc_restricted_j7_j8.json', 'r') as f:
    results = json.load(f)

# Analyze a specific case
j7_1 = next(r for r in results if r['id'] == 'J7-1')
print(f"Case J7-1 Score: {j7_1['score']}")
print(f"Official Sources: {len(j7_1['official_sources_used'])}")
print(f"Guidance: {j7_1['agent_guidance'][:200]}...")
```

## Contact

For questions about this evaluation or the methodology, see the parent project documentation.
