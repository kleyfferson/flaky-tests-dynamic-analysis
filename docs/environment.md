# System Environment

All experiments were conducted on a workstation with the following specifications:

- **CPU**: Intel Core i9-14900KF (3.2 GHz base clock)
- **RAM**: 64 GB DDR5 (5600 MHz)
- **Storage**: 1 TB NVMe SSD
- **Operating System**: Linux Mint 22.1
- **Kernel**: 6.8.0-110-generic, x86-64 architecture
- **Python**: 3.12

## Execution Parameters

- Each test was executed **400 times** per analysis.
- Executions were performed separately for:
  - Code coverage
  - Profiling
  - Function-level tracing
  - No dynamic analysis (baseline)
- **16 CPU workers** were allocated for the experimental load in each analysis.
