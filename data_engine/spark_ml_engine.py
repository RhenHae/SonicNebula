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

warnings.filterwarnings('ignore')

def run_ml_engine():
    print("🧠 [Step 1] 启动 Spark MLlib 引擎...")
    spark = SparkSession.builder.appName("SonicNebula_MLEngine").master("local[*]").getOrCreate()
    spark.sparkContext.setLogLevel("ERROR")

    # 1. 加载数据
    INPUT_PARQUET = "./data_storage/data_lake/features.parquet"
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
    # 🚀 架构大升级：将所有前端需要的数据全量放行！(Data Pipeline Passthrough)
    # =========================================================================
    print("🔭 [Step 3] 提取全量数据至内存，开始高阶指标预计算...")
    
    mfcc_cols = [f"mfcc_{i}" for i in range(1, 21)]
    
    # 💡 【核心修复】：把 hash_id, album, track_num, cover_url 全部加进来！一个都不能少！
    select_cols =[
        "hash_id", "file_name", "title", "artist", "album", "track_num", 
        "true_genre", "bpm", "cover_url", "cluster_id", "scaled_features"
    ] + mfcc_cols
    
    pandas_df = df_clustered.select(select_cols).toPandas()

    # A. t-SNE 降维
    print("🌀 正在执行 t-SNE 降维...")
    features_array = np.array(pandas_df["scaled_features"].tolist())
    tsne = TSNE(n_components=3, random_state=42, perplexity=30)
    tsne_results = tsne.fit_transform(features_array)
    pandas_df['x'] = tsne_results[:, 0]
    pandas_df['y'] = tsne_results[:, 1]
    pandas_df['z'] = tsne_results[:, 2]

    # B. 伪 3D 视觉参数预计算
    print("✨ 预计算视觉深度参数...")
    z_min, z_max = pandas_df['z'].min(), pandas_df['z'].max()
    pandas_df['star_size'] = ((pandas_df['z'] - z_min) / (z_max - z_min + 1e-8)) * 12 + 2

    # C. 流派质心与纯血度预计算
    print("🧬 预计算流派声学质心与单曲纯血度...")
    genre_centroids = {}
    purity_scores = []
    
    for genre in pandas_df['true_genre'].unique():
        genre_df = pandas_df[pandas_df['true_genre'] == genre]
        genre_centroids[genre] = genre_df[mfcc_cols].mean().values.tolist()

    for idx, row in pandas_df.iterrows():
        genre = row['true_genre']
        song_vec = row[mfcc_cols].values.astype(float)
        centroid_vec = np.array(genre_centroids[genre])
        
        sim = 1 - cosine(song_vec, centroid_vec)
        purity = max(0, min(100, sim * 100))
        purity_scores.append(purity)
        
    pandas_df['purity_score'] = purity_scores

    # 清理无用的 Spark 中间列
    final_df = pandas_df.drop(columns=['scaled_features', 'z'])

    # =========================================================================
    # 💾 数据落地
    # =====================================================================
    OUT_CSV = "./data_storage/data_lake/dashboard_data.csv"
    OUT_JSON = "./data_storage/data_lake/genre_centroids.json"
    
    print(f"💾 正在输出前端缓存数据...")
    final_df.to_csv(OUT_CSV, index=False, encoding='utf-8-sig')
    
    with open(OUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(genre_centroids, f, ensure_ascii=False, indent=2)

    print("✅ 后台数据引擎执行完毕！所有元数据均已完整保留！")
    spark.stop()

if __name__ == "__main__":
    run_ml_engine()