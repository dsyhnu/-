# PDF 超链接和书签验证指南

## 编译完成

论文已成功编译为 PDF,文件位置: `thesis/main.pdf`

## 如何验证书签和超链接

### 方法一: 使用 PDF 阅读器查看书签

1. 用 Adobe Acrobat Reader、Foxit Reader 或其他 PDF 阅读器打开 `main.pdf`
2. 查看左侧的"书签"或"大纲"面板
3. 应该能看到以下层级结构:
   - 摘要
   - Abstract  
   - 1 绪论
     - 1.1 研究背景与意义
     - 1.2 国内外研究现状
     - 1.3 研究内容与目标
     - 1.4 论文组织结构
   - 2 相关理论与技术基础
     - 2.1 分子表示方法
     - 2.2 药物属性预测
     - ... (以此类推)

### 方法二: 测试目录跳转

1. 翻到目录页(通常在第3-4页)
2. 将鼠标悬停在目录条目上,光标应该变成手形
3. 点击任意章节标题,应该能跳转到对应页面
4. 所有章节标题都应该是蓝色的(可点击链接)

### 方法三: 检查交叉引用

在正文中查找类似"见图4-1"、"如表2-1所示"这样的引用:
- 这些引用应该是蓝色的
- 点击后应该能跳转到对应的图表

## 已配置的 hyperref 选项

```latex
\usepackage[
  unicode=true,              % 支持中文书签
  colorlinks=true,           % 使用彩色链接而非红框
  linkcolor=blue,            % 内部链接颜色(章节、图表等)
  citecolor=blue,            % 引用链接颜色
  urlcolor=blue,             % URL链接颜色
  bookmarks=true,            % 生成PDF书签
  bookmarksnumbered=true     % 书签显示章节编号
]{hyperref}
```

## 如果仍然没有书签或超链接

### 可能的原因和解决方案:

1. **PDF阅读器不支持**
   - 尝试使用 Adobe Acrobat Reader DC(免费)
   - 或使用 Foxit Reader、SumatraPDF 等

2. **浏览器预览可能不显示书签**
   - 请下载到本地后用专业PDF阅读器打开
   - 浏览器的PDF插件功能有限

3. **需要重新编译**
   ```bash
   cd thesis
   rm -f *.aux *.log *.toc *.out main.pdf
   xelatex main.tex
   xelatex main.tex
   xelatex main.tex
   ```

4. **检查 hyperref 是否最后加载**
   - hyperref 应该在几乎所有包之后加载
   - 当前配置已正确

## 预期的PDF特性

✅ 左侧有可折叠的书签面板  
✅ 目录中的条目可点击跳转  
✅ 章节标题是蓝色可点击链接  
✅ 图表引用(如"图4-1")可点击跳转  
✅ 参考文献引用可点击跳转  
✅ 无红色边框,使用蓝色文字表示链接  

## 文件大小

- main.pdf: 约 559KB
- 页数: 37页
