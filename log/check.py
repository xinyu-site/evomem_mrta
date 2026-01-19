import os
import re
from collections import defaultdict
from pathlib import Path

def analyze_log_files(directory="."):
    """
    分析目录下所有run_php_开头的文件夹中的test_log文件
    
    Args:
        directory: 要分析的目录，默认为当前目录
    """
    
    # 存储统计结果
    # 结构: {种类名: {"total": 总数, "true_count": True数量}}
    stats = defaultdict(lambda: {"total": 0, "true_count": 0})
    
    # 获取当前目录下所有run_php_开头的文件夹
    base_path = Path(directory)
    
    for item in base_path.iterdir():
        if item.is_dir() and item.name.startswith("run_coe_"):
            # 提取种类名称（去掉时间戳）
            folder_name = item.name
            # 移除"run_php_"前缀
            name_without_prefix = folder_name[8:]
            
            # 使用正则表达式匹配种类名称和数字时间戳
            # 假设种类名称由字母、数字和下划线组成，时间戳是纯数字
            match = re.match(r'^(.+?)_(\d+)$', name_without_prefix)
            
            if match:
                category = match.group(1)  # 种类名称
                timestamp = match.group(2)  # 时间戳（我们不需要这个）
                
                # 查找以test_log结尾的txt文件
                log_files = list(item.glob("*test_log*.txt"))
                
                if log_files:
                    # 假设每个文件夹下只有一个test_log文件
                    log_file = log_files[0]
                    
                    try:
                        with open(log_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                        # 更新统计信息
                        stats[category]["total"] += 1
                        
                        # 检查是否包含True（区分大小写）
                        if "True" in content:
                            stats[category]["true_count"] += 1
                            print(f"✓ {folder_name}: 包含True")
                        else:
                            print(f"✗ {folder_name}: 不包含True")
                            
                    except Exception as e:
                        print(f"错误: 无法读取文件 {log_file}: {e}")
                        stats[category]["total"] += 1  # 仍然计入总数，但不算True
                else:
                    print(f"警告: {folder_name} 中没有找到test_log文件")
            else:
                print(f"警告: 无法解析文件夹名 {folder_name}")
    
    return stats

def print_statistics(stats):
    """打印统计结果"""
    print("\n" + "="*50)
    print("统计结果:")
    print("="*50)
    
    if not stats:
        print("没有找到任何符合条件的文件夹")
        return
    
    # 按种类名称排序
    sorted_categories = sorted(stats.items())
    
    print(f"{'种类':<20} {'总数':<8} {'True数量':<10} {'正确率':<10}")
    print("-"*50)
    
    for category, data in sorted_categories:
        total = data["total"]
        true_count = data["true_count"]
        
        if total > 0:
            accuracy = true_count / total * 100
        else:
            accuracy = 0.0
            
        print(f"{category:<20} {total:<8} {true_count:<10} {accuracy:.2f}%")
    
    print("="*50)
    
    # 计算总体统计
    total_folders = sum(data["total"] for data in stats.values())
    total_true = sum(data["true_count"] for data in stats.values())
    
    if total_folders > 0:
        overall_accuracy = total_true / total_folders * 100
        print(f"\n总体统计:")
        print(f"总文件夹数: {total_folders}")
        print(f"包含True的文件夹数: {total_true}")
        print(f"总体正确率: {overall_accuracy:.2f}%")
    else:
        print("\n没有找到任何有效的文件夹")

def main():
    """主函数"""
    # 你可以在这里指定目录，或者使用当前目录
    target_directory = "."  # 当前目录
    # target_directory = "/path/to/your/directory"  # 或者指定目录
    
    print(f"正在分析目录: {os.path.abspath(target_directory)}")
    print("正在搜索run_php_开头的文件夹...\n")
    
    # 分析日志文件
    stats = analyze_log_files(target_directory)
    
    # 打印统计结果
    print_statistics(stats)
    
    # 可选：保存结果到文件
    save_to_file = input("\n是否要将结果保存到文件？(y/n): ").lower()
    if save_to_file == 'y':
        filename = "log_analysis_results.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("日志文件分析结果\n")
            f.write("="*50 + "\n\n")
            
            for category, data in sorted(stats.items()):
                total = data["total"]
                true_count = data["true_count"]
                accuracy = true_count / total * 100 if total > 0 else 0.0
                f.write(f"种类: {category}\n")
                f.write(f"  总数: {total}\n")
                f.write(f"  True数量: {true_count}\n")
                f.write(f"  正确率: {accuracy:.2f}%\n\n")
            
            # 总体统计
            total_folders = sum(data["total"] for data in stats.values())
            total_true = sum(data["true_count"] for data in stats.values())
            overall_accuracy = total_true / total_folders * 100 if total_folders > 0 else 0.0
            
            f.write("总体统计:\n")
            f.write(f"总文件夹数: {total_folders}\n")
            f.write(f"包含True的文件夹数: {total_true}\n")
            f.write(f"总体正确率: {overall_accuracy:.2f}%\n")
        
        print(f"结果已保存到: {filename}")

if __name__ == "__main__":
    main()