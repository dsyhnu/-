"""
结果可视化模块
功能：读取实验结果，绘制收敛曲线对比图
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
from glob import glob

# 设置中文显示
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial']
plt.rcParams['axes.unicode_minus'] = False


def load_latest_stats(folder_path: str) -> pd.DataFrame:
    """加载文件夹中最新的 stats 文件"""
    stats_files = glob(os.path.join(folder_path, "stats_*.csv"))
    if not stats_files:
        return None
    latest_file = max(stats_files, key=os.path.getctime)
    df = pd.read_csv(latest_file)
    print(f"加载成功: {latest_file}")
    return df


def plot_convergence_curves(results_dict: dict, save_path: str = "./convergence_plot.png"):
    """
    绘制收敛曲线对比图

    Args:
        results_dict: 策略名称 -> DataFrame 的字典
        save_path: 保存路径
    """
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    colors = {'basic': 'blue', 'examples': 'green', 'diversity': 'orange'}
    markers = {'basic': 'o', 'examples': 's', 'diversity': '^'}

    # 图1：最佳 QED 收敛曲线
    ax1 = axes[0, 0]
    for name, df in results_dict.items():
        if df is not None and 'best_qed' in df.columns:
            ax1.plot(df['generation'], df['best_qed'],
                     marker=markers.get(name, 'o'),
                     color=colors.get(name, 'black'),
                     linewidth=2, markersize=6, label=name.upper())
    ax1.set_xlabel('代数 (Generation)', fontsize=12)
    ax1.set_ylabel('最佳 QED 分数', fontsize=12)
    ax1.set_title('最佳 QED 收敛曲线对比', fontsize=14)
    ax1.legend(loc='lower right')
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim(0.7, 0.95)

    # 图2：平均 QED 收敛曲线
    ax2 = axes[0, 1]
    for name, df in results_dict.items():
        if df is not None and 'avg_qed' in df.columns:
            ax2.plot(df['generation'], df['avg_qed'],
                     marker=markers.get(name, 'o'),
                     color=colors.get(name, 'black'),
                     linewidth=2, markersize=6, label=name.upper())
    ax2.set_xlabel('代数 (Generation)', fontsize=12)
    ax2.set_ylabel('平均 QED 分数', fontsize=12)
    ax2.set_title('平均 QED 收敛曲线对比', fontsize=14)
    ax2.legend(loc='lower right')
    ax2.grid(True, alpha=0.3)
    ax2.set_ylim(0.6, 0.9)

    # 图3：种群多样性曲线
    ax3 = axes[1, 0]
    for name, df in results_dict.items():
        if df is not None and 'diversity' in df.columns:
            ax3.plot(df['generation'], df['diversity'],
                     marker=markers.get(name, 'o'),
                     color=colors.get(name, 'black'),
                     linewidth=2, markersize=6, label=name.upper())
    ax3.set_xlabel('代数 (Generation)', fontsize=12)
    ax3.set_ylabel('种群多样性', fontsize=12)
    ax3.set_title('种群多样性变化对比', fontsize=14)
    ax3.legend(loc='best')
    ax3.grid(True, alpha=0.3)
    ax3.set_ylim(0, 1)

    # 图4：最终结果柱状图
    ax4 = axes[1, 1]
    names = []
    final_best = []
    final_avg = []

    for name, df in results_dict.items():
        if df is not None and 'best_qed' in df.columns:
            names.append(name.upper())
            final_best.append(df['best_qed'].iloc[-1])
            final_avg.append(df['avg_qed'].iloc[-1])

    x = np.arange(len(names))
    width = 0.35

    bars1 = ax4.bar(x - width / 2, final_best, width, label='最佳 QED', color='steelblue')
    bars2 = ax4.bar(x + width / 2, final_avg, width, label='平均 QED', color='lightcoral')

    # 在柱子上添加数值
    for bar in bars1:
        ax4.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.005,
                 f'{bar.get_height():.3f}', ha='center', va='bottom', fontsize=10)
    for bar in bars2:
        ax4.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.005,
                 f'{bar.get_height():.3f}', ha='center', va='bottom', fontsize=10)

    ax4.set_xlabel('提示策略', fontsize=12)
    ax4.set_ylabel('QED 分数', fontsize=12)
    ax4.set_title('最终结果对比', fontsize=14)
    ax4.set_xticks(x)
    ax4.set_xticklabels(names)
    ax4.legend()
    ax4.set_ylim(0, 1)
    ax4.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.show()
    print(f"\n图表已保存至: {save_path}")


def generate_summary_table(results_dict: dict) -> pd.DataFrame:
    """生成结果汇总表格"""
    summary = []

    for name, df in results_dict.items():
        if df is None:
            continue

        initial_best = df['best_qed'].iloc[0]
        final_best = df['best_qed'].iloc[-1]
        improvement = final_best - initial_best
        improvement_pct = (improvement / initial_best) * 100

        # 找到最佳代数
        best_idx = df['best_qed'].idxmax()
        best_gen = df.loc[best_idx, 'generation']

        summary.append({
            '策略': name.upper(),
            '初始最佳QED': f"{initial_best:.4f}",
            '最终最佳QED': f"{final_best:.4f}",
            '提升幅度': f"{improvement:+.4f} (+{improvement_pct:.1f}%)",
            '最佳代数': int(best_gen),
            '最终多样性': f"{df['diversity'].iloc[-1]:.3f}"
        })

    df_summary = pd.DataFrame(summary)
    return df_summary


# ========== 主程序 ==========
if __name__ == "__main__":
    print("=" * 60)
    print("结果可视化工具")
    print("=" * 60)

    # 定义结果文件夹路径（根据你的实际情况修改）
    folders = {
        'basic': './results_basic',
        'examples': './results_examples',
        'diversity': './results_diversity'
    }

    # 加载数据
    results = {}
    for name, folder in folders.items():
        print(f"\n正在加载 {name} 策略结果...")
        df = load_latest_stats(folder)
        if df is not None:
            results[name] = df
        else:
            print(f"警告: {folder} 中没有找到 stats 文件")
            results[name] = None

    # 生成汇总表格
    print("\n" + "=" * 60)
    print("实验结果汇总")
    print("=" * 60)
    summary_df = generate_summary_table(results)
    print(summary_df.to_string(index=False))

    # 保存汇总表格
    summary_df.to_csv('./results_summary.csv', index=False)
    print("\n汇总表格已保存至: ./results_summary.csv")

    # 绘制对比图
    print("\n正在绘制收敛曲线对比图...")
    plot_convergence_curves(results, save_path='./convergence_comparison.png')

    print("\n✅ 可视化完成！")