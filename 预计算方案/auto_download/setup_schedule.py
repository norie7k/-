"""
设置 Windows 任务计划程序
1. 每天凌晨 00:05 自动下载聊天记录
2. 每天晚上 23:30 自动删除聊天记录

用法: python setup_schedule.py [--yes]
"""
import os
import sys
import subprocess
import argparse
from pathlib import Path


def create_download_task(script_dir, pythonw_exe):
    """创建下载任务 - 每天 00:05"""
    
    download_script = script_dir / "download_chat.py"
    task_name = "QQ群聊天记录自动下载"
    
    xml_template = f'''<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Description>每天凌晨自动下载QQ群聊天记录</Description>
  </RegistrationInfo>
  <Triggers>
    <CalendarTrigger>
      <StartBoundary>2025-01-01T00:05:00</StartBoundary>
      <Enabled>true</Enabled>
      <ScheduleByDay>
        <DaysInterval>1</DaysInterval>
      </ScheduleByDay>
    </CalendarTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <LogonType>InteractiveToken</LogonType>
      <RunLevel>LeastPrivilege</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <AllowHardTerminate>true</AllowHardTerminate>
    <StartWhenAvailable>true</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>false</RunOnlyIfNetworkAvailable>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <Enabled>true</Enabled>
    <Hidden>false</Hidden>
    <RunOnlyIfIdle>false</RunOnlyIfIdle>
    <WakeToRun>true</WakeToRun>
    <ExecutionTimeLimit>PT1H</ExecutionTimeLimit>
    <Priority>7</Priority>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>{pythonw_exe}</Command>
      <Arguments>"{download_script}"</Arguments>
      <WorkingDirectory>{script_dir}</WorkingDirectory>
    </Exec>
  </Actions>
</Task>
'''
    
    xml_file = script_dir / "task_download.xml"
    with open(xml_file, "w", encoding="utf-16") as f:
        f.write(xml_template)
    
    print(f"\n📥 创建下载任务: {task_name}")
    print(f"   执行时间: 每天 00:05")
    
    subprocess.run(["schtasks", "/delete", "/tn", task_name, "/f"], capture_output=True)
    result = subprocess.run(
        ["schtasks", "/create", "/tn", task_name, "/xml", str(xml_file)],
        capture_output=True, text=True
    )
    
    if result.returncode == 0:
        print(f"   ✅ 创建成功")
        return True
    else:
        print(f"   ❌ 创建失败: {result.stderr}")
        return False


def create_cleanup_task(script_dir, pythonw_exe):
    """创建清理任务 - 每天 23:30"""
    
    cleanup_script = script_dir / "cleanup_chat.py"
    task_name = "QQ群聊天记录自动清理"
    
    xml_template = f'''<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Description>每天晚上自动删除QQ群聊天记录</Description>
  </RegistrationInfo>
  <Triggers>
    <CalendarTrigger>
      <StartBoundary>2025-01-01T23:30:00</StartBoundary>
      <Enabled>true</Enabled>
      <ScheduleByDay>
        <DaysInterval>1</DaysInterval>
      </ScheduleByDay>
    </CalendarTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <LogonType>InteractiveToken</LogonType>
      <RunLevel>LeastPrivilege</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <AllowHardTerminate>true</AllowHardTerminate>
    <StartWhenAvailable>true</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>false</RunOnlyIfNetworkAvailable>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <Enabled>true</Enabled>
    <Hidden>false</Hidden>
    <RunOnlyIfIdle>false</RunOnlyIfIdle>
    <WakeToRun>false</WakeToRun>
    <ExecutionTimeLimit>PT10M</ExecutionTimeLimit>
    <Priority>7</Priority>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>{pythonw_exe}</Command>
      <Arguments>"{cleanup_script}"</Arguments>
      <WorkingDirectory>{script_dir}</WorkingDirectory>
    </Exec>
  </Actions>
</Task>
'''
    
    xml_file = script_dir / "task_cleanup.xml"
    with open(xml_file, "w", encoding="utf-16") as f:
        f.write(xml_template)
    
    print(f"\n🗑️ 创建清理任务: {task_name}")
    print(f"   执行时间: 每天 23:30")
    
    subprocess.run(["schtasks", "/delete", "/tn", task_name, "/f"], capture_output=True)
    result = subprocess.run(
        ["schtasks", "/create", "/tn", task_name, "/xml", str(xml_file)],
        capture_output=True, text=True
    )
    
    if result.returncode == 0:
        print(f"   ✅ 创建成功")
        return True
    else:
        print(f"   ❌ 创建失败: {result.stderr}")
        return False


def main():
    parser = argparse.ArgumentParser(description="设置 Windows 任务计划")
    parser.add_argument("--yes", "-y", action="store_true", help="跳过确认直接创建")
    args = parser.parse_args()
    
    script_dir = Path(__file__).parent
    python_exe = sys.executable
    pythonw_exe = python_exe.replace("python.exe", "pythonw.exe")
    
    print("=" * 60)
    print("🔧 设置 Windows 任务计划")
    print("=" * 60)
    print()
    print("将创建以下定时任务：")
    print("  1. 📥 每天 00:05 - 自动下载聊天记录")
    print("  2. 🗑️ 每天 23:30 - 自动删除聊天记录")
    print()
    print("⚠️ 需要管理员权限")
    print()
    
    if not args.yes:
        response = input("是否继续？(y/n): ")
        if response.lower() != 'y':
            print("已取消")
            return
    
    # 创建两个任务
    success1 = create_download_task(script_dir, pythonw_exe)
    success2 = create_cleanup_task(script_dir, pythonw_exe)
    
    print()
    print("=" * 60)
    if success1 and success2:
        print("✅ 所有任务创建成功！")
    else:
        print("⚠️ 部分任务创建失败，请以管理员身份重新运行")
    print("=" * 60)
    print()
    print("管理命令：")
    print('  查看下载任务: schtasks /query /tn "QQ群聊天记录自动下载"')
    print('  查看清理任务: schtasks /query /tn "QQ群聊天记录自动清理"')
    print('  手动运行下载: schtasks /run /tn "QQ群聊天记录自动下载"')
    print('  手动运行清理: schtasks /run /tn "QQ群聊天记录自动清理"')


if __name__ == "__main__":
    main()
