"""
LLM 交互模块
功能：封装 Ollama API 调用，实现与大语言模型的交互
"""

import requests
import re
from typing import List


class LLMClient:
    """大语言模型客户端"""

    def __init__(self,
                 model_name: str = "qwen2.5:7b",
                 base_url: str = "http://localhost:11434",
                 temperature: float = 0.8):
        """
        初始化LLM客户端

        Args:
            model_name: Ollama中的模型名称（如 qwen2.5:7b, llama3.2:3b）
            base_url: Ollama服务地址
            temperature: 生成温度（0-1，越高越随机）
        """
        self.model_name = model_name
        self.base_url = base_url
        self.temperature = temperature
        self.api_url = f"{base_url}/api/generate"

        # 测试连接
        self._test_connection()

    def _test_connection(self):
        """测试Ollama服务连接"""
        try:
            response = requests.get(f"{self.base_url}", timeout=5)
            if response.status_code == 200:
                print(f"✅ Ollama连接成功，使用模型: {self.model_name}")
            else:
                print(f"⚠️ Ollama返回状态码: {response.status_code}")
        except requests.exceptions.ConnectionError:
            print(f"❌ 无法连接到Ollama，请确保服务已启动")
            print("请在命令行运行: ollama serve")

    def generate(self, prompt: str, n: int = 3) -> List[str]:
        """
        生成分子SMILES

        Args:
            prompt: 提示词
            n: 生成数量

        Returns:
            生成的SMILES列表
        """
        # 添加数量要求
        enhanced_prompt = prompt + f"\n请生成{n}个不同的分子，每行一个SMILES。"

        try:
            response = requests.post(
                self.api_url,
                json={
                    "model": self.model_name,
                    "prompt": enhanced_prompt,
                    "stream": False,
                    "options": {
                        "temperature": self.temperature
                    }
                },
                timeout=60
            )

            if response.status_code == 200:
                result = response.json()
                text = result.get("response", "")
                smiles_list = self._parse_smiles_from_text(text)
                return smiles_list[:n]
            else:
                print(f"API调用失败: {response.status_code}")
                return []

        except Exception as e:
            print(f"生成失败: {e}")
            return []

    def _parse_smiles_from_text(self, text: str) -> List[str]:
        """
        从LLM返回的文本中提取SMILES
        处理各种可能的格式
        """
        smiles_list = []
        lines = text.strip().split('\n')

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # 去除常见的序号标记（如 "1.", "2)", "- ", "* "）
            line = re.sub(r'^\d+[\.\)\s]+', '', line)
            line = re.sub(r'^[\-\*\+]\s+', '', line)

            # 简单验证是否是SMILES（包含原子符号，长度合理）
            if len(line) > 3 and len(line) < 200:
                # 检查是否包含字母（SMILES必须包含原子）
                if re.search(r'[A-Za-z]', line):
                    smiles_list.append(line)

        return smiles_list


# 测试代码
if __name__ == "__main__":
    print("=" * 50)
    print("测试 LLM 客户端")
    print("=" * 50)

    # 注意：运行前请确保 Ollama 服务已启动
    # 在命令行运行: ollama serve

    # 初始化客户端
    client = LLMClient(model_name="qwen2.5:7b")

    # 测试生成
    print("\n正在生成分子...")
    prompt = "生成一个简单的药物分子SMILES，例如阿司匹林或布洛芬"
    result = client.generate(prompt, n=2)

    print(f"\n生成的SMILES:")
    for i, smiles in enumerate(result, 1):
        print(f"  {i}. {smiles}")

    print("\n✅ LLM客户端测试完成！")