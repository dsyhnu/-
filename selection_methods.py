"""
选择方法演示模块
功能：实现多种选择方法，用于对比实验
"""

import random
import numpy as np
from typing import List, Any


class SelectionMethods:
    """选择方法集合类"""

    @staticmethod
    def tournament_selection(population: List[Any],
                             fitnesses: List[float],
                             k: int,
                             tournament_size: int = 3) -> List[Any]:
        """
        锦标赛选择

        原理：随机抽取 tournament_size 个个体，选择适应度最高的

        Args:
            population: 种群个体列表
            fitnesses: 对应的适应度列表
            k: 需要选择的数量
            tournament_size: 锦标赛规模

        Returns:
            选中的个体列表
        """
        selected = []
        n = len(population)

        for _ in range(k):
            # 随机选择 tournament_size 个索引
            indices = random.sample(range(n), min(tournament_size, n))
            # 找出适应度最高的索引
            best_idx = max(indices, key=lambda i: fitnesses[i])
            selected.append(population[best_idx])

        return selected

    @staticmethod
    def roulette_selection(population: List[Any],
                           fitnesses: List[float],
                           k: int) -> List[Any]:
        """
        轮盘赌选择（适应度比例选择）

        原理：每个个体被选中的概率 = 个体适应度 / 总适应度

        Args:
            population: 种群个体列表
            fitnesses: 对应的适应度列表
            k: 需要选择的数量

        Returns:
            选中的个体列表
        """
        if not population:
            return []

        total_fitness = sum(fitnesses)

        # 如果总适应度为0，随机选择
        if total_fitness == 0:
            return random.sample(population, min(k, len(population)))

        # 计算每个个体的选择概率
        probabilities = [f / total_fitness for f in fitnesses]

        # 根据概率选择k个个体（有放回）
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
        """
        Top-K选择（精英选择）

        原理：直接选择适应度最高的k个个体

        Args:
            population: 种群个体列表
            fitnesses: 对应的适应度列表
            k: 需要选择的数量

        Returns:
            选中的个体列表
        """
        # 按适应度降序排序
        paired = sorted(zip(population, fitnesses), key=lambda x: x[1], reverse=True)
        selected = [p for p, _ in paired[:min(k, len(paired))]]
        return selected

    @staticmethod
    def rank_selection(population: List[Any],
                       fitnesses: List[float],
                       k: int) -> List[Any]:
        """
        排名选择

        原理：按适应度排名分配选择概率，避免适应度差异过大

        Args:
            population: 种群个体列表
            fitnesses: 对应的适应度列表
            k: 需要选择的数量

        Returns:
            选中的个体列表
        """
        if not population:
            return []

        # 按适应度排序，获得排名
        sorted_indices = sorted(range(len(fitnesses)), key=lambda i: fitnesses[i], reverse=True)

        n = len(population)
        # 按排名分配概率（排名越高，概率越大）
        ranks = list(range(n, 0, -1))  # 排名：n, n-1, ..., 1
        total_rank = sum(ranks)
        probabilities = [rank / total_rank for rank in ranks]

        # 根据排名概率选择
        selected_positions = np.random.choice(n, size=k, replace=True, p=probabilities)
        selected = [population[sorted_indices[pos]] for pos in selected_positions]

        return selected

    @staticmethod
    def random_selection(population: List[Any],
                         fitnesses: List[float],
                         k: int) -> List[Any]:
        """
        随机选择

        原理：完全随机选择，不考虑适应度

        Args:
            population: 种群个体列表
            fitnesses: 对应的适应度列表（此处不使用）
            k: 需要选择的数量

        Returns:
            选中的个体列表
        """
        return random.sample(population, min(k, len(population)))

    @staticmethod
    def boltzmann_selection(population: List[Any],
                            fitnesses: List[float],
                            k: int,
                            temperature: float = 1.0) -> List[Any]:
        """
        玻尔兹曼选择

        原理：使用玻尔兹曼分布，温度越高选择越随机，温度越低越偏向精英

        Args:
            population: 种群个体列表
            fitnesses: 对应的适应度列表
            k: 需要选择的数量
            temperature: 温度参数（越高越随机）

        Returns:
            选中的个体列表
        """
        if not population:
            return []

        # 计算玻尔兹曼概率
        # P(i) = exp(fitness_i / T) / sum(exp(fitness_j / T))
        exp_fitness = np.exp(np.array(fitnesses) / max(temperature, 0.01))
        probabilities = exp_fitness / np.sum(exp_fitness)

        selected_indices = np.random.choice(
            len(population),
            size=k,
            replace=True,
            p=probabilities
        )

        return [population[i] for i in selected_indices]


# 测试代码
if __name__ == "__main__":
    print("=" * 60)
    print("选择方法演示")
    print("=" * 60)


    # 创建示例种群
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

    print(f"\n种群: {population}")
    print(f"适应度: {fitnesses}")

    k = 3  # 选择3个个体

    # 测试各种选择方法
    methods = [
        ("锦标赛选择", SelectionMethods.tournament_selection, {"tournament_size": 3}),
        ("轮盘赌选择", SelectionMethods.roulette_selection, {}),
        ("Top-K选择", SelectionMethods.topk_selection, {}),
        ("排名选择", SelectionMethods.rank_selection, {}),
        ("随机选择", SelectionMethods.random_selection, {}),
        ("玻尔兹曼选择", SelectionMethods.boltzmann_selection, {"temperature": 0.5}),
    ]

    print("\n" + "-" * 60)
    for name, method, kwargs in methods:
        selected = method(population, fitnesses, k, **kwargs)
        print(f"{name}: {selected}")

    # 轮盘赌选择的概率分布演示
    print("\n" + "=" * 60)
    print("轮盘赌选择概率分布")
    print("=" * 60)
    probs = [f / sum(fitnesses) for f in fitnesses]
    for ind, prob in zip(population, probs):
        print(f"  {ind.name}: 适应度={ind.fitness:.2f}, 概率={prob:.2%}")

    print("\n✅ 选择方法演示完成！")