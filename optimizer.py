"""
进化优化器主类
功能：整合LLM、种群管理、提示词模板，实现完整的进化优化流程
"""
import warnings
warnings.filterwarnings('ignore')
from rdkit import RDLogger
RDLogger.DisableLog('rdApp.*')
import time
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
from datetime import datetime
import os
import warnings
warnings.filterwarnings('ignore')

from molecule_utils import MoleculeUtils, PropertyPredictor
from llm_client import LLMClient
from prompt_templates import PromptTemplates
from population import Population, Individual


class LLMEvolutionaryOptimizer:
    """LLM驱动的进化优化器"""

    def __init__(self,
                 property_name: str = 'qed',
                 population_size: int = 20,
                 llm_model: str = 'qwen2.5:7b',
                 prompt_strategy: str = 'basic',
                 selection_method: str = 'tournament',
                 temperature: float = 0.8,
                 children_per_parent: int = 3,
                 survival_rate: float = 0.3,
                 max_generations: int = 20,
                 output_dir: str = './results'):

        self.property_name = property_name.lower()
        self.population_size = population_size
        self.children_per_parent = children_per_parent
        self.survival_rate = survival_rate
        self.max_generations = max_generations

        self.mol_utils = MoleculeUtils()
        self.predictor = PropertyPredictor()

        print(f"正在初始化LLM客户端，模型: {llm_model}")
        self.llm_client = LLMClient(model_name=llm_model, temperature=temperature)

        self.population = Population(population_size=population_size, property_names=[self.property_name])

        self.prompt_strategy = prompt_strategy
        self.selection_method = selection_method
        self.example_library = []

        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

        # 初始化统计字典
        self.stats = {
            'generation': [],
            'best_fitness': [],
            'avg_fitness': [],
            'std_fitness': [],
            f'best_{self.property_name}': [],
            f'avg_{self.property_name}': [],
            'diversity': [],
            'population_size': [],
            'llm_calls': []
        }

    def initialize_population(self, smiles_pool: List[str]):
        """初始化种群"""
        print(f"初始化种群，规模: {self.population_size}")
        valid_smiles = self.mol_utils.filter_valid_smiles(smiles_pool)
        print(f"有效SMILES数量: {len(valid_smiles)}/{len(smiles_pool)}")

        count = self.population.initialize_from_smiles(valid_smiles)
        print(f"初始化了 {count} 个个体")

        self._record_stats()
        best = self.population.get_best(1)[0]
        print(f"初始最佳适应度: {best.fitness:.4f}")

    def _build_prompt(self, parent: Individual) -> str:
        """根据策略构建提示词"""
        current_score = parent.properties.get(self.property_name, 0)

        if self.prompt_strategy == 'basic':
            return PromptTemplates.basic_optimization(parent.smiles, self.property_name.upper(), current_score)
        elif self.prompt_strategy == 'examples':
            return PromptTemplates.with_examples(parent.smiles, self.property_name.upper(), current_score)
        elif self.prompt_strategy == 'diversity':
            recent = [ind.smiles for ind in self.population.individuals[:5]]
            return PromptTemplates.diversity_encouraging(parent.smiles, self.property_name.upper(), current_score, recent)
        else:
            return PromptTemplates.basic_optimization(parent.smiles, self.property_name.upper(), current_score)

    def _create_individual(self, smiles: str, parent: Individual = None) -> Optional[Individual]:
        """创建新个体"""
        std_smiles = self.mol_utils.standardize_smiles(smiles)
        if not std_smiles:
            return None

        prop_value = self.predictor.predict(std_smiles, self.property_name)
        if prop_value < 0:
            return None

        properties = {self.property_name: prop_value}
        ind = Individual(std_smiles, properties)
        ind.generation = self.population.generation + 1
        if parent:
            ind.parents = [parent.smiles]
        return ind

    def _generate_offspring(self, parents: List[Individual]) -> List[Individual]:
        """生成子代"""
        offspring = []

        for parent in parents:
            prompt = self._build_prompt(parent)
            generated = self.llm_client.generate(prompt, n=self.children_per_parent)

            for smiles in generated:
                ind = self._create_individual(smiles, parent)
                if ind:
                    offspring.append(ind)
                    if ind.properties.get(self.property_name, 0) > parent.properties.get(self.property_name, 0):
                        self.example_library.append({
                            'input': parent.smiles,
                            'output': ind.smiles,
                            'improvement': f'{self.property_name}: {parent.properties[self.property_name]:.3f} → {ind.properties[self.property_name]:.3f}'
                        })
            time.sleep(0.5)

        # 去重
        unique_offspring = []
        seen_smiles = set()
        for ind in offspring:
            if ind.smiles not in seen_smiles:
                seen_smiles.add(ind.smiles)
                unique_offspring.append(ind)

        print(f"  生成 {len(unique_offspring)}/{len(offspring)} 个有效子代")
        return unique_offspring

    def run_one_generation(self) -> Dict:
        """运行一代进化"""
        num_parents = max(1, int(self.population_size * self.survival_rate))
        parents = self.population.select_parents(method=self.selection_method, k=num_parents)

        print(f"第{self.population.generation + 1}代: 选择{len(parents)}个父代")

        offspring = self._generate_offspring(parents)

        if not offspring:
            print("  警告：没有生成有效子代")
            self.population.generation += 1
            return self._record_stats()

        self.population.update(offspring, strategy='steady_state')
        return self._record_stats()

    def _record_stats(self) -> Dict:
        """记录当前统计信息"""
        if not self.population.individuals:
            return {}

        fitnesses = [ind.fitness for ind in self.population.individuals]
        prop_values = [ind.properties.get(self.property_name, 0) for ind in self.population.individuals]

        self.stats['generation'].append(self.population.generation)
        self.stats['best_fitness'].append(max(fitnesses))
        self.stats['avg_fitness'].append(np.mean(fitnesses))
        self.stats['std_fitness'].append(np.std(fitnesses))
        self.stats[f'best_{self.property_name}'].append(max(prop_values))
        self.stats[f'avg_{self.property_name}'].append(np.mean(prop_values))
        self.stats['diversity'].append(self.population.get_diversity())
        self.stats['population_size'].append(len(self.population.individuals))
        self.stats['llm_calls'].append(len(self.stats['generation']))

        return {
            'generation': self.population.generation,
            'best_fitness': max(fitnesses),
            'avg_fitness': np.mean(fitnesses),
            'diversity': self.population.get_diversity()
        }

    def run(self) -> pd.DataFrame:
        """运行完整进化过程"""
        print(f"\n开始进化优化，目标属性: {self.property_name}")
        print(f"种群规模: {self.population_size}, 最大代数: {self.max_generations}")
        print(f"提示策略: {self.prompt_strategy}, 选择方法: {self.selection_method}")
        print("-" * 50)

        for gen in range(self.max_generations):
            self.run_one_generation()
            if (gen + 1) % 5 == 0 or gen == 0:
                best = self.population.get_best(1)[0]
                print(f"  第{gen+1}代最佳: {self.property_name}={best.properties.get(self.property_name, 0):.4f}, 适应度={best.fitness:.4f}")

        self.save_results()
        return pd.DataFrame(self.stats)

    def save_results(self):
        """保存结果"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        pop_file = os.path.join(self.output_dir, f"population_{timestamp}.csv")
        self.population.save(pop_file)

        stats_file = os.path.join(self.output_dir, f"stats_{timestamp}.csv")
        pd.DataFrame(self.stats).to_csv(stats_file, index=False)

        print(f"\n结果已保存至: {self.output_dir}")

    def get_best_molecules(self, n: int = 5) -> List[Dict]:
        """获取最优分子"""
        best = self.population.get_best(n)
        return [{'smiles': ind.smiles, 'fitness': ind.fitness, self.property_name: ind.properties.get(self.property_name, 0)} for ind in best]


# 测试代码
if __name__ == "__main__":
    print("=" * 50)
    print("测试 Optimizer 模块")
    print("=" * 50)

    # 准备测试数据
    test_smiles = [
        "CC(=O)Oc1ccccc1C(=O)O",  # 阿司匹林
        "CN1C=NC2=C1C(=O)N(C(=O)N2C)C",  # 咖啡因
        "CC(C)CC1=CC=C(C=C1)C(C)C(=O)O",  # 布洛芬
    ]

    # 创建优化器（小规模测试）
    optimizer = LLMEvolutionaryOptimizer(
        property_name='qed',
        population_size=10,
        llm_model='qwen2.5:7b',
        prompt_strategy='diversity',
        max_generations=3,
        children_per_parent=3,
        output_dir='./results_diversity'
    )

    # 初始化种群
    optimizer.initialize_population(test_smiles * 10)

    # 运行优化
    print("\n开始运行...")
    df = optimizer.run()

    # 显示结果
    print("\n" + "=" * 50)
    print("优化完成！最佳分子：")
    best = optimizer.get_best_molecules(3)
    for i, mol in enumerate(best, 1):
        print(f"{i}. SMILES: {mol['smiles'][:50]}...")
        print(f"   QED: {mol['qed']:.4f}")

    print("\n✅ Optimizer 模块测试完成！")