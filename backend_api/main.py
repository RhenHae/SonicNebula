# backend_api/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import json
import os
import numpy as np

# 1. 初始化 FastAPI 实例
app = FastAPI(
    title="SonicNebula API Core",
    description="为音景星云前端大屏提供数据的核心驱动接口",
    version="1.0.0"
)

# 2. 跨域配置 (CORS) - 极其重要！
# 因为你的 Vue 前端在 localhost:5173，FastAPI 在 localhost:8000
# 没有这个配置，浏览器会拦截所有请求（CORS 报错）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # 开发阶段允许所有源，生产环境需改写
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. 动态路径寻址器 (保证去 data_lake 拿数据的准确性)
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
DATA_LAKE_DIR = os.path.join(PROJECT_ROOT, "data_storage", "data_lake")

# 4. 全局数据中心 (Singleton 模式，应用启动时加载，避免每次请求都读硬盘)
class DataCenter:
    def __init__(self):
        self.df = None
        self.centroids = None
        self.load_data()

    def load_data(self):
        csv_path = os.path.join(DATA_LAKE_DIR, "dashboard_data.csv")
        json_path = os.path.join(DATA_LAKE_DIR, "genre_centroids.json")
        
        try:
            if os.path.exists(csv_path) and os.path.exists(json_path):
                # 读取 CSV 时，把所有的 NaN (空值) 替换掉，否则转 JSON 时会引发前端解析错误
                self.df = pd.read_csv(csv_path).replace({np.nan: "Unknown"})
                self.df['cluster_id'] = self.df['cluster_id'].astype(str)
                
                with open(json_path, 'r', encoding='utf-8') as f:
                    self.centroids = json.load(f)
                print("✅ 🚀 DataCenter: 数据湖缓存已全部装载至内存！")
            else:
                print("⚠️ ⚠️ DataCenter: 找不到数据文件，请确认 Spark 任务已执行。")
        except Exception as e:
            print(f"❌ DataCenter 初始化灾难性失败: {e}")

# 实例化数据中心
db = DataCenter()


# ==========================================
# 📌 5. 定义 RESTful API 路由 (给前端调用的接口)
# ==========================================

@app.get("/")
async def root():
    return {"status": "online", "message": "SonicNebula Backend is running!"}

@app.get("/api/nebula_points")
async def get_nebula_points():
    """
    【接口一】为前端的 2.5D 星云图提供全量坐标点数据
    """
    if db.df is None:
        raise HTTPException(status_code=500, detail="Database not loaded")
    
    # 为了保证前端加载速度，只提取画图必须的字段
    needed_cols =['file_name', 'title', 'artist', 'true_genre', 'cluster_id', 'x', 'y', 'star_size', 'bpm']
    
    # 将 DataFrame 转化为给前端的 JSON 列表:[{"title": "xxx", "x": 1.2}, ...]
    records = db.df[needed_cols].to_dict(orient='records')
    
    return {
        "count": len(records),
        "points": records
    }

@app.get("/api/song_detail/{song_title}")
async def get_song_detail(song_title: str):
    """
    【接口二】前端点击某颗星星（某首歌）后，获取它的深入分析雷达数据
    """
    if db.df is None:
        raise HTTPException(status_code=500, detail="Database not loaded")
    
    # 在内存中检索这首歌
    song_row = db.df[db.df['title'] == song_title]
    if song_row.empty:
        raise HTTPException(status_code=404, detail="Song not found in the universe")
    
    song_data = song_row.iloc[0]
    genre = song_data['true_genre']
    
    # 提取雷达图所需的 6 维 MFCC (提取 mfcc_1 到 mfcc_6)
    radar_cols =[f"mfcc_{i}" for i in range(1, 7)]
    song_radar = song_data[radar_cols].tolist()
    
    # 获取该流派的质心平均值（也只取前 6 维作对比）
    genre_centroid_radar = db.centroids.get(genre, [0]*20)[:6]
    
    # 构建结构化的响应报文
    response = {
        "title": song_data['title'],
        "artist": song_data['artist'],
        "genre": genre,
        "bpm": song_data['bpm'],
        "cluster_id": song_data['cluster_id'],
        "purity_score": round(song_data['purity_score'], 1),
        "radar_data": {
            "categories":['能量密度', '音色明暗', '频谱质心', '粗糙度', '中频厚度', '高频泛音'],
            "song_values": song_radar,
            "genre_avg_values": genre_centroid_radar
        }
    }
    
    return response

@app.get("/api/filters")
async def get_filters():
    """
    【接口三】给前端下拉选择框提供选项：包含所有存在流派的列表
    """
    if db.df is None:
        return {"genres": []}
    
    # 去重并排序
    genres = sorted(db.df['true_genre'].unique().tolist())
    return {"genres": genres}