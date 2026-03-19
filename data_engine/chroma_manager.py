# data_engine/chroma_manager.py
import chromadb
import pandas as pd
import os

# 配置路径
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
# ChromaDB 数据库会存在这个文件夹里
CHROMA_DB_PATH = os.path.join(PROJECT_ROOT, "data_storage", "chroma_db")
FEATURES_CSV = os.path.join(PROJECT_ROOT, "data_storage", "output", "music_features.csv")

def init_vector_db():
    print("🧠 正在启动 ChromaDB 向量记忆引擎...")
    
    if not os.path.exists(FEATURES_CSV):
        print(f"❌ 找不到原始特征文件: {FEATURES_CSV}")
        return

    # 1. 实例化本地 ChromaDB 客户端
    client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    
    # 2. 获取或创建名为 'sonic_nebula' 的集合 (Collection)
    # 这里的 L2 代表使用 欧几里得距离 (Euclidean distance) 来计算相似度
    collection = client.get_or_create_collection(
        name="sonic_nebula",
        metadata={"hnsw:space": "l2"} 
    )

    # 检查库里是不是已经有数据了
    existing_count = collection.count()
    if existing_count > 0:
        print(f"✅ 向量库已存在，当前记录数: {existing_count}。如需覆盖，请先删除 chroma_db 文件夹。")
        return

    # 3. 读取 CSV 特征数据
    print("📥 正在读取原始音频特征...")
    df = pd.read_csv(FEATURES_CSV)
    
    # 准备批量插入的数组
    ids = []
    embeddings =[]
    metadatas =[]
    
    # 4. 数据转换与打包
    print(f"🔄 正在将 {len(df)} 首歌曲转化为高维空间向量...")
    mfcc_cols =[f"mfcc_{i}" for i in range(1, 21)]
    
    for idx, row in df.iterrows():
        # 唯一 ID (用歌名+歌手避免重复)
        # 用内置的 str 转换，并清除可能导致问题的特殊字符
        safe_filename = str(row['file_name']).replace(" ", "_")
        safe_artist = str(row['artist']).replace(" ", "_")
        song_id = f"ID{idx}_{safe_filename}::{safe_artist}"
        
        ids.append(song_id)
        
        # 提取 20 维 MFCC 作为该歌曲的 Embedding (嵌入向量)
        vector = row[mfcc_cols].values.astype(float).tolist()
        embeddings.append(vector)
        
        # 存储一些额外的元数据，方便前端展示
        metadatas.append({
            "title": row['title'],
            "artist": row['artist'],
            "genre": row['true_genre'],
            "bpm": float(row['bpm'])
        })

    # 5. 批量写入 ChromaDB
    print("💾 正在向 ChromaDB 注入记忆...")
    # 注意：ChromaDB 限制一次性插入太多可能会报错，1000条直接插没问题
    collection.add(
        ids=ids,
        embeddings=embeddings,
        metadatas=metadatas
    )
    
    print(f"🎉 成功！已有 {collection.count()} 首歌曲获得了空间向量坐标。")

if __name__ == "__main__":
    init_vector_db()