"""
QQ 群聊天记录自动下载脚本
根据校准的坐标，按顺序点击完成导出
"""
import json
import time
import argparse
from pathlib import Path
from datetime import datetime, timedelta

try:
    import pyautogui
    import pygetwindow as gw
except ImportError:
    print("请先安装依赖: pip install pyautogui pygetwindow")
    exit(1)

# 加载坐标
COORDS_FILE = Path(__file__).parent / "coordinates.json"

# 每个操作之间的等待时间（秒）
ACTION_WAIT = 1.0
SCROLL_WAIT = 0.5
EXPORT_WAIT = 5.0  # 等待导出对话框出现
SAVE_WAIT = 3.0    # 保存后等待


def load_coordinates():
    """加载校准的坐标"""
    if not COORDS_FILE.exists():
        print("❌ 坐标文件不存在，请先运行 calibrate.py 进行校准")
        exit(1)
    
    with open(COORDS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def do_action(coord_name: str, coords: dict, wait: float = None, description: str = ""):
    """
    根据坐标执行操作（自动识别左键/双击/右键/滚轮）
    """
    coord = coords.get(coord_name)
    if not coord:
        print(f"  ⚠️ 坐标 '{coord_name}' 未设置，跳过")
        return False
    
    action_type = coord.get("action", "click")
    x, y = coord["x"], coord["y"]
    
    if description:
        type_label = {"click": "点击", "double": "双击", "right": "右键", "click12": "点12次", "click1": "点1次"}.get(action_type, "点击")
        print(f"  → [{type_label}] {description}")
    
    if action_type == "right":
        # 右键点击
        pyautogui.rightClick(x, y)
        time.sleep(wait or ACTION_WAIT)
    elif action_type == "double":
        # 双击
        pyautogui.doubleClick(x, y)
        time.sleep(wait or ACTION_WAIT)
    elif action_type == "click12":
        # 点击下滑按钮 12 次（滑到底）
        for i in range(12):
            pyautogui.click(x, y)
            time.sleep(0.15)
        time.sleep(wait or ACTION_WAIT)
    elif action_type == "click1":
        # 点击下滑按钮 1 次
        pyautogui.click(x, y)
        time.sleep(wait or ACTION_WAIT)
    else:
        # 左键点击
        pyautogui.click(x, y)
        time.sleep(wait or ACTION_WAIT)
    
    return True


def activate_qq_window():
    """激活 QQ 窗口"""
    try:
        qq_windows = [w for w in gw.getWindowsWithTitle('QQ') if 'QQ' in w.title]
        if qq_windows:
            qq_windows[0].activate()
            time.sleep(1)
            return True
    except Exception as e:
        print(f"  ⚠️ 激活窗口出错: {e}")
    return False


def export_group1(coords: dict):
    """
    导出地球群1的聊天记录
    """
    print("\n" + "=" * 40)
    print("📁 导出地球群1...")
    print("=" * 40)
    
    # 1. 点击群聊按钮
    do_action("qunliao_box", coords, description="群聊按钮")
    
    # 2. 点击地球群1
    do_action("group1_entry", coords, description="选择地球群1")
    
    # 3. 右键点击弹出菜单
    do_action("group1_right", coords, description="右键弹出菜单")
    
    # 4. 点击导出聊天记录
    do_action("group1_export", coords, wait=EXPORT_WAIT, description="导出聊天记录")
    
    # 5. 选择保存路径（双击打开文件夹）
    do_action("group1_pc", coords, description="此电脑")
    do_action("group1_disk_e", coords, description="磁盘E")
    do_action("group1_scroll1", coords, description="下滑到底")
    do_action("group1_project", coords, description="项目文件夹")
    do_action("group1_player", coords, description="玩家社群分析")
    do_action("group1_scroll2", coords, description="下滑一次")
    do_action("group1_yunying", coords, description="供运营")
    do_action("group1_daily", coords, description="单日copy")
    
    # 6. 选择保存格式
    do_action("group1_format", coords, description="下拉保存类型")
    do_action("group1_txt", coords, description="选择txt格式")
    
    # 7. 保存
    do_action("group1_save", coords, wait=1.5, description="保存")
    
    # 8. 处理"文件已存在，是否覆盖"对话框
    print("  → [按键] 确认覆盖（按 Y 键）")
    time.sleep(0.5)
    pyautogui.press('y')  # 按 Y 确认覆盖
    time.sleep(SAVE_WAIT)
    
    print("  ✅ 地球群1 导出完成")


def export_group2(coords: dict):
    """
    导出地球群2的聊天记录
    """
    print("\n" + "=" * 40)
    print("📁 导出地球群2...")
    print("=" * 40)
    
    # 1. 点击地球群2
    do_action("group2_entry", coords, description="选择地球群2")
    
    # 2. 右键点击弹出菜单
    do_action("group2_right", coords, description="右键弹出菜单")
    
    # 3. 点击导出聊天记录
    do_action("group2_export", coords, wait=EXPORT_WAIT, description="导出聊天记录")
    
    # 4. 选择保存路径（双击打开文件夹）
    do_action("group2_pc", coords, description="此电脑")
    do_action("group2_disk_e", coords, description="磁盘E")
    do_action("group2_scroll1", coords, description="下滑到底")
    do_action("group2_project", coords, description="项目文件夹")
    do_action("group2_player", coords, description="玩家社群分析")
    do_action("group2_scroll2", coords, description="下滑一次")
    do_action("group2_yunying", coords, description="供运营")
    do_action("group2_daily", coords, description="单日copy")
    
    # 5. 选择保存格式
    do_action("group2_format", coords, description="下拉保存类型")
    do_action("group2_txt", coords, description="选择txt格式")
    
    # 6. 保存
    do_action("group2_save", coords, wait=1.5, description="保存")
    
    # 7. 处理"文件已存在，是否覆盖"对话框
    print("  → [按键] 确认覆盖（按 Y 键）")
    time.sleep(0.5)
    pyautogui.press('y')  # 按 Y 确认覆盖
    time.sleep(SAVE_WAIT)
    
    print("  ✅ 地球群2 导出完成")


def main():
    parser = argparse.ArgumentParser(description="QQ群聊天记录自动下载")
    parser.add_argument("--test", action="store_true", help="测试模式（只显示坐标不执行）")
    parser.add_argument("--group", type=int, choices=[1, 2], help="只导出指定群 (1 或 2)")
    args = parser.parse_args()
    
    print("=" * 60)
    print("🤖 QQ 群聊天记录自动下载")
    print(f"⏰ 时间: {datetime.now()}")
    print("=" * 60)
    
    # 加载坐标
    coords = load_coordinates()
    
    if args.test:
        print("\n⚠️ 测试模式 - 只显示坐标，不执行操作")
        print("\n已加载的坐标：")
        for key, value in coords.items():
            if value:
                action = value.get("action", "click")
                type_label = {"click": "左键", "double": "双击", "right": "右键", "click12": "点12次", "click1": "点1次"}.get(action, "左键")
                print(f"  {key}: ({value['x']}, {value['y']}) [{type_label}]")
            else:
                print(f"  {key}: 未设置")
        return
    
    # 激活 QQ 窗口
    print("\n激活 QQ 窗口...")
    do_action("qq_icon", coords, description="QQ 图标")
    time.sleep(2)
    
    # 导出群聊记录
    try:
        if args.group == 1:
            export_group1(coords)
        elif args.group == 2:
            export_group2(coords)
        else:
            # 导出所有群
            export_group1(coords)
            time.sleep(2)
            export_group2(coords)
        
        print("\n" + "=" * 60)
        print("✅ 全部导出完成！")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 导出出错: {e}")
        import traceback
        traceback.print_exc()
    
    # 记录日志
    log_file = Path(__file__).parent / "download_log.txt"
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"{datetime.now()} - 导出完成\n")


if __name__ == "__main__":
    main()
