import os
import json
import numpy as np
import pandas as pd
from scipy.spatial.distance import cosine
from pyspark.sql import SparkSession
from pyspark.ml.feature import VectorAssembler, StandardScaler
from pyspark.ml.clustering import KMeans
from sklearn.manifold import TSNE
import warnings

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)

warnings.filterwarnings('ignore')

def run_ml_engine():
    print("🧠[Step 1] 启动 Spark MLlib 引擎...")
    spark = SparkSession.builder.appName("SonicNebula_MLEngine").master("local[*]").getOrCreate()
    spark.sparkContext.setLogLevel("ERROR")

    # 1. 加载数据
    INPUT_PARQUET = os.path.join(PROJECT_ROOT, "data_lake", "features.parquet")
    if not os.path.exists(INPUT_PARQUET):
        print(f"❌ 找不到 {INPUT_PARQUET}")
        return
        
    df = spark.read.parquet(INPUT_PARQUET)
    
    # 2. 融合特征与标准化
    feature_cols = ["bpm"] +[f"mfcc_{i}" for i in range(1, 21)]
    assembler = VectorAssembler(inputCols=feature_cols, outputCol="raw_features")
    df_vectorized = assembler.transform(df)
    
    scaler = StandardScaler(inputCol="raw_features", outputCol="scaled_features", withStd=True, withMean=True)
    df_scaled = scaler.fit(df_vectorized).transform(df_vectorized)

    # 3. K-Means 聚类
    print("🌌 [Step 2] 执行 K-Means 聚类...")
    kmeans = KMeans(featuresCol="scaled_features", predictionCol="cluster_id", k=10, seed=42)
    df_clustered = kmeans.fit(df_scaled).transform(df_scaled)

    # =========================================================================
    # 🚀 架构大升级：将所有前端计算前置到这里 (Pre-computation)
    # =========================================================================
    print("🔭 [Step 3] 提取全量数据至内存，开始高阶指标预计算...")
    
    # 把所有需要的列一次性全拉出来 (包括 MFCC 1-20)
    mfcc_cols = [f"mfcc_{i}" for i in range(1, 21)]
    select_cols =["file_name", "title", "artist", "true_genre", "bpm", "cluster_id", "scaled_features"] + mfcc_cols
    pandas_df = df_clustered.select(select_cols).toPandas()

    # A. t-SNE 降维
    print("🌀 正在执行 t-SNE 降维...")
    features_array = np.array(pandas_df["scaled_features"].tolist())
    tsne = TSNE(n_components=3, random_state=42, perplexity=30)
    tsne_results = tsne.fit_transform(features_array)
    pandas_df['x'] = tsne_results[:, 0]
    pandas_df['y'] = tsne_results[:, 1]
    pandas_df['z'] = tsne_results[:, 2]

    # B. 伪 3D 视觉参数预计算 (解放前端算力)
    print("✨ 预计算视觉深度参数...")
    z_min, z_max = pandas_df['z'].min(), pandas_df['z'].max()
    # 直接算好星星尺寸
    pandas_df['star_size'] = ((pandas_df['z'] - z_min) / (z_max - z_min + 1e-8)) * 12 + 2

    # C. 流派质心与纯血度预计算 (彻底免除前端矩阵运算)
    print("🧬 预计算流派声学质心与单曲纯血度...")
    genre_centroids = {}
    purity_scores = []
    
    # 计算每个流派的平均 MFCC
    for genre in pandas_df['true_genre'].unique():
        genre_df = pandas_df[pandas_df['true_genre'] == genre]
        # 存为 list，方便写入 JSON
        genre_centroids[genre] = genre_df[mfcc_cols].mean().values.tolist()

    # 计算每首歌的纯血度
    for idx, row in pandas_df.iterrows():
        genre = row['true_genre']
        song_vec = row[mfcc_cols].values.astype(float)
        centroid_vec = np.array(genre_centroids[genre])
        
        # 使用 scipy 计算余弦相似度 (1 - cosine_distance = cosine_similarity)
        sim = 1 - cosine(song_vec, centroid_vec)
        purity = max(0, min(100, sim * 100))
        purity_scores.append(purity)
        
    pandas_df['purity_score'] = purity_scores

    # 清理无用列
    final_df = pandas_df.drop(columns=['scaled_features', 'z']) # z已经转成size了，可以丢弃节省空间

    # =========================================================================
    # 💾 数据落地：产出两份“熟食”数据
    # =========================================================================
    OUT_CSV = os.path.join(PROJECT_ROOT, "data_lake", "dashboard_data.csv")
    OUT_JSON = os.path.join(PROJECT_ROOT, "data_lake", "genre_centroids.json")
    
    print(f"💾 正在输出前端缓存数据...")
    final_df.to_csv(OUT_CSV, index=False, encoding='utf-8-sig')
    
    with open(OUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(genre_centroids, f, ensure_ascii=False, indent=2)

    print("✅ 后台数据引擎执行完毕！前端可以直接光速读取了！")
    spark.stop()

if __name__ == "__main__":
    run_ml_engine()