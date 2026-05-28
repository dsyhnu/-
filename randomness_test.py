"""
随机性验证模块
功能：演示各种选择方法的随机性，并测试真实进化数据中的随机性
"""

import random
import numpy as np
import pandas as pd
import os
from glob import glob
from typing import List, Any


class SelectionMethods:
    """选择方法集合类"""

    @staticmethod
    def tournament_selection(population: List[Any],
                             fitnesses: List[float],
                             k: int,
                             tournament_size: int = 3) -> List[Any]:
        """锦标赛选择"""
        selected = []
        n = len(population)

        for _ in range(k):
            indices = random.sample(range(n), min(tournament_size, n))
            best_idx = max(indices, key=lambda i: fitnesses[i])
            selected.append(population[best_idx])

        return selected

    @staticmethod
    def roulette_selection(population: List[Any],
                           fitnesses: List[float],
                           k: int) -> List[Any]:
        """轮盘赌选择"""
        if not population:
            return []

        total_fitness = sum(fitnesses)

        if total_fitness == 0:
            return random.sample(population, min(k, len(population)))

        probabilities = [f / total_fitness for f in fitnesses]

        selected_indices = np.random.choice(
            len(population),
            size=k,
            replace=True,
            p=probabilities
        )

        return [population[i] for i in selected_indices]

    @staticmethod
    def topk_selection(population: List[Any],
                       fitnesses: List[float],
                       k: int) -> List[Any]:
        """Top-K选择（确定性，无随机性）"""
        paired = sorted(zip(population, fitnesses), key=lambda x: x[1], reverse=True)
        return [p for p, _ in paired[:min(k, len(paired))]]

    @staticmethod
    def rank_selection(population: List[Any],
                       fitnesses: List[float],
                       k: int) -> List[Any]:
        """排名选择"""
        if not population:
            return []

        sorted_indices = sorted(range(len(fitnesses)), key=lambda i: fitnesses[i], reverse=True)

        n = len(population)
        ranks = list(range(n, 0, -1))
        total_rank = sum(ranks)
        probabilities = [rank / total_rank for rank in ranks]

        selected_positions = np.random.choice(n, size=k, replace=True, p=probabilities)
        selected = [population[sorted_indices[pos]] for pos in selected_positions]

        return selected

    @staticmethod
    def random_selection(population: List[Any],
                         fitnesses: List[float],
                         k: int) -> List[Any]:
        """随机选择"""
        return random.sample(population, min(k, len(population)))


def demo_randomness():
    """演示选择方法的随机性"""
    print("=" * 70)
    print("演示1：使用固定种群，多次运行观察随机性")
    print("=" * 70)

    # 创建测试个体
    class MockIndividual:
        def __init__(self, name, fitness):
            self.name = name
            self.fitness = fitness

        def __repr__(self):
            return f"{self.name}({self.fitness:.2f})"

    population = [
        MockIndividual("A", 0.95),
        MockIndividual("B", 0.85),
        MockIndividual("C", 0.75),
        MockIndividual("D", 0.65),
        MockIndividual("E", 0.55),
        MockIndividual("F", 0.45),
    ]
    fitnesses = [ind.fitness for ind in population]

    print(f"\n固定种群: {population}")
    print(f"适应度: {fitnesses}\n")

    # 多次运行轮盘赌选择，观察随机性
    print("-" * 70)
    print("轮盘赌选择（随机性测试 - 运行10次）")
    print("-" * 70)
    for run in range(10):
        selected = SelectionMethods.roulette_selection(population, fitnesses, k=3)
        names = [ind.name for ind in selected]
        print(f"第{run + 1:2d}次: {names}")

    # 多次运行锦标赛选择，观察随机性
    print("\n" + "-" * 70)
    print("锦标赛选择（随机性测试 - 运行10次，tournament_size=2）")
    print("-" * 70)
    for run in range(10):
        selected = SelectionMethods.tournament_selection(population, fitnesses, k=3, tournament_size=2)
        names = [ind.name for ind in selected]
        print(f"第{run + 1:2d}次: {names}")

    # 对比确定性方法
    print("\n" + "-" * 70)
    print("Top-K选择（确定性方法 - 每次结果相同）")
    print("-" * 70)
    for run in range(3):
        selected = SelectionMethods.topk_selection(population, fitnesses, k=3)
        names = [ind.name for ind in selected]
        print(f"第{run + 1}次: {names}")


def load_real_population():
    """从真实实验结果中加载种群数据"""
    # 查找最新的实验结果文件夹
    result_folders = ['results_basic', 'results_examples', 'results_diversity']
    latest_stats = None

    for folder in result_folders:
        if os.path.exists(folder):
            stats_files = glob(os.path.join(folder, "stats_*.csv"))
            if stats_files:
                latest_file = max(stats_files, key=os.path.getctime)
                df = pd.read_csv(latest_file)
                if latest_stats is None or df['generation'].max() > latest_stats['generation'].max():
                    latest_stats = df

    if latest_stats is None:
        print("未找到真实实验数据，使用模拟数据")
        return None, None

    return latest_stats, latest_stats['best_qed'].values.tolist()


def demo_real_data():
    """使用真实进化数据演示随机性"""
    print("\n" + "=" * 70)
    print("演示2：使用真实进化数据（从实验结果读取）")
    print("=" * 70)

    # 读取真实数据
    result_folders = ['results_basic', 'results_examples', 'results_diversity']

    for folder in result_folders:
        if os.path.exists(folder):
            stats_files = glob(os.path.join(folder, "stats_*.csv"))
            if stats_files:
                latest_file = max(stats_files, key=os.path.getctime)
                df = pd.read_csv(latest_file)

                print(f"\n文件夹: {folder}")
                print(f"文件: {os.path.basename(latest_file)}")
                print(f"代数范围: 0-{df['generation'].max()}")
                print(f"最佳QED范围: {df['best_qed'].min():.4f} - {df['best_qed'].max():.4f}")

                # 使用最后一代的适应度作为种群
                # 注意：这里简化演示，实际种群有多个个体
                fitnesses = df['best_qed'].values.tolist()
                population = [f"Gen{int(gen)}" for gen in df['generation']]

                print(f"\n  轮盘赌选择（从各代最佳中选3个）:")
                for run in range(5):
                    selected = SelectionMethods.roulette_selection(population, fitnesses, k=3)
                    print(f"    第{run + 1}次: {selected}")

                print(f"\n  锦标赛选择（从各代最佳中选3个）:")
                for run in range(5):
                    selected = SelectionMethods.tournament_selection(population, fitnesses, k=3, tournament_size=2)
                    print(f"    第{run + 1}次: {selected}")

                break  # 只演示第一个找到的


def demo_probability_distribution():
    """演示概率分布"""
    print("\n" + "=" * 70)
    print("演示3：轮盘赌选择的概率分布")
    print("=" * 70)

    # 创建测试个体
    class MockIndividual:
        def __init__(self, name, fitness):
            self.name = name
            self.fitness = fitness

    population = [
        MockIndividual("A", 0.95),
        MockIndividual("B", 0.85),
        MockIndividual("C", 0.75),
        MockIndividual("D", 0.65),
        MockIndividual("E", 0.55),
        MockIndividual("F", 0.45),
    ]
    fitnesses = [ind.fitness for ind in population]
    total = sum(fitnesses)

    print("\n个体适应度与选中概率：")
    print("-" * 50)
    for ind, f in zip(population, fitnesses):
        prob = f / total * 100
        bar = "█" * int(prob * 2)
        print(f"  {ind.name}: 适应度={f:.2f}, 概率={prob:.2f}% {bar}")

    # 模拟1000次选择，统计实际频率
    print("\n模拟1000次选择（轮盘赌）的实际频率：")
    print("-" * 50)

    counts = {ind.name: 0 for ind in population}
    for _ in range(1000):
        selected = SelectionMethods.roulette_selection(population, fitnesses, k=1)
        counts[selected[0].name] += 1

    for ind in population:
        theoretical = (ind.fitness / total) * 100
        actual = counts[ind.name] / 10
        print(f"  {ind.name}: 理论={theoretical:.2f}%, 实际={actual:.2f}%")


def demo_seed_control():
    """演示随机种子控制"""
    print("\n" + "=" * 70)
    print("演示4：随机种子控制（可复现 vs 不可复现）")
    print("=" * 70)

    class MockIndividual:
        def __init__(self, name, fitness):
            self.name = name
            self.fitness = fitness

    population = [
        MockIndividual("A", 0.95),
        MockIndividual("B", 0.85),
        MockIndividual("C", 0.75),
        MockIndividual("D", 0.65),
        MockIndividual("E", 0.55),
        MockIndividual("F", 0.45),
    ]
    fitnesses = [ind.fitness for ind in population]

    print("\n设置随机种子=42（结果可复现）")
    print("-" * 50)

    np.random.seed(42)
    random.seed(42)
    result1 = SelectionMethods.roulette_selection(population, fitnesses, k=3)
    names1 = [ind.name for ind in result1]
    print(f"第1次运行: {names1}")

    np.random.seed(42)
    random.seed(42)
    result2 = SelectionMethods.roulette_selection(population, fitnesses, k=3)
    names2 = [ind.name for ind in result2]
    print(f"第2次运行: {names2}")
    print(f"两次结果相同: {names1 == names2}")

    print("\n不设置随机种子（结果不可复现）")
    print("-" * 50)
    result3 = SelectionMethods.roulette_selection(population, fitnesses, k=3)
    names3 = [ind.name for ind in result3]
    print(f"第1次运行: {names3}")

    result4 = SelectionMethods.roulette_selection(population, fitnesses, k=3)
    names4 = [ind.name for ind in result4]
    print(f"第2次运行: {names4}")
    print(f"两次结果相同: {names3 == names4}")


if __name__ == "__main__":
    print("=" * 70)
    print("随机性验证测试")
    print("=" * 70)

    # 演示1：固定种群的随机性
    demo_randomness()

    # 演示2：真实数据的随机性
    demo_real_data()

    # 演示3：概率分布
    demo_probability_distribution()

    # 演示4：随机种子控制
    demo_seed_control()

    print("\n" + "=" * 70)
    print("✅ 随机性验证完成！")
    print("=" * 70)