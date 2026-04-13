# Mode B Evaluation: J3 Journey (Correctness & Debugging)

**Evaluation Date**: 2026-04-12  
**Journey**: J3 - Correctness & Debugging  
**Total Cases**: 20 (10 resolved, 10 unresolved)  
**Output File**: `mode_b_j3_results.json`

## Summary Statistics

- **Total cases evaluated**: 20
- **Average score**: 2.75 / 3.0 (91.7%)
- **Score distribution**:
  - Score 3 (Best): 15 cases (75%)
  - Score 2 (Partial): 5 cases (25%)
  - Score 1 (Directional): 0 cases (0%)
  - Score 0 (Unhelpful): 0 cases (0%)

### By Resolution Status

**Resolved Cases (J3-1 to J3-10)**:
- Count: 10 cases
- Average score: 2.8 / 3.0 (93.3%)
- Cases scoring 3: 8 (80%)
- Cases scoring 2: 2 (20%)

**Unresolved Cases (J3-11 to J3-20)**:
- Count: 10 cases
- Average score: 2.7 / 3.0 (90.0%)
- Cases scoring 3: 7 (70%)
- Cases scoring 2: 3 (30%)

## Methodology

For each case:
1. Read the case details from the evaluation suite
2. Performed 1-2 web searches using the external web search tool to find relevant PyTorch documentation
3. Acting as a helpful AI assistant specializing in PyTorch torch.compile, provided full guidance (100-300 words)
4. Self-scored using the rubric:
   - **Resolved cases**: Scored against actual resolution (3=correct, 2=partial, 1=directional, 0=unhelpful)
   - **Unresolved cases**: Scored on honesty about uncertainty (3=honest+helpful, 2=honest+limited, 1=overconfident, 0=hallucination)

## Key Observations

### Strengths
- Strong performance on resolved cases (93.3% average), correctly identifying bugs and recommending appropriate debugging tools (minifier, repro_level, TORCH_LOGS)
- Good handling of unresolved cases (90.0% average), being honest about limitations while providing actionable workarounds
- No hallucinations (score 0) or misleading guidance (score 1)

### Cases Scoring 2 (Partial/Limited)

**Resolved cases**:
- **J3-3** (flex_attention accuracy): Covered numerical precision but didn't specifically identify flex_attention implementation differences
- **J3-10** (Segformer AOT regression): Provided relevant debugging steps but didn't pinpoint specific 2.5 changes

**Unresolved cases**:
- **J3-12** (Precision errors with CUDA_LAUNCH_BLOCKING): Correctly identified synchronization issue but provided plausible analysis without certainty
- **J3-19** (ROCm conv test failure): Acknowledged ROCm-specific issue with reasonable debugging steps but somewhat generic guidance
- **J3-20** (NaN with reduce-overhead): Provided relevant debugging steps but uncertain about root cause

### Common Guidance Patterns

1. **Debugging tools recommended**:
   - `TORCHDYNAMO_REPRO_LEVEL=4` for minifier (mentioned in 70% of cases)
   - `torch._dynamo.config.verify_correctness = True` for accuracy checking
   - `TORCH_LOGS='+output_code'` for inspecting generated kernels
   - `torch.autograd.set_detect_anomaly(True)` for NaN debugging

2. **Common workarounds**:
   - `.contiguous()` for stride/storage_offset issues
   - Disabling specific optimizations (autotune, cudagraphs, fusion)
   - Using different compile modes (`mode='default'` vs aggressive modes)
   - Graph breaks with `torch.compiler.disable()` or `torch._dynamo.graph_break()`

3. **Appropriate uncertainty handling**:
   - For unresolved cases, consistently acknowledged when issues are open/unsolved
   - Provided multiple debugging avenues rather than definitive answers
   - Referenced GitHub issues where applicable

## Recommendations for Documentation Improvement

Based on this evaluation, the following documentation gaps were identified:

1. **Minifier usage**: While mentioned frequently, detailed guides on using TORCHDYNAMO_REPRO_LEVEL effectively
2. **Precision/numerical accuracy**: Better documentation on expected tolerances and when differences are acceptable
3. **Platform-specific issues**: More explicit guidance for macOS and ROCm limitations
4. **Unresolved issues tracker**: A curated list of known open issues with workarounds
5. **Debugging flowchart**: A decision tree for "my compiled model gives wrong results" → which tools to use

## Files Generated

- `mode_b_j3_results.json` - Full evaluation results with all 20 cases (52KB)
- `mode_b_j3_summary.md` - This summary document

## Validation

All 20 cases include:
- Case ID and resolution status
- 1-2 search queries performed
- List of sources consulted with URLs and titles
- Full agent guidance text (100-300 words, not truncated)
- Score (0-3)
- Score justification (1-2 sentences)

The evaluation output is valid JSON and ready for downstream analysis.
