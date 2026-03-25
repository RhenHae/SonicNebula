import os
import sys
from pyspark.sql import SparkSession
import warnings

# =============================================================================
# 🔥 关键修复 1: 强制指定 JDK 21 路径（覆盖系统环境变量）
# =============================================================================
JDK21_PATH = r"C:\Program Files\Eclipse Adoptium\jdk-21.0.6.7-hotspot"
os.environ['JAVA_HOME'] = JDK21_PATH
os.environ['PATH'] = os.path.join(JDK21_PATH, 'bin') + os.pathsep + os.environ.get('PATH', '')

# 忽略警告
warnings.filterwarnings('ignore')

def run_etl_pipeline():
    # 设定输入输出路径
    INPUT_CSV = "././data_storage/output/music_features.csv"
    OUTPUT_PARQUET_DIR = "././data_storage/data_lake/features.parquet"
    
    if not os.path.exists(INPUT_CSV):
        print(f"❌ 找不到输入文件：{INPUT_CSV}")
        return

    print("🚀 [Step 1] 正在启动 Spark 引擎 (Local Mode)...")
    
    # =============================================================================
    # 🔥 关键修复 2: 添加网络绑定配置，解决 Gateway 卡住问题
    # =============================================================================
    spark = SparkSession.builder \
        .appName("SonicNebula_ETL") \
        .master("local[*]") \
        .config("spark.sql.execution.arrow.pyspark.enabled", "true") \
        .config("spark.driver.host", "127.0.0.1") \
        .config("spark.driver.bindAddress", "127.0.0.1") \
        .config("spark.network.timeout", "800s") \
        .config("spark.executor.heartbeatInterval", "200s") \
        .config("spark.ui.enabled", "false") \
        .config("spark.driver.maxResultSize", "1g") \
        .getOrCreate()
        
    # 把冗长的日志静音，只显示报错
    spark.sparkContext.setLogLevel("ERROR")

    print(f"📥 [Step 2] 正在加载 CSV 数据：{INPUT_CSV} ...")
    
    # 读取 CSV，让 Spark 自动推断列的类型
    df = spark.read.csv(INPUT_CSV, header=True, inferSchema=True)
    
    # 打印出数据总量
    total_rows = df.count()
    print(f"📊 成功读取 {total_rows} 条记录！")
    
    # 打印 Schema
    print("\n🔍 数据结构 (Schema) 概览:")
    df.printSchema()

    # 简单清洗：过滤掉那些可能有空值 (Null) 的行
    clean_df = df.dropna()
    clean_count = clean_df.count()
    
    if clean_count < total_rows:
        print(f"🧹 数据清洗：已剔除 {total_rows - clean_count} 条包含空值的不良数据。")

    print(f"\n🔄 [Step 3] 正在执行 ETL: 转换为 Parquet 列式存储...")
    
    # 确保存储目录存在
    os.makedirs("./data_lake", exist_ok=True)
    
    # 写入 Parquet
    clean_df.coalesce(1).write.mode("overwrite").parquet(OUTPUT_PARQUET_DIR)

    print(f"✅ ETL 任务大功告成！")
    print(f"📁 大数据资产已落地至：{OUTPUT_PARQUET_DIR}")
    
    # 优雅地关闭 Spark
    spark.stop()

if __name__ == "__main__":
    run_etl_pipeline()