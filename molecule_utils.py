"""
分子处理工具模块
功能：SMILES验证、属性计算、相似度计算
"""

from rdkit import Chem
from rdkit.Chem import Descriptors, QED
from rdkit.Chem import AllChem
from rdkit.Chem import DataStructs
from typing import List, Optional


class MoleculeUtils:
    """分子处理工具类"""

    @staticmethod
    def validate_smiles(smiles: str) -> bool:
        """验证SMILES字符串是否有效"""
        if not isinstance(smiles, str):
            return False
        mol = Chem.MolFromSmiles(smiles)
        return mol is not None

    @staticmethod
    def standardize_smiles(smiles: str) -> Optional[str]:
        """标准化SMILES"""
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return None
        return Chem.MolToSmiles(mol, canonical=True)

    @staticmethod
    def calculate_qed(smiles: str) -> float:
        """计算QED（药物相似性）分数 [0, 1]"""
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return -1.0
        try:
            return QED.qed(mol)
        except:
            return -1.0

    @staticmethod
    def calculate_mol_weight(smiles: str) -> float:
        """计算分子量"""
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return -1.0
        return Descriptors.MolWt(mol)

    @staticmethod
    def calculate_logp(smiles: str) -> float:
        """计算LogP"""
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return -1.0
        return Descriptors.MolLogP(mol)

    @staticmethod
    def calculate_similarity(smiles1: str, smiles2: str) -> float:
        """计算两个分子的相似度"""
        mol1 = Chem.MolFromSmiles(smiles1)
        mol2 = Chem.MolFromSmiles(smiles2)

        if mol1 is None or mol2 is None:
            return 0.0

        fp1 = AllChem.GetMorganFingerprintAsBitVect(mol1, 2, nBits=1024)
        fp2 = AllChem.GetMorganFingerprintAsBitVect(mol2, 2, nBits=1024)

        return DataStructs.TanimotoSimilarity(fp1, fp2)

    @staticmethod
    def filter_valid_smiles(smiles_list: List[str]) -> List[str]:
        """过滤出有效的SMILES"""
        valid = []
        for s in smiles_list:
            if MoleculeUtils.validate_smiles(s):
                std = MoleculeUtils.standardize_smiles(s)
                if std:
                    valid.append(std)
        return valid


class PropertyPredictor:
    """分子属性预测器"""

    def __init__(self):
        pass

    def calculate_qed(self, smiles: str) -> float:
        """计算QED"""
        return MoleculeUtils.calculate_qed(smiles)

    def predict_drd2(self, smiles: str) -> float:
        """预测DRD2活性（启发式模拟）"""
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return 0.0

        # 计算芳香原子数量
        num_aromatic_atoms = sum(1 for atom in mol.GetAtoms() if atom.GetIsAromatic())
        num_nitrogen = sum(1 for atom in mol.GetAtoms() if atom.GetAtomicNum() == 7)

        # 归一化到0-1
        score = min(1.0, num_aromatic_atoms * 0.05 + num_nitrogen * 0.1)
        return score

    def predict_gsk3b(self, smiles: str) -> float:
        """预测GSK3β活性"""
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return 0.0
        num_heteroatoms = sum(1 for atom in mol.GetAtoms()
                              if atom.GetAtomicNum() not in [1, 6])
        score = min(1.0, num_heteroatoms * 0.1)
        return score

    def predict_jnk3(self, smiles: str) -> float:
        """预测JNK3活性"""
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return 0.0
        mol_weight = Descriptors.MolWt(mol)
        if 300 <= mol_weight <= 500:
            return 0.8
        else:
            return 0.3

    def predict(self, smiles: str, property_name: str) -> float:
        """
        统一的预测接口

        Args:
            smiles: SMILES字符串
            property_name: 属性名称 ('qed', 'drd2', 'gsk3b', 'jnk3')

        Returns:
            预测分数
        """
        if property_name == 'qed':
            return self.calculate_qed(smiles)
        elif property_name == 'drd2':
            return self.predict_drd2(smiles)
        elif property_name == 'gsk3b':
            return self.predict_gsk3b(smiles)
        elif property_name == 'jnk3':
            return self.predict_jnk3(smiles)
        else:
            return self.calculate_qed(smiles)


# 测试代码
if __name__ == "__main__":
    print("=" * 50)
    print("测试 molecule_utils 模块")
    print("=" * 50)

    test_smiles = "CC(=O)Oc1ccccc1C(=O)O"  # 阿司匹林

    print(f"\n测试分子: {test_smiles}")
    print(f"是否有效: {MoleculeUtils.validate_smiles(test_smiles)}")
    print(f"QED分数: {MoleculeUtils.calculate_qed(test_smiles):.3f}")
    print(f"分子量: {MoleculeUtils.calculate_mol_weight(test_smiles):.1f}")

    predictor = PropertyPredictor()
    print(f"\n统一接口测试:")
    print(f"  predict('qed'): {predictor.predict(test_smiles, 'qed'):.3f}")
    print(f"  predict('drd2'): {predictor.predict(test_smiles, 'drd2'):.3f}")
    print(f"  predict('gsk3b'): {predictor.predict(test_smiles, 'gsk3b'):.3f}")
    print(f"  predict('jnk3'): {predictor.predict(test_smiles, 'jnk3'):.3f}")

    print("\n✅ molecule_utils 模块测试完成！")