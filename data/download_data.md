# Downloading the Raw Data

The raw data (400 executions for each analysis: coverage, profiling, tracing, and none)
is publicly available on Zenodo:

**Zenodo DOI**: https://zenodo.org/records/23484158

## Steps

1. Access the Zenodo link above.
2. Download the dataset archive(s).
3. Extract the contents into this directory (`data/`), creating a `results/` subfolder
   with the following structure:

   data/
   └── results/
       ├── coverage/
       ├── profiling/
       ├── tracing/
       └── none/

4. The analysis scripts in `analysis/` expect the data in this structure.

> **Note**: The `results/` directory is intentionally not tracked by Git due to its size
> (see `.gitignore`).
