#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
代码统计工具 - 统计项目代码行数、函数数、类数等信息
"""

import os
import ast
from pathlib import Path
from typing import Dict, List, Tuple


class CodeStatistics:
    """代码统计类"""

    def __init__(self, root_dir: str = '.'):
        self.root_dir = Path(root_dir)
        self.stats = {
            'total_files': 0,
            'python_files': 0,
            'html_files': 0,
            'total_lines': 0,
            'python_lines': 0,
            'html_lines': 0,
            'total_functions': 0,
            'total_classes': 0,
            'file_details': []
        }

    def count_lines(self, file_path: Path) -> int:
        """统计文件行数"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return len(f.readlines())
        except:
            return 0

    def analyze_python_file(self, file_path: Path) -> Tuple[int, int, int]:
        """分析Python文件"""
        lines = self.count_lines(file_path)
        functions = 0
        classes = 0

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
                tree = ast.parse(code)

                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        functions += 1
                    elif isinstance(node, ast.ClassDef):
                        classes += 1
        except:
            pass

        return lines, functions, classes

    def analyze_html_file(self, file_path: Path) -> int:
        """分析HTML文件"""
        return self.count_lines(file_path)

    def analyze(self):
        """执行统计分析"""
        print(f"正在分析目录: {self.root_dir}")
        print("-" * 60)

        # 遍历所有文件
        for file_path in self.root_dir.rglob('*'):
            if file_path.is_file():
                self.stats['total_files'] += 1

                if file_path.suffix == '.py':
                    lines, functions, classes = self.analyze_python_file(file_path)
                    self.stats['python_files'] += 1
                    self.stats['python_lines'] += lines
                    self.stats['total_functions'] += functions
                    self.stats['total_classes'] += classes
                    self.stats['total_lines'] += lines

                    self.stats['file_details'].append({
                        'file': str(file_path.relative_to(self.root_dir)),
                        'type': 'Python',
                        'lines': lines,
                        'functions': functions,
                        'classes': classes
                    })

                elif file_path.suffix in ['.html', '.htm']:
                    lines = self.analyze_html_file(file_path)
                    self.stats['html_files'] += 1
                    self.stats['html_lines'] += lines
                    self.stats['total_lines'] += lines

                    self.stats['file_details'].append({
                        'file': str(file_path.relative_to(self.root_dir)),
                        'type': 'HTML',
                        'lines': lines,
                        'functions': 0,
                        'classes': 0
                    })

    def print_summary(self):
        """打印统计摘要"""
        print("\n" + "=" * 60)
        print("代码统计摘要")
        print("=" * 60)
        print(f"总文件数:          {self.stats['total_files']}")
        print(f"Python文件数:      {self.stats['python_files']}")
        print(f"HTML文件数:        {self.stats['html_files']}")
        print(f"总代码行数:        {self.stats['total_lines']}")
        print(f"Python代码行数:    {self.stats['python_lines']}")
        print(f"HTML代码行数:      {self.stats['html_lines']}")
        print(f"总函数数:          {self.stats['total_functions']}")
        print(f"总类数:            {self.stats['total_classes']}")
        print("=" * 60)

    def print_file_details(self):
        """打印文件详情"""
        print("\n文件详情:")
        print("-" * 100)
        print(f"{'文件路径':<50} {'类型':<10} {'行数':<10} {'函数数':<10} {'类数':<10}")
        print("-" * 100)

        for detail in self.stats['file_details']:
            print(f"{detail['file']:<50} {detail['type']:<10} "
                  f"{detail['lines']:<10} {detail['functions']:<10} {detail['classes']:<10}")

    def export_to_markdown(self, output_file: str = 'code_statistics.md'):
        """导出为Markdown格式"""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# 代码统计报告\n\n")
            f.write("## 统计摘要\n\n")
            f.write("| 项目 | 数值 |\n")
            f.write("|------|------|\n")
            f.write(f"| 总文件数 | {self.stats['total_files']} |\n")
            f.write(f"| Python文件数 | {self.stats['python_files']} |\n")
            f.write(f"| HTML文件数 | {self.stats['html_files']} |\n")
            f.write(f"| 总代码行数 | {self.stats['total_lines']} |\n")
            f.write(f"| Python代码行数 | {self.stats['python_lines']} |\n")
            f.write(f"| HTML代码行数 | {self.stats['html_lines']} |\n")
            f.write(f"| 总函数数 | {self.stats['total_functions']} |\n")
            f.write(f"| 总类数 | {self.stats['total_classes']} |\n\n")

            f.write("## 文件详情\n\n")
            f.write("| 文件路径 | 类型 | 行数 | 函数数 | 类数 |\n")
            f.write("|---------|------|------|--------|------|\n")

            for detail in self.stats['file_details']:
                f.write(f"| {detail['file']} | {detail['type']} | {detail['lines']} | "
                       f"{detail['functions']} | {detail['classes']} |\n")

        print(f"\n统计报告已导出至: {output_file}")


def main():
    """主函数"""
    # 统计当前目录
    stats = CodeStatistics('.')
    stats.analyze()
    stats.print_summary()
    stats.print_file_details()
    stats.export_to_markdown()


if __name__ == '__main__':
    main()