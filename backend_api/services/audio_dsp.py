import os
import librosa
import numpy as np
from mutagen import File as MutagenFile
from mutagen.id3 import ID3
from mutagen.flac import FLAC
from mutagen.mp4 import MP4, MP4Cover
from PIL import Image
import io
import shutil
import hashlib

# 动态获取 covers 目录
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(CURRENT_DIR))
COVERS_DIR = os.path.join(PROJECT_ROOT, "data_storage", "output", "covers")
os.makedirs(COVERS_DIR, exist_ok=True)

COVER_SIZE = (400, 400) # 统一压缩尺寸

def extract_and_optimize_cover(cover_data, fallback_title):
    """
    统一的物理级封面去重引擎 (和 batch_extractor 完全一致)
    接收二进制图片数据，计算 MD5，压缩保存，返回 URL
    """
    if not cover_data:
        # 如果没有提取到二进制数据，返回极客风格占位图
        return f"https://ui-avatars.com/api/?name={fallback_title}&background=0D0D12&color=00FFCC&size=300"
        
    try:
        # 🚨 终极核武器：直接对图片字节流求 MD5，实现 100% 物理级去重
        image_hash = hashlib.md5(cover_data).hexdigest()[:16]
        save_filename = f"cov_{image_hash}.jpg"
        save_path = os.path.join(COVERS_DIR, save_filename)
        
        cover_url = f"http://127.0.0.1:8000/covers/{save_filename}"
        
        # 💡 如果这张图以前存过（不管歌名是不是一样），直接跳过压缩写入，秒回 URL！
        if os.path.exists(save_path):
            return cover_url
            
        # 如果没存过，进行标准化的缩放与有损压缩
        image = Image.open(io.BytesIO(cover_data))
        if image.mode in ('RGBA', 'P'): 
            image = image.convert('RGB')
        
        image = image.resize(COVER_SIZE, Image.Resampling.LANCZOS)
        image.save(save_path, 'JPEG', quality=85)
        
        return cover_url
        
    except Exception as e:
        print(f"⚠️ 封面处理异常: {e}")
        return f"https://ui-avatars.com/api/?name={fallback_title}&background=0D0D12&color=00FFCC&size=300"

def process_audio_file(file_obj, temp_dir, db_centroids):
    """处理单个音频文件流，返回严密的数据结构"""
    safe_filename = os.path.basename(file_obj.filename)
    temp_file_path = os.path.join(temp_dir, safe_filename)
    
    # 1. 保存文件流到临时目录
    with open(temp_file_path, "wb") as buffer:
        shutil.copyfileobj(file_obj.file, buffer)
        
    # 2. 剥离元数据与原始图片二进制流
    title, artist, album, track_num = "Unknown", "Unknown Artist", "Unknown Album", 1
    cover_data = None
    
    try:
        audio = MutagenFile(temp_file_path)
        if audio:
            tags = audio.tags if hasattr(audio, 'tags') and audio.tags else audio
            
            if 'TIT2' in tags: title = str(tags['TIT2'].text[0])
            elif 'title' in tags: title = str(tags['title'][0])
            if 'TPE1' in tags: artist = str(tags['TPE1'].text[0])
            elif 'artist' in tags: artist = str(tags['artist'][0])
            if 'TALB' in tags: album = str(tags['TALB'].text[0])
            elif 'album' in tags: album = str(tags['album'][0])
            
            track_raw = ""
            if 'TRCK' in tags: track_raw = str(tags['TRCK'].text[0])
            elif 'tracknumber' in tags: track_raw = str(tags['tracknumber'][0])
            if track_raw:
                try: track_num = int(track_raw.split('/')[0])
                except: pass

            # 兼容读取二进制封面
            if hasattr(audio, 'pictures') and audio.pictures:
                cover_data = audio.pictures[0].data 
            elif isinstance(audio, ID3) or (hasattr(audio, 'tags') and isinstance(audio.tags, ID3)):
                id3_tags = audio if isinstance(audio, ID3) else audio.tags
                for tag in id3_tags.values():
                    if tag.FrameID == 'APIC':
                        cover_data = tag.data
                        break
            elif tags and 'covr' in tags:
                cover_item = tags['covr'][0]
                cover_data = bytes(cover_item) if hasattr(cover_item, '__class__') and cover_item.__class__.__name__ == 'MP4Cover' else cover_item
    except Exception:
        pass
        
    if title == "Unknown": title = os.path.splitext(safe_filename)[0]
    
    # 3. 🎯 调用统一封面引擎，获取去重后的封面 URL
    cover_url = extract_and_optimize_cover(cover_data, title)

    # 4. DSP 信号处理
    y, sr = librosa.load(temp_file_path, sr=22050, duration=30.0)
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=20)
    mfcc_mean = np.mean(mfcc.T, axis=0)
    
    radar_vector = mfcc_mean[:6].tolist()
    mfcc_vector = mfcc_mean.tolist()
    
    # 5. 质心分类推断
    predicted_genre = "Unknown"
    genre_avg = [0]*6
    if db_centroids:
        min_distance = float('inf')
        for genre_name, centroid_vector in db_centroids.items():
            dist = np.linalg.norm(np.array(mfcc_vector) - np.array(centroid_vector))
            if dist < min_distance:
                min_distance = dist
                predicted_genre = genre_name
        genre_avg = db_centroids.get(predicted_genre)[:6]

    if os.path.exists(temp_file_path): os.remove(temp_file_path)
        
    # 📦 统一输出结构
    return {
        "track_num": track_num,
        "title": title,
        "artist": artist,
        "album": album,
        "genre": predicted_genre,
        "bpm": float(tempo[0]),
        "mfcc_vector": mfcc_vector,
        "radar_vector": radar_vector,
        "genre_avg": genre_avg,
        "cover_url": cover_url, 
        "ai_review": f"基于真实空间距离测算：该轨道的 20 维声学向量矩阵，距离【{predicted_genre}】的数字质心最近，已为您进行自动归类。"
    }