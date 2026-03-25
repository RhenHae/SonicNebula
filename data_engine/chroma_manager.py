# chroma_manager.py
import chromadb
import pandas as pd
import os
import math
import hashlib # 💡 新增，用于兜底生成 hash

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
CHROMA_DB_PATH = os.path.join(PROJECT_ROOT, "data_storage", "chroma_db")

# 🔑 读取 Spark 处理过的高级数据
DASHBOARD_CSV = os.path.join(PROJECT_ROOT, "data_storage", "data_lake", "dashboard_data.csv")

def generate_song_hash(title, artist, album):
    """防撞车兜底哈希生成器"""
    raw_str = f"{str(title).lower().strip()}|{str(artist).lower().strip()}|{str(album).lower().strip()}"
    return hashlib.md5(raw_str.encode('utf-8')).hexdigest()[:16]

def init_vector_db():
    print("🧠 正在启动 ChromaDB 向量记忆引擎...")

    if not os.path.exists(DASHBOARD_CSV):
        print(f"❌ 找不到数据文件：{DASHBOARD_CSV}")
        return

    # 1. 实例化本地 ChromaDB 客户端
    client = chromadb.PersistentClient(path=CHROMA_DB_PATH)

    # 2. 获取或创建集合
    collection = client.get_or_create_collection(
        name="sonic_nebula",
        metadata={"hnsw:space": "l2"} 
    )

    # 每次运行前清空旧数据
    if collection.count() > 0:
        print("🧹 检测到旧的向量索引，正在清空重建...")
        client.delete_collection(name="sonic_nebula")
        collection = client.create_collection(name="sonic_nebula", metadata={"hnsw:space": "l2"})

    # 3. 读取数据
    print("📥 正在读取结构化音频特征与元数据...")
    df = pd.read_csv(DASHBOARD_CSV)

    # 🔑 修复：统一使用 cover_url
    if 'cover_url' in df.columns:
        cover_col = 'cover_url'
        print("✅ 检测到 cover_url 列")
    elif 'cover_path' in df.columns:
        cover_col = 'cover_path'
        print("⚠️ 检测到 cover_path 列（建议统一为 cover_url）")
    else:
        cover_col = None
        print("⚠️ 未检测到封面列，将使用空值")

    df = df.fillna("")

    ids = []
    embeddings = []
    metadatas =[]

    # 4. 数据转换与组装
    print(f"🔄 正在将 {len(df)} 首歌曲转化为高维空间向量...")
    mfcc_cols =[f"mfcc_{i}" for i in range(1, 21)]

    for idx, row in df.iterrows():
        # 💡 核心修复 1：提取或生成 hash_id
        hash_id = str(row['hash_id']) if 'hash_id' in row and str(row['hash_id']) != "" else generate_song_hash(row['title'], row['artist'], row['album'])
        
        # 保证插入 ChromaDB 的主键绝对唯一
        song_id = f"ID{idx}_{hash_id}"
        ids.append(song_id)
        
        vector = row[mfcc_cols].values.astype(float).tolist()
        vector =[0.0 if math.isnan(v) or math.isinf(v) else v for v in vector]
        embeddings.append(vector)
        
        cover_value = str(row[cover_col]) if cover_col and cover_col in row else ""
        
        # 💡 核心修复 2：严格对齐 main.py 中要求的 Metadata 结构
        metadatas.append({
            "hash_id": hash_id,
            "file_name": str(row.get('file_name', '')),
            "title": str(row['title']),
            "artist": str(row['artist']),
            "album": str(row['album']) if not pd.isna(row['album']) else "未知专辑",
            "genre": str(row['true_genre']),
            "cluster_id": str(row['cluster_id']),
            "purity_score": float(row['purity_score']) if 'purity_score' in row and str(row['purity_score']) != "" else 0.0,
            "cover_url": cover_value
        })

    # 5. 分批写入 ChromaDB
    print("💾 正在向 ChromaDB 注入记忆...")
    BATCH_SIZE = 500
    for i in range(0, len(ids), BATCH_SIZE):
        batch_ids = ids[i:i+BATCH_SIZE]
        batch_embeddings = embeddings[i:i+BATCH_SIZE]
        batch_metadatas = metadatas[i:i+BATCH_SIZE]
        
        collection.add(
            ids=batch_ids,
            embeddings=batch_embeddings,
            metadatas=batch_metadatas
        )
        print(f"   已写入 {min(i+BATCH_SIZE, len(ids))} / {len(ids)} 条记录...")

    print(f"🎉 成功！高维空间检索矩阵已建立。当前库容量：{collection.count()} 首。")

if __name__ == "__main__":
    init_vector_db()