# Knapsack Algorithm Comparison

## Overview
This repository contains a report comparing an exact search algorithm and an evolutionary algorithm on the **0/1 Knapsack Problem** .

The study evaluates:
- **Best-first Branch and Bound**
- **Genetic Algorithm**

The comparison focuses on three dimensions:
- runtime
- solution quality
- reliability

## Problem
The 0/1 Knapsack Problem is a combinatorial optimization problem where each item must be either fully selected or rejected. The objective is to maximize total value without exceeding a fixed weight capacity.

## Methods Compared
### 1. Best-first Branch and Bound
- deterministic exact search
- uses fractional knapsack relaxation for upper-bound pruning
- guarantees optimality if completed

### 2. Genetic Algorithm
- stochastic population-based search
- uses binary encoding, tournament selection, crossover, mutation, elitism, and feasibility repair
- provides high-quality feasible solutions under fixed computational budgets

## Experimental Setup
The report evaluates both methods on:
- **uncorrelated instances**
- **strongly correlated instances**

Problem sizes tested:
- 50 items
- 100 items
- 150 items
- 200 items

Evaluation metrics:
- runtime
- optimality gap
- exact / optimum-hit rate

## Key Findings
- Branch and Bound performed extremely well on uncorrelated instances, achieving exact solutions very quickly.
- On strongly correlated instances, pruning became weaker and the Genetic Algorithm became more competitive.
- The comparison highlights a clear trade-off between:
  - **certified optimality**
  - **predictable runtime with high-quality solutions**

## Files
- `knapsack-comparison-report.pdf` — final report
- `knapsack-comparison-report.docx` — editable source document
- `knapsack_compare.py` — Python implementation (if included)
- `output/` — generated charts or experiment outputs (if included)

## Tools and Technologies
- Python
- Branch and Bound
- Genetic Algorithm
- Dynamic Programming
- Matplotlib

## Author
Zi Huang Yew
