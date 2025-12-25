"""
坐标校准工具
运行此脚本，按照提示点击 QQ 界面的各个位置
"""
import json
import time
from pathlib import Path

try:
    import pyautogui
    import keyboard
except ImportError:
    print("请先安装依赖: pip install pyautogui keyboard")
    exit(1)

# 需要校准的坐标点
# 格式: (key名, 操作说明, 操作类型)
# 操作类型: "click"=左键, "double"=双击, "right"=右键, "click12"=点击12次, "click1"=点击1次
CALIBRATION_POINTS = [
    # ========== 通用操作 ==========
    ("qq_icon", "任务栏上的 QQ 图标", "click"),
    ("qunliao_box", "点击群聊按钮", "click"),
    
    # ========== 地球群1 ==========
    ("group1_entry", "地球群1 (左键点击进入)", "click"),
    ("group1_right", "地球群1 (右键弹出菜单的位置)", "right"),
    ("group1_export", "导出聊天记录 按钮", "click"),
    ("group1_pc", "此电脑 按钮", "double"),        # 双击打开
    ("group1_disk_e", "磁盘E 按钮", "double"),     # 双击打开
    ("group1_scroll1", "滚动条下滑按钮 ▼ (点击12次到底)", "click12"),
    ("group1_project", "项目 文件夹", "double"),   # 双击打开
    ("group1_player", "玩家社群分析 文件夹", "double"),  # 双击打开
    ("group1_scroll2", "滚动条下滑按钮 ▼ (点击1次)", "click1"),
    ("group1_yunying", "供运营 文件夹", "double"), # 双击打开
    ("group1_daily", "单日copy 文件夹", "double"), # 双击打开
    ("group1_format", "下拉保存类型", "click"),
    ("group1_txt", "选择 txt 格式", "click"),
    ("group1_save", "保存 按钮", "click"),
   
    
    

    # ========== 地球群2 ==========
    ("group2_entry", "地球群2 (左键点击进入)", "click"),
    ("group2_right", "地球群2 (右键弹出菜单的位置)", "right"),
    ("group2_export", "导出聊天记录 按钮", "click"),
    ("group2_pc", "此电脑 按钮", "double"),        # 双击打开
    ("group2_disk_e", "磁盘E 按钮", "double"),     # 双击打开
    ("group2_scroll1", "滚动条下滑按钮 ▼ (点击12次到底)", "click12"),
    ("group2_project", "项目 文件夹", "double"),   # 双击打开
    ("group2_player", "玩家社群分析 文件夹", "double"),  # 双击打开
    ("group2_scroll2", "滚动条下滑按钮 ▼ (点击1次)", "click1"),
    ("group2_yunying", "供运营 文件夹", "double"), # 双击打开
    ("group2_daily", "单日copy 文件夹", "double"), # 双击打开
    ("group2_format", "下拉保存类型", "click"),
    ("group2_txt", "选择 txt 格式", "click"),
    ("group2_save", "保存 按钮", "click"),

]

def main():
    print("=" * 60)
    print("QQ 自动导出 - 坐标校准工具") 
    print("=" * 60)
    print()
    print("使用说明：")
    print("1. 确保 QQ 已打开并登录")
    print("2. 按照提示，将鼠标移动到指定位置")
    print("3. 按 空格键 记录当前鼠标位置")
    print("4. 按 ESC 键跳过当前项")
    print("5. 按 Q 键退出")
    print()
    print("操作类型说明：")
    print("  [左键] = 普通点击")
    print("  [双击] = 双击打开文件夹")
    print("  [右键] = 右键点击弹出菜单")
    print("  [点12次] = 点击下滑按钮12次（滑到底）")
    print("  [点1次] = 点击下滑按钮1次")
    print()
    print("准备好后按 空格键 开始...")
    
    keyboard.wait('space')
    
    coordinates = {}
    
    for item in CALIBRATION_POINTS:
        key = item[0]
        description = item[1]
        action_type = item[2] if len(item) > 2 else "click"
        
        # 显示操作类型
        type_label = {"click": "左键", "double": "双击", "right": "右键", "click12": "点12次", "click1": "点1次"}.get(action_type, "左键")
        
        print()
        print("-" * 40)
        print(f"[{type_label}] 请将鼠标移动到: {description}")
        print("然后按 空格键 记录位置（ESC 跳过）")
        
        while True:
            if keyboard.is_pressed('space'):
                x, y = pyautogui.position()
                coordinates[key] = {"x": x, "y": y, "action": action_type}
                print(f"✅ 已记录 {key}: ({x}, {y}) [{type_label}]")
                time.sleep(0.5)  # 防止连续触发
                break
            elif keyboard.is_pressed('escape'):
                coordinates[key] = None
                print(f"⏭️ 跳过 {key}")
                time.sleep(0.5)
                break
            elif keyboard.is_pressed('q'):
                print("\n已退出校准")
                return
            time.sleep(0.1)
    
    # 保存坐标
    output_file = Path(__file__).parent / "coordinates.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(coordinates, f, indent=2, ensure_ascii=False)
    
    print()
    print("=" * 60)
    print(f"✅ 校准完成！坐标已保存到: {output_file}")
    print("=" * 60)
    print()
    print("已记录的坐标：")
    for key, value in coordinates.items():
        if value:
            action = value.get("action", "click")
            type_label = {"click": "左键", "double": "双击", "right": "右键", "click12": "点12次", "click1": "点1次"}.get(action, "左键")
            print(f"  {key}: ({value['x']}, {value['y']}) [{type_label}]")
        else:
            print(f"  {key}: 未设置")


if __name__ == "__main__":
    main()
