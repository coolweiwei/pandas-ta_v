import os
import re

# 定义项目目录
project_dir = 'd:/pandas_ta_v/pandas-ta_v/pandas_ta/'  # 替换为你的项目路径

# 遍历项目中的所有文件
for root, dirs, files in os.walk(project_dir):
    for file in files:
        if file.endswith('.py'):  # 仅处理Python文件
            file_path = os.path.join(root, file)
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 替换 import 语句
            content = re.sub(r'^from\s+numpy\s+import\s+nan\s+as\s+np.nan', 'import numpy as np', content, flags=re.MULTILINE)
            
            # 替换 np.nan 为 np.nan
            content = content.replace('np.nan', 'np.nan')
            
            # 将修改后的内容写回文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

print("替换完成。")