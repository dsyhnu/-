"""
种群管理模块
功能：维护分子种群、选择操作、更新策略
"""

import random
import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional
from molecule_utils import MoleculeUtils, PropertyPredictor


class Individual:
    """个体类，代表一个分子"""

    def __init__(self, smiles: str, properties: Dict[str, float] = None):
        """
        初始化个体

        Args:
            smiles: 分子SMILES
            properties: 属性字典（如 {'qed': 0.55, 'drd2': 0.6}）
        """
        self.smiles = MoleculeUtils.standardize_smiles(smiles)
        self.properties = properties or {}
        self.fitness = 0.0  # 综合适应度
        self.generation = 0  # 所属世代
        self.parents = []  # 父代SMILES列表

    def calculate_fitness(self, weights: Dict[str, float] = None) -> float:
        """
        计算综合适应度（加权和）

        Args:
            weights: 各属性的权重，如 {'qed': 1.0, 'drd2': 0.5}

        Returns:
            适应度分数
        """
        if not self.properties:
            self.fitness = 0.0
            return 0.0

        if weights is None:
            # 默认等权重
            weights = {k: 1.0 for k in self.properties.keys()}

        fitness = 0.0
        total_weight = 0.0

        for prop, value in self.properties.items():
            if prop in weights and value >= 0:
                fitness += weights[prop] * value
                total_weight += weights[prop]

        self.fitness = fitness / total_weight if total_weight > 0 else 0.0
        return self.fitness

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'smiles': self.smiles,
            'fitness': self.fitness,
            'generation': self.generation,
            **self.properties
        }


class Population:
    """种群类"""

    def __init__(self,
                 population_size: int = 50,
                 property_names: List[str] = None,
                 weights: Dict[str, float] = None):
        """
        初始化种群

        Args:
            population_size: 种群规模
            property_names: 属性名称列表（如 ['qed', 'drd2']）
            weights: 各属性的权重
        """
        self.population_size = population_size
        self.property_names = property_names or ['qed']
        self.weights = weights
        self.individuals: List[Individual] = []  # 当前种群
        self.archive: List[Individual] = []  # 历史最优个体
        self.generation = 0
        self.history = []  # 历史记录

        # 初始化属性预测器
        self.predictor = PropertyPredictor()

    def initialize_from_smiles(self, smiles_list: List[str]) -> int:
        """
        从SMILES列表初始化种群

        Args:
            smiles_list: SMILES列表

        Returns:
            成功初始化的个体数
        """
        # 随机采样
        if len(smiles_list) > self.population_size:
            selected = random.sample(smiles_list, self.population_size)
        else:
            selected = smiles_list.copy()
            while len(selected) < self.population_size:
                selected.append(random.choice(smiles_list))

        # 创建个体并计算属性
        count = 0
        for smiles in selected:
            ind = Individual(smiles)

            # 计算各属性
            properties = {}
            for prop in self.property_names:
                prop_value = self.predictor.predict(smiles, prop)
                if prop_value >= 0:
                    properties[prop] = prop_value

            if properties:
                ind.properties = properties
                ind.generation = 0
                self.individuals.append(ind)
                count += 1

        # 计算适应度
        self._update_fitness()

        # 更新档案
        self._update_archive()

        return count

    def _update_fitness(self):
        """更新所有个体的适应度"""
        for ind in self.individuals:
            ind.calculate_fitness(self.weights)

    def _update_archive(self):
        """更新历史最优档案"""
        if not self.individuals:
            return

        best = max(self.individuals, key=lambda x: x.fitness)

        if not self.archive:
            self.archive.append(best)
        elif best.fitness > max(a.fitness for a in self.archive):
            self.archive.append(best)
            # 限制档案大小
            self.archive.sort(key=lambda x: x.fitness, reverse=True)
            self.archive = self.archive[:10]

    def select_parents(self, method: str = 'tournament',
                       k: int = 2, **kwargs) -> List[Individual]:
        """
        选择父代

        Args:
            method: 选择方法 ['tournament', 'roulette', 'topk']
            k: 选择数量

        Returns:
            选中的父代个体列表
        """
        if not self.individuals:
            return []

        if method == 'tournament':
            return self._tournament_selection(k, **kwargs)
        elif method == 'roulette':
            return self._roulette_selection(k)
        elif method == 'topk':
            return self._topk_selection(k)
        else:
            return random.sample(self.individuals, min(k, len(self.individuals)))

    def _tournament_selection(self, k: int, tournament_size: int = 3) -> List[Individual]:
        """锦标赛选择"""
        selected = []
        for _ in range(k):
            contestants = random.sample(self.individuals,
                                        min(tournament_size, len(self.individuals)))
            winner = max(contestants, key=lambda x: x.fitness)
            selected.append(winner)
        return selected

    def _roulette_selection(self, k: int) -> List[Individual]:
        """轮盘赌选择（适应度比例选择）"""
        fitness_sum = sum(ind.fitness for ind in self.individuals)
        if fitness_sum == 0:
            return random.sample(self.individuals, min(k, len(self.individuals)))

        probs = [ind.fitness / fitness_sum for ind in self.individuals]
        selected_indices = np.random.choice(
            len(self.individuals), size=k, replace=True, p=probs
        )
        return [self.individuals[i] for i in selected_indices]

    def _topk_selection(self, k: int) -> List[Individual]:
        """选择适应度最高的k个"""
        sorted_ind = sorted(self.individuals, key=lambda x: x.fitness, reverse=True)
        return sorted_ind[:min(k, len(sorted_ind))]

    def update(self, new_individuals: List[Individual],
               strategy: str = 'steady_state') -> int:
        """
        更新种群

        Args:
            new_individuals: 新个体列表
            strategy: 更新策略 ['steady_state', 'generational']

        Returns:
            更新的个体数
        """
        if not new_individuals:
            return 0

        # 计算新个体的适应度
        for ind in new_individuals:
            ind.calculate_fitness(self.weights)

        if strategy == 'steady_state':
            # 稳态更新：用新个体替换最差的
            self._steady_state_update(new_individuals)
        else:
            # 世代更新：保留最优，其余替换
            self._generational_update(new_individuals)

        self.generation += 1
        self._record_history()
        self._update_archive()

        return len(new_individuals)

    def _steady_state_update(self, new_individuals: List[Individual]):
        """稳态更新：用新个体替换最差的"""
        combined = self.individuals + new_individuals
        combined.sort(key=lambda x: x.fitness, reverse=True)
        self.individuals = combined[:self.population_size]

    def _generational_update(self, new_individuals: List[Individual]):
        """世代更新：完全替换，但保留最优"""
        # 找出当前最优
        best = max(self.individuals, key=lambda x: x.fitness)

        # 新个体按适应度排序
        new_individuals.sort(key=lambda x: x.fitness, reverse=True)

        # 组合：最优 + 最好的新个体
        combined = [best] + new_individuals
        self.individuals = combined[:self.population_size]

    def _record_history(self):
        """记录历史统计"""
        if not self.individuals:
            return

        fitnesses = [ind.fitness for ind in self.individuals]
        record = {
            'generation': self.generation,
            'best_fitness': max(fitnesses),
            'avg_fitness': np.mean(fitnesses),
            'std_fitness': np.std(fitnesses),
            'population_size': len(self.individuals)
        }

        # 记录各属性统计
        for prop in self.property_names:
            values = [ind.properties.get(prop, 0) for ind in self.individuals]
            record[f'best_{prop}'] = max(values) if values else 0
            record[f'avg_{prop}'] = np.mean(values) if values else 0

        self.history.append(record)

    def get_best(self, n: int = 1) -> List[Individual]:
        """获取最优的n个个体"""
        if not self.individuals:
            return []
        sorted_ind = sorted(self.individuals, key=lambda x: x.fitness, reverse=True)
        return sorted_ind[:n]

    def get_diversity(self) -> float:
        """计算种群多样性（基于不同SMILES的比例）"""
        if not self.individuals:
            return 0.0
        smiles_set = set(ind.smiles for ind in self.individuals)
        return len(smiles_set) / len(self.individuals)

    def to_dataframe(self) -> pd.DataFrame:
        """转换为DataFrame"""
        records = [ind.to_dict() for ind in self.individuals]
        return pd.DataFrame(records)

    def save(self, filepath: str):
        """保存种群到文件"""
        df = self.to_dataframe()
        df.to_csv(filepath, index=False)


# 测试代码
if __name__ == "__main__":
    print("=" * 50)
    print("测试 Population 模块")
    print("=" * 50)

    # 创建测试数据
    test_smiles = [
        "CC(=O)Oc1ccccc1C(=O)O",  # 阿司匹林
        "CN1C=NC2=C1C(=O)N(C(=O)N2C)C",  # 咖啡因
        "CC(C)CC1=CC=C(C=C1)C(C)C(=O)O",  # 布洛芬
        "CC(C)CCC(=O)NC1=CC=C(C=C1)S(=O)(=O)N",  # 另一种药物
    ]

    # 初始化种群
    pop = Population(population_size=10, property_names=['qed'])
    count = pop.initialize_from_smiles(test_smiles)
    print(f"初始化了 {count} 个个体")

    # 显示种群信息
    print(f"\n种群规模: {len(pop.individuals)}")
    print(f"种群多样性: {pop.get_diversity():.3f}")

    # 显示最优个体
    best = pop.get_best(1)[0]
    print(f"\n最优个体:")
    print(f"  SMILES: {best.smiles}")
    print(f"  QED: {best.properties.get('qed', 0):.3f}")
    print(f"  适应度: {best.fitness:.3f}")

    # 测试选择
    print(f"\n选择测试:")
    parents = pop.select_parents(method='tournament', k=3)
    print(f"选择了 {len(parents)} 个父代")

    # 测试更新
    print(f"\n更新测试:")
    # 创建新个体
    new_ind = Individual("CCO", properties={'qed': 0.8})
    new_ind.generation = pop.generation + 1
    updated = pop.update([new_ind], strategy='steady_state')
    print(f"更新了 {updated} 个个体")
    print(f"更新后种群规模: {len(pop.individuals)}")

    # 显示历史
    print(f"\n历史记录:")
    print(pop.history[-1] if pop.history else "无")

    print("\n✅ Population 模块测试完成！")