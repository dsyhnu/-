"""
提示词模板模块
功能：设计不同的提示策略，引导LLM生成具有改进属性的分子
"""

from typing import List, Dict, Any


class PromptTemplates:
    """提示词模板集合"""

    @staticmethod
    def basic_optimization(smiles: str,
                           property_name: str,
                           current_score: float) -> str:
        """
        基础优化提示模板

        Args:
            smiles: 当前分子SMILES
            property_name: 属性名称（如 QED, DRD2）
            current_score: 当前分数

        Returns:
            提示词字符串
        """
        return f"""你是一个专业的药物化学家，擅长设计具有特定性质的药物分子。

任务：优化分子的{property_name}分数，使其更高。
当前分子SMILES：{smiles}
当前{property_name}分数：{current_score:.3f}

要求：
1. 生成的分子必须是化学上有效的SMILES格式
2. 保持分子的核心骨架
3. 通过修改官能团或侧链来优化{property_name}
4. 每行输出一个SMILES，不要有其他解释

请生成3个改进后的分子SMILES："""

    @staticmethod
    def with_examples(smiles: str,
                      property_name: str,
                      current_score: float) -> str:
        """
        带示例的优化提示（Few-shot Learning）

        Args:
            smiles: 当前分子SMILES
            property_name: 属性名称
            current_score: 当前分数

        Returns:
            提示词字符串
        """
        return f"""你是一个专业的药物化学家，擅长设计具有特定性质的药物分子。

参考以下成功优化的例子：

例子1：
  输入：CC(=O)Oc1ccccc1C(=O)O (QED=0.55)
  输出：CC(=O)Oc1ccc(Cl)cc1C(=O)O (QED=0.78)
  改进策略：在苯环上添加氯原子，增加亲脂性

例子2：
  输入：CN1C=NC2=C1C(=O)N(C(=O)N2C)C (QED=0.62)
  输出：CN1C=NC2=C1C(=O)N(C(=O)N2CC)C (QED=0.71)
  改进策略：将甲基替换为乙基，改善分子性质

现在，请优化以下分子：
输入：{smiles}
当前{property_name}分数：{current_score:.3f}

要求：
1. 生成的分子必须化学有效
2. 参考上面的优化策略
3. 每行输出一个SMILES

请生成3个改进后的分子SMILES："""

    @staticmethod
    def diversity_encouraging(smiles: str,
                              property_name: str,
                              current_score: float,
                              recent_smiles: List[str] = None) -> str:
        """
        鼓励多样性的优化提示

        Args:
            smiles: 当前分子SMILES
            property_name: 属性名称
            current_score: 当前分数
            recent_smiles: 最近生成的分子列表，避免重复

        Returns:
            提示词字符串
        """
        recent_text = ""
        if recent_smiles:
            recent_text = "\n".join([f"  - {s}" for s in recent_smiles[:5]])
            recent_text = f"\n\n近期已生成的分子（请避免重复）：\n{recent_text}"

        return f"""你是一个专业的药物化学家，擅长探索新的化学空间。

任务：优化分子的{property_name}分数，使其更高。
当前分子SMILES：{smiles}
当前{property_name}分数：{current_score:.3f}
{recent_text}

要求：
1. 生成的分子必须化学有效
2. 尝试与近期分子不同的化学结构
3. 探索新的官能团和骨架
4. 每行输出一个SMILES

请生成3个新颖的改进分子SMILES："""

    @staticmethod
    def multi_objective(smiles: str,
                        objectives: List[Dict[str, Any]]) -> str:
        """
        多目标优化提示

        Args:
            smiles: 当前分子SMILES
            objectives: 目标列表，每个包含 name, current, direction

        Returns:
            提示词字符串
        """
        obj_desc = []
        for obj in objectives:
            direction = "提高" if obj.get('direction', 'higher') == 'higher' else "降低"
            obj_desc.append(f"  - {obj['name']}: {direction}（当前值: {obj['current']:.3f}）")

        obj_text = "\n".join(obj_desc)

        return f"""你是一个专业的药物化学家，擅长平衡多重药物性质。

任务：优化分子，同时满足以下多个目标：
{obj_text}

当前分子SMILES：{smiles}

要求：
1. 生成的分子必须化学有效
2. 尽可能同时改善多个性质
3. 如果难以兼顾，优先保证最重要的性质
4. 每行输出一个SMILES

请生成3个多目标优化的分子SMILES："""


# 测试代码
if __name__ == "__main__":
    print("=" * 50)
    print("测试 PromptTemplates 模块")
    print("=" * 50)

    # 测试分子
    test_smiles = "CC(=O)Oc1ccccc1C(=O)O"

    # 测试基础模板
    print("\n1. 基础优化模板：")
    print("-" * 40)
    prompt1 = PromptTemplates.basic_optimization(test_smiles, "QED", 0.55)
    print(prompt1[:200] + "...\n")

    # 测试带示例模板
    print("2. 带示例模板：")
    print("-" * 40)
    prompt2 = PromptTemplates.with_examples(test_smiles, "QED", 0.55)
    print(prompt2[:200] + "...\n")

    # 测试多样性模板
    print("3. 多样性鼓励模板：")
    print("-" * 40)
    recent = ["CC(=O)Oc1ccc(Cl)cc1C(=O)O", "CC(=O)Oc1ccccc1C(=O)N"]
    prompt3 = PromptTemplates.diversity_encouraging(test_smiles, "QED", 0.55, recent)
    print(prompt3[:200] + "...\n")

    # 测试多目标模板
    print("4. 多目标优化模板：")
    print("-" * 40)
    objectives = [
        {'name': 'QED', 'current': 0.55, 'direction': 'higher'},
        {'name': 'LogP', 'current': 1.2, 'direction': 'lower'}
    ]
    prompt4 = PromptTemplates.multi_objective(test_smiles, objectives)
    print(prompt4[:200] + "...\n")

    print("✅ PromptTemplates 模块测试完成！")