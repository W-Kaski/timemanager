import PyInstaller.__main__
import os

# 确保sounds目录存在
if not os.path.exists('sounds'):
    os.makedirs('sounds')

# 运行PyInstaller
PyInstaller.__main__.run([
    'time_manager_gui.py',
    '--onefile',
    '--windowed',
    '--name=时间管理工具',
    '--add-data=sounds;sounds',  # 添加sounds目录
    '--icon=NONE'  # 如果有图标文件，替换NONE为图标路径
]) 