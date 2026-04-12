# pytorch.org Compile Documentation Inventory (2026-04-12)

Reference for Coverage scoring. ~58 unique pages found.

## Core Reference
- torch.compile API: docs.pytorch.org/docs/stable/generated/torch.compile.html
- torch.compiler API: docs.pytorch.org/docs/stable/torch.compiler_api.html
- Getting Started: docs.pytorch.org/docs/stable/torch.compiler_get_started.html

## Troubleshooting & Debugging
- Troubleshooting: docs.pytorch.org/docs/stable/torch.compiler_troubleshooting.html
- FAQ: docs.pytorch.org/docs/stable/torch.compiler_faq.html
- Profiling: docs.pytorch.org/docs/stable/torch.compiler_profiling_torch_compile.html
- Inductor GPU Profiling: docs.pytorch.org/docs/stable/torch.compiler_inductor_profiling.html
- Logging: docs.pytorch.org/docs/stable/logging.html
- torch._logging recipe: docs.pytorch.org/tutorials/recipes/torch_logs.html

## Dynamo (Frontend)
- Dynamo Overview: docs.pytorch.org/docs/stable/torch.compiler_dynamo_overview.html
- Deep Dive: docs.pytorch.org/docs/stable/torch.compiler_deepdive.html
- Guards Overview: docs.pytorch.org/docs/stable/torch.compiler_guards_overview.html

## Dynamic Shapes
- Dynamic Shapes: docs.pytorch.org/docs/stable/user_guide/torch_compiler/torch.compiler_dynamic_shapes.html
- Core Concepts: docs.pytorch.org/docs/stable/user_guide/torch_compiler/compile/dynamic_shapes_core_concepts.html

## Caching
- Caching Tutorial: docs.pytorch.org/tutorials/recipes/torch_compile_caching_tutorial.html

## Custom Ops
- torch.library API: docs.pytorch.org/docs/stable/library.html
- Custom Python Operators: docs.pytorch.org/tutorials/advanced/python_custom_ops.html
- Custom Backends: docs.pytorch.org/docs/stable/torch.compiler_custom_backends.html

## FlexAttention
- API: docs.pytorch.org/docs/stable/nn.attention.flex_attention.html
- Blog: pytorch.org/blog/flexattention/

## Tutorials
- End-to-End: docs.pytorch.org/tutorials/intermediate/torch_compile_full_example.html
- Compiled Autograd: docs.pytorch.org/tutorials/intermediate/compiled_autograd_tutorial.html
- Triton Kernels: docs.pytorch.org/tutorials/recipes/torch_compile_user_defined_triton_kernel_tutorial.html
- Regional Compilation: docs.pytorch.org/tutorials/recipes/regional_compilation.html
- Transformers + compile: docs.pytorch.org/tutorials/intermediate/transformer_building_blocks.html

## Inductor
- CUDAGraph Trees: docs.pytorch.org/docs/stable/torch.compiler_cudagraph_trees.html
- Graph Transformations: docs.pytorch.org/docs/stable/user_guide/torch_compiler/torch.compiler_transformations.html

## Other
- nn.Module Support: docs.pytorch.org/docs/stable/torch.compiler_nn_module.html
- Performance Dashboard: docs.pytorch.org/docs/stable/torch.compiler_performance_dashboard.html
- AOT Autograd: docs.pytorch.org/functorch/1.13/notebooks/aot_autograd_optimizations.html
- FX IR: docs.pytorch.org/docs/stable/fx.html

## Notable Gaps
- No dedicated "graph breaks" reference page (only in troubleshooting/FAQ)
- No torch.scan / higher-order ops page
- No "how to reduce recompilations" guide
- No compile + quantization integration guide
- No tensor subclasses + compile page
- No standalone compiled autograd reference (only tutorial)
