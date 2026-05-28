#!/bin/bash
# 论文编译脚本

echo "开始编译论文..."

# 进入thesis目录
cd "$(dirname "$0")/thesis" || exit 1

# 清理之前的编译文件
echo "清理临时文件..."
latexmk -c main.tex

# 使用xelatex编译（支持中文字体）
echo "第一次编译..."
xelatex -interaction=nonstopmode main.tex

echo "第二次编译（处理引用）..."
xelatex -interaction=nonstopmode main.tex

echo "第三次编译（确保所有交叉引用正确）..."
xelatex -interaction=nonstopmode main.tex

# 检查是否成功
if [ -f "main.pdf" ]; then
    echo ""
    echo "✓ 编译成功！"
    echo "PDF文件: $(pwd)/main.pdf"
    ls -lh main.pdf
else
    echo ""
    echo "✗ 编译失败！"
    exit 1
fi
