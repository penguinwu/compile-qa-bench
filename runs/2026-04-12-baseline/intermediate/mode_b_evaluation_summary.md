# DOC-RESTRICTED Mode B Evaluation Summary

## Overview

Evaluated 40 torch.compile documentation cases (J3-1 through J3-20 and J4-1 through J4-20) using **ONLY** official pytorch.org documentation.

**Constraint:** Agent could only use information from official pytorch.org pages (docs.pytorch.org, pytorch.org/tutorials, pytorch.org/blog). All GitHub issues, StackOverflow, forums, blogs, and other non-pytorch.org sources were ignored.

## Results

### Score Distribution
- **Score 1:** 11 cases (27.5%)  - Limited guidance, too vague to be actionable
- **Score 2:** 29 cases (72.5%)  - Relevant guidance or appropriate acknowledgment of limitations

### By Resolution Status
- **Resolved cases (X-1 to X-10):** 20 cases, average score: **1.45**
  - These are real bugs that were fixed in PyTorch
  - Official docs often lack the specific debugging tools (minifier, repro_level) needed to solve them
  
- **Unresolved cases (X-11 to X-20):** 20 cases, average score: **2.00**
  - Agent correctly acknowledges documentation gaps and suggests workarounds
  - For unresolved issues, saying "I don't know" or "check GitHub" is appropriate

### Overall Average Score: **1.73 / 3.0**

## Key Findings

### Documentation Available (Good Coverage)
1. **Graph Breaks & Debugging** - torch.compile troubleshooting docs + TorchDynamo deep dive provide TORCH_LOGS debugging
2. **Dynamic Shapes** - Comprehensive official documentation with debugging tools
3. **Caching Configuration** - Tutorial covers FX graph cache setup
4. **Logging (TORCH_LOGS)** - Well-documented debugging tool

### Documentation Gaps (Limited or Missing)
1. **Minifier & repro_level** - Internal debugging tools not in public docs
2. **Accuracy debugging tools** - No systematic correctness debugging guide
3. **float8 + compile integration** - Blog introduces float8 but no debugging procedures
4. **DDP/FSDP + compile** - Distributed training and compile covered separately, not integration
5. **Migration guides** - No breaking changes documentation across versions
6. **Backend-specific debugging** - Limited troubleshooting for Inductor correctness issues
7. **flex_attention debugging** - Blog introduces feature but no accuracy debugging guide

## Official Sources Used

Found and used 15 official pytorch.org documentation sources:
- 5 docs.pytorch.org documentation pages
- 4 pytorch.org blog posts  
- 1 pytorch.org tutorials page
- Typical searches skipped 3-5 non-official sources per case

## Evaluation Methodology

For each case:
1. Read case question and expected topics from cases.json
2. Performed 1-2 web searches with "site:pytorch.org" filter
3. Filtered results to ONLY pytorch.org URLs
4. Generated guidance based exclusively on official documentation
5. Self-scored using rubric:
   - **Resolved cases:** 3=matches resolution, 2=relevant but incomplete, 1=too vague, 0=wrong
   - **Unresolved cases:** 3=acknowledges+workarounds, 2=admits unknown, 1=plausible but wrong, 0=fabricated answer

## Conclusion

The official PyTorch documentation provides:
- ✅ Good coverage of core features (dynamic shapes, graph breaks, caching)
- ✅ Essential debugging tool (TORCH_LOGS) is well documented
- ❌ Limited coverage of advanced debugging tools (minifier, repro_level)
- ❌ Few guides for debugging correctness/accuracy issues
- ❌ Integration scenarios (DDP+compile, float8+compile) not well documented

For a DOC-RESTRICTED agent with only official docs, the average score of 1.73/3.0 indicates that about half the cases can get relevant guidance, but many lack the specific tools needed for actionable debugging.
