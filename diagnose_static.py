# diagnose_static.py
import os

# 项目根目录
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# 实际文件位置
ACTUAL_COVERS_DIR = os.path.join(PROJECT_ROOT, "data_storage", "output", "covers")

# 测试文件
TEST_FILE = "cov_21845fc420ea8ae5.jpg"
TEST_FILE_PATH = os.path.join(ACTUAL_COVERS_DIR, TEST_FILE)

print("=" * 60)
print("🔍 StaticFiles 路径诊断")
print("=" * 60)
print(f"\n📁 路径信息:")
print(f"   PROJECT_ROOT: {PROJECT_ROOT}")
print(f"   ACTUAL_COVERS_DIR: {ACTUAL_COVERS_DIR}")
print(f"   ACTUAL_COVERS_DIR 存在：{os.path.exists(ACTUAL_COVERS_DIR)}")
print(f"\n🖼️ 测试文件:")
print(f"   文件名：{TEST_FILE}")
print(f"   完整路径：{TEST_FILE_PATH}")
print(f"   文件存在：{os.path.exists(TEST_FILE_PATH)}")

if os.path.exists(TEST_FILE_PATH):
    print(f"   文件大小：{os.path.getsize(TEST_FILE_PATH)} bytes")
else:
    # 搜索文件
    print(f"\n🔍 搜索文件...")
    for root, dirs, files in os.walk(os.path.join(PROJECT_ROOT, "data_storage")):
        if TEST_FILE in files:
            print(f"   ✅ 找到文件：{os.path.join(root, TEST_FILE)}")
            break

# 列出 covers 目录内容
if os.path.exists(ACTUAL_COVERS_DIR):
    files = os.listdir(ACTUAL_COVERS_DIR)
    print(f"\n📋 covers 文件夹内容 (前 10 个):")
    for f in files[:10]:
        print(f"   - {f}")