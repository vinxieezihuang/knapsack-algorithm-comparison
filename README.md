# Knapsack Algorithm Comparison

## Overview
This repository contains a comparative study of two optimization approaches for the **0/1 Knapsack Problem** :

- **Best-first Branch and Bound**
- **Genetic Algorithm**

The project evaluates how an exact search method and an evolutionary method behave under different instance structures, with comparison focused on:

- **runtime**
- **solution quality**
- **reliability**

The study was implemented in Python and documented in a formal report.

---

## Problem Description
The **0/1 Knapsack Problem** is a combinatorial optimization problem where each item must be either fully selected or fully rejected.

Each item has:
- a **weight**
- a **value**

The objective is to select a subset of items that **maximizes total value** without exceeding a fixed knapsack capacity.

This problem is a strong benchmark for comparing optimization methods because it has:
- a clear mathematical objective,
- a hard feasibility constraint,
- and an exponentially growing search space.

---

## Algorithms Compared

### 1. Best-first Branch and Bound
This is the **exact search method** used in the study.

Key characteristics:
- deterministic search
- expands the most promising node first
- uses **fractional knapsack relaxation** to compute an upper bound
- prunes branches that cannot beat the current best solution
- can guarantee optimality if allowed to complete

### 2. Genetic Algorithm
This is the **evolutionary method** used in the study.

Key characteristics:
- stochastic population-based search
- binary chromosome representation
- tournament selection
- one-point crossover
- bit-flip mutation
- elitism
- feasibility repair for overweight solutions

Unlike Branch and Bound, the Genetic Algorithm does **not** guarantee optimality, but it offers more stable runtime under fixed search budgets.

---

## Experimental Design
The two algorithms were evaluated on the same generated instances using a common binary solution representation.

### Instance families
- **Uncorrelated**
- **Strongly correlated**

### Problem sizes
- 50 items
- 100 items
- 150 items
- 200 items

### Evaluation metrics
- runtime
- optimality gap
- exact / optimum-hit rate
- reliability across repeated runs

### Additional setup
- A **dynamic programming oracle** was used to compute the true optimum for comparison.
- Branch and Bound used a **5-second time limit** per instance.
- The Genetic Algorithm used fixed parameters for population size, generations, crossover, mutation, and elitism.

---

## Key Findings
The results show that performance depends strongly on instance structure.

### On uncorrelated instances
- Branch and Bound achieved **exact solutions extremely quickly** .
- It maintained a **0.0% mean gap** and **100% exact success rate** across all tested sizes.
- The Genetic Algorithm also produced high-quality solutions, but its optimum-hit rate declined as problem size increased.

### On strongly correlated instances
- Branch and Bound became less effective because similar value-to-weight ratios weakened pruning.
- The Genetic Algorithm became more competitive due to:
  - more stable runtime,
  - strong feasible solution quality,
  - and lower sensitivity to instance structure.

### Main conclusion
Neither algorithm is uniformly superior.

- **Branch and Bound** is preferable when **certified optimality** is required.
- **Genetic Algorithm** is more attractive when **predictable runtime** and **high-quality near-optimal solutions** are sufficient.

---

## Repository Structure

```text
knapsack-algorithm-comparison/
├── README.md
├── requirements.txt
├── knapsack_compare.py
└── knapsack-comparison-report.pdf
