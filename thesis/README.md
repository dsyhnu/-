# 毕业论文 LaTeX 模板

## 论文题目
基于大语言模型的分子进化优化方法研究

## 文件结构

```
thesis/
├── main.tex                    # 主文件
├── abstract.tex                # 中英文摘要
├── chapter1_introduction.tex   # 第一章 绪论
├── chapter2_related_work.tex   # 第二章 相关理论与技术基础
├── chapter3_methodology.tex    # 第三章 基于LLM的分子进化优化方法
├── chapter4_experiments.tex    # 第四章 实验与结果分析
├── chapter5_conclusion.tex     # 第五章 总结与展望(含参考文献)
└── acknowledgements.tex        # 致谢
```

## 编译方法

### 方法一: 使用 pdflatex (推荐)

```bash
cd thesis
pdflatex main.tex
bibtex main.aux  # 如果需要处理参考文献
pdflatex main.tex
pdflatex main.tex  # 运行多次以生成正确的目录和引用
```

### 方法二: 使用 xelatex (更好的中文支持)

```bash
cd thesis
xelatex main.tex
bibtex main.aux
xelatex main.tex
xelatex main.tex
```

### 方法三: 使用 latexmk (自动化编译)

```bash
cd thesis
latexmk -pdf main.tex
# 或者使用 xelatex
latexmk -pdfxe main.tex
# 清理临时文件
latexmk -c
```

## 论文特点

1. **口语化但正式**: 使用了大量"的、了、到、过、会、有、能、把"等虚词,使文章读起来更自然流畅
2. **避免生硬连接词**: 用"一是、二是、三是"或"一方面、另一方面"替代"首先、其次、最后"
3. **长短句交替**: 专业术语密集的句子较短,非专业句子较长,增强可读性
4. **减少句号使用**: 多用逗号或分号连接相关句子
5. **同义词替换**: 将正式词汇换成简单易懂的词语
6. **改变句子结构**: 调整语序,避免千篇一律的表达方式

## 论文结构

- **摘要**: 中英文摘要,约800-1000字
- **第一章 绪论**: 研究背景与意义、国内外研究现状、研究内容与目标
- **第二章 相关理论与技术基础**: 分子表示方法、药物属性预测、进化算法原理、大语言模型基础
- **第三章 基于LLM的分子进化优化方法**: 系统架构、各模块设计、算法流程
- **第四章 实验与结果分析**: 实验设置、对比实验、多样性分析、随机性测试、结果讨论
- **第五章 总结与展望**: 研究工作总结、不足之处、未来展望、参考文献
- **致谢**: 感谢导师、同学、家人等

## 字数统计

整篇论文约25,000-30,000字,符合本科毕业论文要求。

## 注意事项

1. 请根据实际情况修改封面信息(姓名、学号、专业、指导教师等)
2. 参考文献可以根据实际需要添加或删除
3. 如果学校有特定的格式要求,请相应调整 LaTeX 模板
4. 建议在最终提交前,多次编译以确保目录、引用、页码等都正确生成

## 依赖的 LaTeX 宏包

- `ctex`: 中文支持
- `geometry`: 页面布局
- `amsmath`: 数学公式
- `graphicx`: 图片插入
- `booktabs`: 表格美化
- `hyperref`: 超链接
- `fancyhdr`: 页眉页脚
- `cite`: 引用管理

## 常见问题

**Q: 中文显示乱码怎么办?**
A: 确保使用 UTF-8 编码保存文件,并使用 xelatex 编译。

**Q: 如何插入图片?**
A: 在相应位置使用 `\includegraphics[width=0.8\textwidth]{filename.png}`

**Q: 如何添加新的章节?**
A: 创建新的 .tex 文件,并在 main.tex 中添加 `\include{新文件名}`

**Q: 参考文献格式不对怎么办?**
A: 可以手动调整 thebibliography 环境中的格式,或使用 BibTeX 管理参考文献。

## 联系信息

如有问题,请联系: 杜森源 (202208010211@hnu.edu.cn)
