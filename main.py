"""
毕业设计主入口文件
运行此文件可以依次演示所有功能
"""

import subprocess
import os


def print_menu():
    """打印菜单"""
    print("=" * 60)
    print("基于大语言模型的分子进化优化器")
    print("=" * 60)
    print("1. 运行进化优化器（快速演示）")
    print("2. 生成对比实验结果图")
    print("3. 展示三种策略对比汇总")
    print("4. 运行随机性测试")
    print("5. 全部运行")
    print("0. 退出")
    print("=" * 60)


def run_optimizer():
    """运行进化优化器"""
    print("\n正在运行进化优化器...\n")
    subprocess.run(["python", "optimizer.py"])


def run_visualize():
    """生成可视化图表"""
    print("\n正在生成对比图表...\n")
    subprocess.run(["python", "visualize_results.py"])


def show_summary():
    """展示结果汇总"""
    import pandas as pd
    import os

    print("\n" + "=" * 60)
    print("三种策略实验结果汇总")
    print("=" * 60)

    # 查找最新的汇总文件
    if os.path.exists("results_summary.csv"):
        df = pd.read_csv("results_summary.csv")
        print(df.to_string(index=False))
    else:
        print("未找到 results_summary.csv，请先运行 visualize_results.py")

    # 显示对比图
    if os.path.exists("convergence_comparison.png"):
        print("\n对比图已生成: convergence_comparison.png")
        print("请在项目目录中打开查看")
    else:
        print("未找到 convergence_comparison.png")


def run_randomness():
    """运行随机性测试"""
    print("\n正在运行随机性测试...\n")
    subprocess.run(["python", "randomness_test.py"])


def run_all():
    """运行所有"""
    run_optimizer()
    run_visualize()
    show_summary()


if __name__ == "__main__":
    while True:
        print_menu()
        choice = input("请选择功能 (0-5): ")

        if choice == "1":
            run_optimizer()
        elif choice == "2":
            run_visualize()
        elif choice == "3":
            show_summary()
        elif choice == "4":
            run_randomness()
        elif choice == "5":
            run_all()
        elif choice == "0":
            print("退出程序")
            break
        else:
            print("输入无效，请重新选择")

        input("\n按回车键继续...")