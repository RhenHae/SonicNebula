from fastapi import FastAPI, HTTPException, UploadFile, File, Body, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import List, Optional
import pandas as pd
import json
import os
import numpy as np
import logging
import hashlib
import uuid
import math
import random
import asyncio
from datetime import datetime
from pydantic import BaseModel

try:
    import chromadb
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False
    print("⚠️ ChromaDB 未安装，推荐功能将受限")

from backend_api.services.audio_dsp import process_audio_file

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(title="SonicNebula API Core", version="3.0.0")

app.add_middleware(
    CORSMiddleware, 
    allow_origins=["*"], 
    allow_credentials=True, 
    allow_methods=["*"], 
    allow_headers=["*"],
)

# ==================== 路径配置 ====================
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
DATA_LAKE_DIR = os.path.join(PROJECT_ROOT, "data_storage", "data_lake")
CHROMA_DB_DIR = os.path.join(PROJECT_ROOT, "data_storage", "chroma_db")
COVERS_DIR = os.path.join(PROJECT_ROOT, "data_storage", "output", "covers")
TEMP_DIR = os.path.join(PROJECT_ROOT, "data_storage", "tmp_processing")


# 🔑 添加调试日志
logger.info(f"🔍 StaticFiles 配置:")
logger.info(f"   CURRENT_DIR: {CURRENT_DIR}")
logger.info(f"   PROJECT_ROOT: {PROJECT_ROOT}")
logger.info(f"   COVERS_DIR: {COVERS_DIR}")
logger.info(f"   COVERS_DIR 存在：{os.path.exists(COVERS_DIR)}")
logger.info(f"   COVERS_DIR 内容：{os.listdir(COVERS_DIR)[:5]}")

for dir_path in[DATA_LAKE_DIR, CHROMA_DB_DIR, COVERS_DIR, TEMP_DIR]:
    os.makedirs(dir_path, exist_ok=True)

app.mount("/covers", StaticFiles(directory=COVERS_DIR), name="covers")

# ==================== 数据模型 ====================
class GenreCorrection(BaseModel):
    title: str
    artist: Optional[str] = None
    corrected_genre: str

# ==================== 数据中心 ====================
class DataCenter:
    def __init__(self):
        self.df = None
        self.centroids = None
        self.chroma_collection = None
        self.csv_path = os.path.join(DATA_LAKE_DIR, "dashboard_data.csv")
        self.load_data()

    def load_data(self):
        # 1. 加载 CSV
        try:
            if os.path.exists(self.csv_path):
                self.df = pd.read_csv(self.csv_path).replace({np.nan: "Unknown"})
                logger.info(f"✅ DataCenter: CSV 数据装载完毕 ({len(self.df)} 首歌曲)")
            else:
                logger.warning(f"⚠️ DataCenter: 未找到 CSV 文件 {self.csv_path}")
        except Exception as e:
            logger.error(f"❌ DataCenter: CSV 加载失败 - {e}")
        
        # 2. 加载质心
        try:
            json_path = os.path.join(DATA_LAKE_DIR, "genre_centroids.json")
            if os.path.exists(json_path):
                with open(json_path, 'r', encoding='utf-8') as f:
                    self.centroids = json.load(f)
        except Exception as e:
            logger.error(f"❌ DataCenter: 质心加载失败 - {e}")
        
        # 3. 连接 ChromaDB
        if CHROMA_AVAILABLE:
            try:
                if os.path.exists(CHROMA_DB_DIR):
                    client = chromadb.PersistentClient(path=CHROMA_DB_DIR)
                    self.chroma_collection = client.get_or_create_collection(name="sonic_nebula", metadata={"hnsw:space": "l2"})
                    logger.info(f"✅ DataCenter: ChromaDB 连接成功 ({self.chroma_collection.count()} 条向量)")
            except Exception as e:
                logger.error(f"❌ DataCenter: ChromaDB 连接失败 - {e}")

    def save_csv(self):
        if self.df is None: return False
        try:
            self.df.to_csv(self.csv_path, index=False, encoding='utf-8-sig')
            logger.info(f"💾 CSV 已持久化 ({len(self.df)} 行)")
            return True
        except Exception as e:
            logger.error(f"❌ CSV 保存失败：{e}")
            return False

db = DataCenter()

# ==================== 工具函数 ====================
def generate_song_hash(title: str, artist: str, album: str) -> str:
    """生成全局统一的歌曲防重哈希 (与 batch_extractor.py 完全一致)"""
    raw_str = f"{str(title).lower().strip()}|{str(artist).lower().strip()}|{str(album).lower().strip()}"
    return hashlib.md5(raw_str.encode('utf-8')).hexdigest()[:16]

@app.on_event("startup")
async def startup_cleanup():
    try:
        if os.path.exists(TEMP_DIR):
            for filename in os.listdir(TEMP_DIR):
                file_path = os.path.join(TEMP_DIR, filename)
                if os.path.isfile(file_path): os.remove(file_path)
    except: pass

# =====================================================================
# 🚀 1. 核心：音频实时分析与入库接口 (优化版)
# =====================================================================
@app.post("/api/analyze_audio")
async def analyze_audio_batch(files: List[UploadFile] = File(...)):
    if not files:
        raise HTTPException(status_code=400, detail="未检测到音频")
    os.makedirs(TEMP_DIR, exist_ok=True)
    
    analyzed_tracks = []
    error_files = []
    
    for idx, file in enumerate(files):
        try:
            # 🔑 步骤 1: 先完整分析（保持原有逻辑）
            track_data = process_audio_file(file, TEMP_DIR, db.centroids)
            
            title = track_data['title']
            artist = track_data['artist']
            album = track_data['album']
            track_num = track_data['track_num']
            
            if db.df is not None and db.chroma_collection is not None:
                # 🚨 终极统一：使用相同的哈希算法查重
                song_hash = generate_song_hash(title, artist, album)
                existing_mask = (db.df['hash_id'] == song_hash)
                
                if not existing_mask.any():
                    # 💡 A. 新歌：拼装新行数据，追加到 Pandas 内存表
                    new_row = {
                        "hash_id": song_hash,
                        "file_name": file.filename,
                        "title": title,
                        "artist": artist,
                        "album": album,
                        "track_num": int(track_num) if track_num else 0,
                        "true_genre": track_data['genre'],
                        "bpm": float(track_data['bpm']),
                        "cover_url": track_data['cover_url'],
                        "cluster_id": "99", 
                        "x": random.uniform(-30, 30),
                        "y": random.uniform(-30, 30),
                        "star_size": random.uniform(3, 8),
                        "purity_score": 0.0,
                    }
                    for i, val in enumerate(track_data['mfcc_vector']):
                        new_row[f"mfcc_{i+1}"] = float(val)
                    
                    # 对齐列结构
                    for col in db.df.columns:
                        if col not in new_row:
                            new_row[col] = None
                    
                    db.df = pd.concat([db.df, pd.DataFrame([new_row])], ignore_index=True)
                    logger.info(f"✨ [数据湖注入] 新歌 {title} 已加入内存表")
                    
                    # 💡 B. 注入 ChromaDB (带唯一 ID)
                    unique_chroma_id = f"UPL_{song_hash}_{str(uuid.uuid4())[:8]}"
                    db.chroma_collection.add(
                        ids=[unique_chroma_id],
                        embeddings=[track_data['mfcc_vector']],
                        metadatas=[{
                            "hash_id": song_hash,
                            "title": title,
                            "artist": artist, 
                            "album": album,
                            "genre": track_data['genre'], 
                            "cover_url": track_data['cover_url'],
                            "file_name": file.filename
                        }]
                    )
                    logger.info(f"🧠 [向量记忆] 新歌 {title} 已写入 ChromaDB")
                    db.save_csv()
                    
                    # 返回分析数据
                    analyzed_tracks.append(track_data)
                    
                else:
                    # 🔑 步骤 2: 歌曲已存在，返回数据库数据
                    logger.info(f"⚡ [查重拦截] 库中已存在 {title} - {artist}，返回数据库数据")
                    
                    existing_song = db.df[existing_mask].iloc[0]
                    
                    # 从数据库构建返回数据（保留用户修正的流派等）
                    db_track_data = {
                        "track_num": int(existing_song.get('track_num', track_num)),
                        "title": existing_song['title'],
                        "artist": existing_song['artist'],
                        "album": existing_song.get('album', album),
                        "genre": existing_song.get('true_genre', track_data['genre']),  # 🔑 保留修正后的流派
                        "bpm": float(existing_song.get('bpm', track_data['bpm'])),
                        "mfcc_vector": [float(existing_song.get(f'mfcc_{i+1}', 0)) for i in range(20)],
                        "radar_vector": [float(existing_song.get(f'mfcc_{i+1}', 0)) for i in range(6)],
                        "genre_avg": [float(existing_song.get(f'mfcc_{i+1}', 0)) for i in range(6)],
                        "cover_url": existing_song.get('cover_url', track_data['cover_url']),
                        "ai_review": f"【数据库缓存】该歌曲已于之前分析完成，流派为 {existing_song.get('true_genre', 'Unknown')}。"
                    }
                    
                    analyzed_tracks.append(db_track_data)
            else:
                # 数据库未就绪，直接返回分析数据
                analyzed_tracks.append(track_data)
            
        except Exception as e:
            error_files.append({"file": file.filename, "error": str(e)})
            logger.error(f"❌ 分析失败 {file.filename}: {e}")
    
    response = {"status": "success", "tracks": analyzed_tracks}
    if error_files:
        response["warnings"] = error_files
        response["status"] = "partial_success" if analyzed_tracks else "failed"
    return response

# =====================================================================
# 🌌 2. 星云坐标数据接口
# =====================================================================
@app.get("/api/nebula_points")
async def get_nebula_points():
    if db.df is None:
        raise HTTPException(status_code=500, detail="Data not loaded")
    needed_cols = ['hash_id', 'file_name', 'title', 'artist', 'album', 'track_num', 
                   'cover_url', 'true_genre', 'cluster_id', 'star_size', 'bpm', 'x', 'y', 'purity_score']
    available_cols = [c for c in needed_cols if c in db.df.columns]
    return {"points": db.df[available_cols].to_dict(orient='records')}

# =====================================================================
# 🔗 3. 向量推荐接口
# =====================================================================
@app.post("/api/recommend")
async def get_recommendations_by_vector(
    target_vector: List[float] = Body(...),
    title: str = Body(default="Unknown"),
    artist: Optional[str] = Body(default=None),
    genre: Optional[str] = Body(default=None),  # 🔑 新增：目标流派
    limit: int = Body(default=5)
):
    if db.chroma_collection is None:
        raise HTTPException(status_code=500, detail="Vector DB not initialized")
    if len(target_vector) != 20:
        raise HTTPException(status_code=400, detail="Invalid vector dimension. Must be 20.")
    
    try:
        # 🔑 多取一些用于流派过滤
        results = db.chroma_collection.query(
            query_embeddings=[target_vector],
            n_results=limit * 5,
            include=["metadatas", "distances"]
        )
        
        distances = results['distances'][0] if results['distances'] else []
        metadatas = results['metadatas'][0] if results['metadatas'] else []
        
        # 🔑 分离同流派和其他流派
        same_genre = []
        other_genre = []
        
        for i, meta in enumerate(metadatas):
            if meta.get('title') == title:
                continue
            
            item = {
                'meta': meta,
                'distance': distances[i] if i < len(distances) else 9999.0,
                'is_same_genre': meta.get('genre') == genre
            }
            
            if item['is_same_genre']:
                same_genre.append(item)
            else:
                other_genre.append(item)
        
        # 🔑 排序：都按距离排序
        same_genre.sort(key=lambda x: x['distance'])
        other_genre.sort(key=lambda x: x['distance'])
        
        # 🔑 70% 同流派 + 30% 其他流派
        same_count = int(limit * 0.7)
        other_count = limit - same_count
        
        final = same_genre[:same_count] + other_genre[:other_count]
        
        recommendations = []
        for item in final:
            meta = item['meta']
            distance = item['distance']
            
            true_dist = math.sqrt(distance) if distance > 0 else 0.0
            similarity_score = 100.0 / (1.0 + true_dist * 0.08)
            
            cover_url = meta.get('cover_url', '')
            if not cover_url:
                name = str(meta.get('title', 'UK'))[:2].upper()
                cover_url = f"https://ui-avatars.com/api/?name={name}&background=1a1a2e&color=00FFCC&size=100"
            
            recommendations.append({
                "id": str(random.randint(1000, 9999)),
                "title": meta.get('title', 'Unknown'),
                "artist": meta.get('artist', 'Unknown Artist'),
                "album": meta.get('album') or meta.get('album_name') or '未知专辑',
                "genre": meta.get('genre', 'Unknown'),
                "similarity": f"{similarity_score:.1f}%", 
                "cover_url": cover_url,
                "is_same_genre": item['is_same_genre']  # 🔑 标记是否同流派
            })
        
        logger.info(f"✅ 推荐完成：返回 {len(recommendations)} 首 (同流派：{len(same_genre)}, 其他：{len(other_genre)})")
        return {"recommendations": recommendations}
        
    except Exception as e:
        logger.error(f"❌ 推荐检索失败：{e}")
        raise HTTPException(status_code=500, detail=str(e))
    
# =====================================================================
# 🤖 4. AI 智能点评接口
# =====================================================================
@app.get("/api/ai_review")
async def get_ai_review(title: str, artist: Optional[str] = None):
    if db.df is None: raise HTTPException(status_code=500, detail="Database not loaded")
    
    song_idx = db.df.index[db.df['title'] == title].tolist()
    if not song_idx: raise HTTPException(status_code=404, detail=f"Song not found: {title}")
    
    row = db.df.iloc[song_idx[0]]
    genre = row.get('true_genre', 'Unknown')
    bpm = float(row.get('bpm', 0))
    
    await asyncio.sleep(random.uniform(1.0, 2.0))
    
    review_templates = {
        "Metal": f"系统嗅探到目标音频属于纯正的 **{genre}** 频段。强烈的吉他失真与密集的鼓点营造出极具冲击力的声场。BPM 稳定在 `{bpm:.0f}`，能量密度在副歌部分有显著跳跃。",
        "PostRock": f"典型的 **{genre}** 美学表达，通过动态对比与器乐层次构建出宏大的叙事空间。BPM `{bpm:.0f}` 的中速节奏适合沉浸式聆听，底层频域数据显示出极其克制的中频厚度。",
        "MidwestEMO": f"这首作品展现了复杂的和弦进行与情感充沛的即兴特质。BPM `{bpm:.0f}` 赋予了它独特的律动感。AI 建议您将其加入『赛博深夜』播放列表中。",
        "Shoegaze": f"警告：检测到强烈的低频下潜！这首 **{genre}** 轨道在信号处理上表现出迷幻的失真特征。虽然其节拍速率为 `{bpm:.0f}`，但其营造的『音墙 (Wall of Sound)』包裹感极强。",
        "Unknown": f"这首作品的声学特征游离于已知流派边界。BPM `{bpm:.0f}`，建议进一步分析 MFCC 特征向量以确定风格倾向。"
    }
    return {
        "status": "success", "title": title, "artist": artist,
        "review_text": review_templates.get(genre, f"该曲目具有明显的 {genre} 风格特征，BPM 为 {bpm:.0f}。")
    }

# =====================================================================
# 🛡️ 5. 人工修正与数据回流接口
# =====================================================================
@app.post("/api/correct_genre")
async def handle_genre_correction(correction: GenreCorrection):
    if db.chroma_collection is None or db.df is None: raise HTTPException(status_code=500, detail="Database not ready")
    
    # 💡 极其严谨的三级匹配查找
    song_idx = None
    matched_hash_id = None
    
    # 级别 1 & 2: title + artist 精确匹配
    song_idx_list = db.df.index[
        (db.df['title'].str.strip().str.lower() == correction.title.strip().lower()) &
        (db.df['artist'].str.strip().str.lower() == str(correction.artist).strip().lower())
    ].tolist()
    if song_idx_list:
        song_idx = song_idx_list[0]
        matched_hash_id = db.df.at[song_idx, 'hash_id']
    
    # 级别 3: 模糊匹配
    if song_idx is None:
        for idx, row in db.df.iterrows():
            if correction.title.strip().lower() in str(row['title']).strip().lower():
                song_idx = idx
                matched_hash_id = row['hash_id']
                break

    if song_idx is None: raise HTTPException(status_code=404, detail="Song not found")
    
    db.df.at[song_idx, 'true_genre'] = correction.corrected_genre
    
    # 🚨 终极安全合并机制：保留封面等所有属性，只改流派
    try:
        if matched_hash_id:
            results = db.chroma_collection.get(where={"hash_id": matched_hash_id}, include=["metadatas"])
            if results and results['metadatas']:
                target_id = results['ids'][0]
                old_meta = results['metadatas'][0]
                
                old_meta['genre'] = correction.corrected_genre
                
                db.chroma_collection.update(ids=[target_id], metadatas=[old_meta])
                logger.info(f"✅ ChromaDB Metadata 合并更新成功")
    except Exception as e:
        logger.warning(f"⚠️ ChromaDB 更新失败：{e}")

    db.save_csv()
    return {"status": "success", "message": "Genre updated successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

@app.get("/api/debug/check_song_cover")
def debug_check_song_cover(title: str = "帽子戏法"):
    """检查特定歌曲的封面数据"""
    if db.df is None:
        raise HTTPException(status_code=500, detail="Data not loaded")
    
    song_df = db.df[db.df['title'] == title]
    if song_df.empty:
        return {"error": "Song not found"}
    
    row = song_df.iloc[0]
    hash_id = row['hash_id']
    cover_url = row['cover_url']
    
    # 检查文件是否存在
    filename = cover_url.replace('http://127.0.0.1:8000/covers/', '')
    file_path = os.path.join(COVERS_DIR, filename)
    
    return {
        "title": title,
        "hash_id": hash_id,
        "cover_url": cover_url,
        "filename": filename,
        "file_exists": os.path.exists(file_path),
        "file_path": file_path,
        "wrong_url_example": f"http://127.0.0.1:8000/covers/cov_{hash_id}.jpg"
    }