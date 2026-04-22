# Visibility Classification

Every file and data element in this repo carries an implicit visibility level.
Before pushing any content, classify it using these rules.

## Levels

| Level | Meaning | Can push externally? |
|-------|---------|---------------------|
| `oss` | Derived from public/open source data | ✅ Yes |
| `internal` | Meta-internal, not competitive | ❌ No |
| `confidential` | Proprietary, sensitive, or competitive | ❌ No — restricted |

## What's Safe (`oss`)

- Open source code, configs, and flags from public PyTorch repos
- Public GitHub handles, issue numbers, PR numbers
- PyTorch version numbers and release dates
- Public benchmark results (TorchBench, HuggingFace)
- Error messages and stack traces from public GitHub issues
- Content from public conference talks or blog posts
- Generic diagnostic patterns and workarounds using public APIs

## What's NOT Safe (`internal` or `confidential`)

### `internal` — never push
- Employee names, unixnames, or @meta.com/@fb.com emails
- Facebook IDs (FBIDs)
- References to internal tools (Scuba, Chronos, Configerator, Tupperware, etc.)
- Internal Workplace group links or GChat space IDs
- Oncall rotation information
- Internal team structure or org mappings
- Phabricator diff numbers (Dxxxx)
- Internal wiki or documentation links

### `confidential` — never push, restricted access
- Internal model names (ads models, pre-release LLMs)
- Performance numbers tied to specific internal workloads
- Internal model architecture details
- Customer-specific workarounds that reveal business relationships
- Security vulnerabilities not yet disclosed
- SEV details

## Scrubbing Rules

When content from internal sources needs to be included:

1. **People**: Remove names, unixnames, emails. Use role descriptions if attribution matters ("a compiler engineer reported...")
2. **Models**: Replace specific model names with generic categories ("internal ads model", "internal LLM")
3. **Performance**: Relative comparisons OK ("2x slower"). Absolute numbers tied to internal workloads → remove.
4. **Workarounds**: The config/API itself is often `oss`. The internal context around it is `internal`. Separate them.

## Before Every Push

1. Review all staged changes against this classification
2. Run: `git diff --cached | grep -iE '@meta\.com|@fb\.com|fbid|workplace\.com|intern\.facebook'`
3. If any match → scrub before pushing
4. When in doubt → don't push. Ask for review.

## Review Standard

Ask yourself: "If this content appeared on a public website, would it reveal anything proprietary about Meta?"
If yes → classify as `internal` or `confidential`.
