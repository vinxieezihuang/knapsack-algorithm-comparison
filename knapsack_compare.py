import csv
import heapq
import math
import random
import statistics
import time
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt


OUTPUT_DIR = Path('/workspace/output')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


@dataclass
class Item:
    index: int
    weight: int
    value: int
    ratio: float


class KnapsackInstance:
    def __init__(self, weights, values, capacity, kind, seed):
        self.weights = list(weights)
        self.values = list(values)
        self.capacity = int(capacity)
        self.kind = kind
        self.seed = seed
        self.n = len(weights)


def generate_instance(n, kind, seed):
    rng = random.Random(seed)
    weights = [rng.randint(10, 100) for _ in range(n)]
    if kind == 'uncorrelated':
        values = [rng.randint(10, 100) for _ in range(n)]
    elif kind == 'strongly_correlated':
        values = [w + 10 for w in weights]
    else:
        raise ValueError(f'Unknown kind: {kind}')
    capacity = int(sum(weights) * 0.5)
    return KnapsackInstance(weights, values, capacity, kind, seed)


def dynamic_programming_optimum(instance):
    capacity = instance.capacity
    dp = [0] * (capacity + 1)
    for w, v in zip(instance.weights, instance.values):
        for c in range(capacity, w - 1, -1):
            candidate = dp[c - w] + v
            if candidate > dp[c]:
                dp[c] = candidate
    return max(dp)


def branch_and_bound(instance, time_limit=10.0):
    items = [
        Item(i, instance.weights[i], instance.values[i], instance.values[i] / instance.weights[i])
        for i in range(instance.n)
    ]
    items.sort(key=lambda x: x.ratio, reverse=True)
    start = time.perf_counter()

    def bound(level, weight, value):
        if weight >= instance.capacity:
            return value
        total_weight = weight
        total_value = value
        j = level
        while j < instance.n and total_weight + items[j].weight <= instance.capacity:
            total_weight += items[j].weight
            total_value += items[j].value
            j += 1
        if j < instance.n:
            remaining = instance.capacity - total_weight
            total_value += remaining * items[j].ratio
        return total_value

    best_value = 0
    best_taken_sorted = [0] * instance.n
    nodes_expanded = 0
    root_bound = bound(0, 0, 0)
    heap = [(-root_bound, 0, 0, 0, tuple())]

    while heap:
        if time.perf_counter() - start > time_limit:
            break
        neg_bound, level, weight, value, decisions = heapq.heappop(heap)
        upper = -neg_bound
        if upper <= best_value:
            continue
        if level == instance.n:
            continue
        nodes_expanded += 1
        item = items[level]

        new_weight = weight + item.weight
        new_value = value + item.value
        if new_weight <= instance.capacity:
            take_decisions = decisions + (1,)
            if new_value > best_value:
                best_value = new_value
                best_taken_sorted = list(take_decisions) + [0] * (instance.n - len(take_decisions))
            take_bound = bound(level + 1, new_weight, new_value)
            if take_bound > best_value:
                heapq.heappush(heap, (-take_bound, level + 1, new_weight, new_value, take_decisions))

        skip_decisions = decisions + (0,)
        skip_bound = bound(level + 1, weight, value)
        if skip_bound > best_value:
            heapq.heappush(heap, (-skip_bound, level + 1, weight, value, skip_decisions))

    elapsed = time.perf_counter() - start
    optimality_proven = len(heap) == 0

    sorted_to_original = [0] * instance.n
    for sorted_pos, item in enumerate(items):
        sorted_to_original[item.index] = best_taken_sorted[sorted_pos]

    return {
        'best_value': best_value,
        'solution': sorted_to_original,
        'runtime_sec': elapsed,
        'nodes_expanded': nodes_expanded,
        'optimality_proven': optimality_proven,
    }


def repair_solution(bits, instance):
    bits = bits[:]
    total_weight = sum(b * w for b, w in zip(bits, instance.weights))
    if total_weight > instance.capacity:
        selected = [i for i, b in enumerate(bits) if b == 1]
        selected.sort(key=lambda i: instance.values[i] / instance.weights[i])
        for i in selected:
            if total_weight <= instance.capacity:
                break
            bits[i] = 0
            total_weight -= instance.weights[i]
    unselected = [i for i, b in enumerate(bits) if b == 0]
    unselected.sort(key=lambda i: instance.values[i] / instance.weights[i], reverse=True)
    for i in unselected:
        if total_weight + instance.weights[i] <= instance.capacity:
            bits[i] = 1
            total_weight += instance.weights[i]
    return bits


def solution_value(bits, instance):
    weight = sum(b * w for b, w in zip(bits, instance.weights))
    value = sum(b * v for b, v in zip(bits, instance.values))
    return weight, value


def genetic_algorithm(instance, seed, population_size=100, generations=180, crossover_rate=0.9, mutation_rate=None, elite_size=2):
    rng = random.Random(seed)
    n = instance.n
    if mutation_rate is None:
        mutation_rate = 1.0 / n

    def random_individual():
        bits = [1 if rng.random() < 0.5 else 0 for _ in range(n)]
        return repair_solution(bits, instance)

    def fitness(individual):
        return solution_value(individual, instance)[1]

    def tournament(population, k=3):
        contestants = rng.sample(population, k)
        return max(contestants, key=fitness)

    def crossover(parent1, parent2):
        if rng.random() >= crossover_rate:
            return parent1[:], parent2[:]
        point = rng.randint(1, n - 1)
        child1 = parent1[:point] + parent2[point:]
        child2 = parent2[:point] + parent1[point:]
        return repair_solution(child1, instance), repair_solution(child2, instance)

    def mutate(individual):
        child = individual[:]
        for i in range(n):
            if rng.random() < mutation_rate:
                child[i] = 1 - child[i]
        return repair_solution(child, instance)

    start = time.perf_counter()
    population = [random_individual() for _ in range(population_size)]
    best = max(population, key=fitness)
    best_value = fitness(best)
    history = [best_value]

    for _ in range(generations):
        ranked = sorted(population, key=fitness, reverse=True)
        new_population = [ind[:] for ind in ranked[:elite_size]]
        while len(new_population) < population_size:
            p1 = tournament(ranked)
            p2 = tournament(ranked)
            c1, c2 = crossover(p1, p2)
            c1 = mutate(c1)
            c2 = mutate(c2)
            new_population.append(c1)
            if len(new_population) < population_size:
                new_population.append(c2)
        population = new_population
        current = max(population, key=fitness)
        current_value = fitness(current)
        if current_value > best_value:
            best = current[:]
            best_value = current_value
        history.append(best_value)

    elapsed = time.perf_counter() - start
    return {
        'best_value': best_value,
        'solution': best,
        'runtime_sec': elapsed,
        'history': history,
    }


def summarise(values):
    return statistics.mean(values), (statistics.pstdev(values) if len(values) > 1 else 0.0)


def run_experiments():
    sizes = [50, 100, 150, 200]
    kinds = ['uncorrelated', 'strongly_correlated']
    instances_per_setting = 3
    ga_runs_per_instance = 5
    bb_time_limit = 5.0

    summary_rows = []
    detailed_rows = []
    convergence_records = []

    for kind in kinds:
        for n in sizes:
            optimum_values = []
            bb_runtimes = []
            bb_nodes = []
            bb_gaps = []
            bb_success = 0

            ga_runtimes = []
            ga_gaps = []
            ga_success = 0
            ga_values_all = []

            for instance_id in range(instances_per_setting):
                seed = 1000 + (0 if kind == 'uncorrelated' else 5000) + n * 10 + instance_id
                instance = generate_instance(n, kind, seed)
                optimum = dynamic_programming_optimum(instance)
                optimum_values.append(optimum)

                bb_result = branch_and_bound(instance, time_limit=bb_time_limit)
                bb_gap = 100.0 * (optimum - bb_result['best_value']) / optimum
                bb_runtimes.append(bb_result['runtime_sec'])
                bb_nodes.append(bb_result['nodes_expanded'])
                bb_gaps.append(bb_gap)
                if bb_result['best_value'] == optimum and bb_result['optimality_proven']:
                    bb_success += 1

                instance_ga_values = []
                histories = []
                for ga_run in range(ga_runs_per_instance):
                    ga_seed = seed * 100 + ga_run
                    ga_result = genetic_algorithm(instance, seed=ga_seed)
                    gap = 100.0 * (optimum - ga_result['best_value']) / optimum
                    ga_runtimes.append(ga_result['runtime_sec'])
                    ga_gaps.append(gap)
                    ga_values_all.append(ga_result['best_value'])
                    instance_ga_values.append(ga_result['best_value'])
                    histories.append(ga_result['history'])
                    if ga_result['best_value'] == optimum:
                        ga_success += 1

                avg_history = [statistics.mean(step_values) for step_values in zip(*histories)]
                if n == 200 and kind == 'strongly_correlated' and instance_id == 0:
                    convergence_records = avg_history

                detailed_rows.append({
                    'kind': kind,
                    'n': n,
                    'instance_id': instance_id,
                    'optimum': optimum,
                    'bb_best_value': bb_result['best_value'],
                    'bb_runtime_sec': round(bb_result['runtime_sec'], 6),
                    'bb_nodes_expanded': bb_result['nodes_expanded'],
                    'bb_gap_pct': round(bb_gap, 4),
                    'bb_optimality_proven': bb_result['optimality_proven'],
                    'ga_mean_value': round(statistics.mean(instance_ga_values), 4),
                    'ga_best_value': max(instance_ga_values),
                    'ga_mean_gap_pct': round(100.0 * (optimum - statistics.mean(instance_ga_values)) / optimum, 4),
                    'ga_best_gap_pct': round(100.0 * (optimum - max(instance_ga_values)) / optimum, 4),
                })

            bb_runtime_mean, bb_runtime_std = summarise(bb_runtimes)
            bb_gap_mean, bb_gap_std = summarise(bb_gaps)
            bb_nodes_mean, bb_nodes_std = summarise(bb_nodes)
            ga_runtime_mean, ga_runtime_std = summarise(ga_runtimes)
            ga_gap_mean, ga_gap_std = summarise(ga_gaps)

            summary_rows.append({
                'kind': kind,
                'n': n,
                'instances': instances_per_setting,
                'ga_runs_total': instances_per_setting * ga_runs_per_instance,
                'optimum_mean': round(statistics.mean(optimum_values), 2),
                'bb_runtime_mean_sec': round(bb_runtime_mean, 4),
                'bb_runtime_std_sec': round(bb_runtime_std, 4),
                'bb_nodes_mean': round(bb_nodes_mean, 2),
                'bb_nodes_std': round(bb_nodes_std, 2),
                'bb_gap_mean_pct': round(bb_gap_mean, 4),
                'bb_gap_std_pct': round(bb_gap_std, 4),
                'bb_exact_success_rate_pct': round(100.0 * bb_success / instances_per_setting, 2),
                'ga_runtime_mean_sec': round(ga_runtime_mean, 4),
                'ga_runtime_std_sec': round(ga_runtime_std, 4),
                'ga_gap_mean_pct': round(ga_gap_mean, 4),
                'ga_gap_std_pct': round(ga_gap_std, 4),
                'ga_hit_optimum_rate_pct': round(100.0 * ga_success / (instances_per_setting * ga_runs_per_instance), 2),
                'ga_mean_value': round(statistics.mean(ga_values_all), 2),
            })

    summary_path = OUTPUT_DIR / 'knapsack_summary.csv'
    detailed_path = OUTPUT_DIR / 'knapsack_detailed.csv'

    with summary_path.open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(summary_rows[0].keys()))
        writer.writeheader()
        writer.writerows(summary_rows)

    with detailed_path.open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(detailed_rows[0].keys()))
        writer.writeheader()
        writer.writerows(detailed_rows)

    plot_summary(summary_rows)
    if convergence_records:
        plot_convergence(convergence_records)

    return summary_rows, detailed_rows


def plot_summary(summary_rows):
    kinds = ['uncorrelated', 'strongly_correlated']
    fig, axes = plt.subplots(2, 2, figsize=(12, 9))

    for idx, kind in enumerate(kinds):
        rows = [r for r in summary_rows if r['kind'] == kind]
        sizes = [r['n'] for r in rows]
        bb_runtime = [r['bb_runtime_mean_sec'] for r in rows]
        ga_runtime = [r['ga_runtime_mean_sec'] for r in rows]
        bb_gap = [r['bb_gap_mean_pct'] for r in rows]
        ga_gap = [r['ga_gap_mean_pct'] for r in rows]

        ax1 = axes[idx][0]
        ax1.plot(sizes, bb_runtime, marker='o', label='Branch and Bound')
        ax1.plot(sizes, ga_runtime, marker='s', label='Genetic Algorithm')
        ax1.set_title(f'Runtime on {kind.replace("_", " ")} instances')
        ax1.set_xlabel('Number of items')
        ax1.set_ylabel('Mean runtime (sec)')
        ax1.grid(True, alpha=0.3)
        ax1.legend()

        ax2 = axes[idx][1]
        ax2.plot(sizes, bb_gap, marker='o', label='Branch and Bound')
        ax2.plot(sizes, ga_gap, marker='s', label='Genetic Algorithm')
        ax2.set_title(f'Optimality gap on {kind.replace("_", " ")} instances')
        ax2.set_xlabel('Number of items')
        ax2.set_ylabel('Mean optimality gap (%)')
        ax2.grid(True, alpha=0.3)
        ax2.legend()

    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / 'knapsack_performance.png', dpi=200)
    plt.close(fig)


def plot_convergence(avg_history):
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.plot(range(len(avg_history)), avg_history, color='tab:purple')
    ax.set_title('Average GA convergence on a hard 200-item correlated instance')
    ax.set_xlabel('Generation')
    ax.set_ylabel('Best-so-far objective value')
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / 'ga_convergence.png', dpi=200)
    plt.close(fig)


if __name__ == '__main__':
    summary_rows, detailed_rows = run_experiments()
    print('Summary rows:')
    for row in summary_rows:
        print(row)
    print(f'Wrote {len(summary_rows)} summary rows and {len(detailed_rows)} detailed rows.')
