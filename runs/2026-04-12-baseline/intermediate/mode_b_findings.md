# DOC-RESTRICTED Mode B Evaluation - Findings

## Evaluation Overview

**Mode**: DOC-RESTRICTED Mode B (official pytorch.org documentation only)  
**Cases Evaluated**: 40 (J1-1 through J1-20, J2-1 through J2-20)  
**Date**: 2026-04-12  
**Constraint**: Only official pytorch.org sources allowed; GitHub issues, forums, blogs excluded

## Summary Statistics

- **Total cases**: 40
- **Resolved cases**: 20 (50%)
- **Unresolved cases**: 20 (50%)
- **Overall average score**: 1.90/3.00
- **Documentation sufficient**: 9 cases (22.5%)
- **Documentation insufficient**: 31 cases (77.5%)

### Score Distribution

| Score | Count | Percentage | Meaning |
|-------|-------|------------|---------|
| 0 | 4 | 10.0% | Doesn't help or is wrong |
| 1 | 7 | 17.5% | Right area but too vague |
| 2 | 18 | 45.0% | Relevant but incomplete / "I don't know" |
| 3 | 11 | 27.5% | Matches resolution or good workaround |

### Average Scores by Resolution Status

- **Resolved cases**: 1.80/3.00
- **Unresolved cases**: 2.00/3.00

The higher score for unresolved cases reflects that "I don't know" is the appropriate response when official documentation doesn't exist, earning score 2.

## Documentation Gap Analysis

### Well-Documented Topics (Score 3 cases)

1. **Compile caching** (J1-1, J1-9): FX graph cache environment variables and configuration
2. **Backend selection** (J1-2): How to change backends via the `backend` parameter
3. **Compilation warmup** (J1-5): Expected first-call overhead and warmup behavior
4. **Performance profiling** (J2-1, J2-9): torch.profiler and troubleshooting methodology
5. **Small model overhead** (J2-3): When torch.compile helps vs hurts
6. **No speedup diagnosis** (J2-6): Understanding when eager is already optimal

### Partially Documented Topics (Score 1-2)

1. **DDP + AMP ordering** (J1-3): Individual features documented but not their interaction
2. **Installation requirements** (J1-4): PyTorch install docs don't mention C++ compiler needs
3. **Gradient checkpointing** (J1-10): Feature documented but compile compatibility unclear
4. **Operator coverage** (J2-10): Fallbacks mentioned but no comprehensive op list
5. **Version regressions** (J2-4): Profiling tools exist but no changelog for compile

### Completely Undocumented Topics (Score 0 or minimal)

1. **Tensor Parallel + compile** (J1-6): No docs on using torch.compile with TP/DTensor
2. **torch.cuda.set_device() behavior** (J1-7): Interaction with compile not documented
3. **Triton/CUDA errors** (J1-8): No troubleshooting for backend compiler errors
4. **torch.autograd.grad tracing** (J1-12): Known limitation not listed
5. **RNN/GRU support** (J1-13): No documentation of unsupported architectures
6. **Multiprocessing compatibility** (J1-14): Daemon process issues not documented
7. **MXFP8 quantization** (J1-15): Advanced quantization not in official docs
8. **Complex dtype support** (J1-16): No documentation of complex number limitations
9. **Windows setup** (J1-17): No Windows-specific compiler setup guide
10. **Pattern matcher internals** (J1-18): Internal optimization behavior not exposed
11. **Linker errors** (J1-19): No guidance on library path configuration
12. **GIL release behavior** (J2-7): Threading behavior not documented
13. **flex_attention** (J2-8): API not in official docs
14. **Float8 training** (J2-13): Experimental feature not documented
15. **Inductor codegen internals** (J2-14): Implementation details not exposed
16. **SDPA backend interaction** (J2-15): Compile + SDPA compatibility not covered
17. **Fusion heuristics** (J2-16): Optimization decisions not documented
18. **torch._foreach operations** (J2-17): Private API not documented
19. **Intel GPU / XPU** (J2-20): Not upstream in official docs

## Key Patterns

### 1. Basic vs Advanced Features

**Well-documented**: Basic torch.compile usage, caching, backend selection, profiling  
**Poorly-documented**: Advanced features (distributed, quantization, RNNs, complex dtypes)

### 2. Feature Documentation vs Integration Documentation

Many features are documented in isolation (e.g., DDP, AMP, gradient checkpointing) but their interaction with torch.compile is not covered. This creates a gap where users combining features encounter undocumented behavior.

### 3. Troubleshooting Gaps

While high-level troubleshooting guides exist, specific error classes are not documented:
- CUDA/Triton compilation errors
- Linker errors with non-standard installations
- Multi-process cache corruption
- Platform-specific issues (Windows)

### 4. Experimental/Internal Features

Many advanced features appear to be experimental or internal:
- Float8 quantization
- MXFP8
- torch._foreach operations
- Pattern matcher behavior
- Inductor codegen strategy

These lack official documentation, making it difficult for users to understand limitations or file actionable bug reports.

## Recommendations for Documentation Improvements

### High Priority

1. **Compatibility matrix**: Document which features work with torch.compile
   - Distributed: DDP, FSDP, Tensor Parallel
   - Quantization: which dtypes and schemes are supported
   - RNN architectures: explicit support status

2. **Installation guide**: System requirements beyond PyTorch
   - C++ compiler requirements (Linux, macOS, Windows)
   - CUDA library path configuration
   - Platform-specific setup

3. **Error troubleshooting**: Common error categories
   - Backend compilation failures (Triton, CUDA)
   - Linker errors and library paths
   - Multi-process/distributed issues

4. **Operator coverage**: Publicly document
   - Which operations are fully supported by inductor
   - Which operations fall back to eager
   - Known performance characteristics

### Medium Priority

5. **Integration guides**: How torch.compile interacts with:
   - Mixed precision training (AMP)
   - Gradient checkpointing
   - Different SDPA backends
   - Distributed training modes

6. **Performance expectations**:
   - When to expect speedups vs slowdowns
   - Model size and complexity thresholds
   - Version-to-version performance notes

7. **Multi-process safety**:
   - Cache safety in distributed settings
   - Multiprocessing compatibility
   - Ray/distributed framework guidance

### Low Priority

8. **Advanced topics** (for power users):
   - Inductor optimization heuristics
   - Custom pattern matching
   - Backend development guide

## Methodology Notes

- **Search strategy**: 1-2 web searches per case using natural language queries
- **Source filtering**: Strictly excluded non-pytorch.org URLs (GitHub, forums, blogs)
- **Scoring**: Conservative scoring focused on actionability of official docs alone
- **Non-official sources skipped**: 29 results excluded due to DOC-RESTRICTED constraint

## Conclusion

Official pytorch.org documentation covers **basic torch.compile usage** well (caching, backends, profiling) but has significant gaps in:

1. **Advanced features** (quantization, distributed, RNNs, complex dtypes)
2. **Feature integration** (compile + DDP + AMP, compile + checkpointing)
3. **Troubleshooting** (specific error classes, platform issues)
4. **Operator/architecture coverage** (what's supported vs not)

Only **22.5% of cases** had sufficient official documentation to provide complete guidance. The majority (77.5%) required information beyond official docs, suggesting substantial room for documentation improvement.

The **average score of 1.90/3.00** indicates that official docs provide directional guidance (point to relevant area) but often lack the specific information needed to resolve issues.
