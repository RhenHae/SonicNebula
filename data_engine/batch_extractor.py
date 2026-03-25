import os
import glob
import librosa
import numpy as np
import pandas as pd
import warnings
import re
import hashlib
from mutagen import File as MutagenFile
from mutagen.id3 import ID3
from mutagen.flac import FLAC
from mutagen.mp4 import MP4, MP4Cover
from PIL import Image
import io
from tqdm import tqdm

warnings.filterwarnings('ignore')

# ==================== 1. 动态路径与常量配置 ====================
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)

AUDIO_DIR = os.path.join(PROJECT_ROOT, "data_storage", "raw_audio")
OUTPUT_CSV = os.path.join(PROJECT_ROOT, "data_storage", "output", "music_features.csv")
COVER_DIR = os.path.join(PROJECT_ROOT, "data_storage", "output", "covers") 

os.makedirs(COVER_DIR, exist_ok=True)
os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)

# 封面标准化尺寸
COVER_SIZE = (400, 400) 

# ==================== 2. 核心功能函数 ====================

def generate_song_hash(title, artist, album):
    """生成单曲唯一哈希（随歌曲标题变化）"""
    raw_str = f"{str(title).lower().strip()}|{str(artist).lower().strip()}|{str(album).lower().strip()}"
    return hashlib.md5(raw_str.encode('utf-8')).hexdigest()[:16]

def generate_album_hash(artist, album):
    """生成专辑唯一哈希（不随标题变化，用于封面去重）"""
    raw_str = f"{str(artist).lower().strip()}|{str(album).lower().strip()}"
    return hashlib.md5(raw_str.encode('utf-8')).hexdigest()[:16]

def extract_metadata(file_path, file_name):
    """智能提取元数据 (包含音轨序号)"""
    title, artist_str, album, track_num = "Unknown Title", "Unknown Artist", "Unknown Album", 1
    
    try:
        audio = MutagenFile(file_path, easy=True)
        if audio is not None:
            if 'title' in audio: title = audio['title'][0]
            if 'artist' in audio: artist_str = audio['artist'][0]
            if 'album' in audio: album = audio['album'][0]
            if 'tracknumber' in audio:
                track_raw = str(audio['tracknumber'][0])
                track_num = int(track_raw.split('/')[0]) if track_raw.split('/')[0].isdigit() else 1
    except Exception:
        pass

    if title == "Unknown Title":
        name_without_ext = os.path.splitext(file_name)[0]
        if " - " in name_without_ext:
            parts = name_without_ext.split(" - ", 1)
            artist_str = parts[0].strip()
            title = parts[1].strip()
        else:
            title = name_without_ext

    return title, artist_str, album, track_num

def split_artists(artist_str):
    """清洗并拆分多歌手字符串"""
    clean_str = re.sub(r'(?i)\s*feat\.\s*|\s*ft\.\s*|\s*&\s*|\s*,\s*|\s*/\s*|\s*;\s*', '、', artist_str)
    artists =[a.strip() for a in clean_str.split('、') if a.strip()]
    return artists if artists else ["Unknown Artist"]

def extract_and_optimize_cover(audio_path):
    """
    终极去重版：提取封面 -> 计算二进制内容的 MD5 -> 检查是否存在 -> 压缩保存
    返回图片保存的 URL 相对路径
    """
    try:
        audio = MutagenFile(audio_path)
        if audio is None: return ""

        cover_data = None
        # 兼容三种格式的封面提取
        if isinstance(audio, ID3) or (hasattr(audio, 'tags') and isinstance(audio.tags, ID3)):
            id3_tags = audio if isinstance(audio, ID3) else audio.tags
            for tag in id3_tags.values():
                if tag.FrameID == 'APIC':
                    cover_data = tag.data
                    break
        elif isinstance(audio, FLAC):
            if audio.pictures: cover_data = audio.pictures[0].data
        elif isinstance(audio, MP4):
            if 'covr' in audio:
                cover_item = audio['covr'][0]
                cover_data = bytes(cover_item) if isinstance(cover_item, MP4Cover) else cover_item

        # 🚨 终极核武器：基于图像真实二进制内容生成指纹！
        if cover_data:
            # 直接对图片字节流求 MD5
            image_hash = hashlib.md5(cover_data).hexdigest()[:16]
            save_filename = f"cov_{image_hash}.jpg"
            save_path = os.path.join(COVER_DIR, save_filename)
            
            # 💡 物理级去重：不管这首歌叫什么名字，只要图片长得一样（哈希相同），且已经存过，直接返回复用！
            if os.path.exists(save_path):
                return f"http://127.0.0.1:8000/covers/{save_filename}"
                
            # 如果是第一次见这张图，进行缩放、压缩并保存
            image = Image.open(io.BytesIO(cover_data))
            if image.mode in ('RGBA', 'P'): 
                image = image.convert('RGB')
            
            # 强制调整为 400x400 大小
            image = image.resize(COVER_SIZE, Image.Resampling.LANCZOS)
            
            # 保存为 85% 质量的 JPG，极大压缩体积
            image.save(save_path, 'JPEG', quality=85)
            
            return f"http://127.0.0.1:8000/covers/{save_filename}"
            
    except Exception as e:
        # print(f"封面处理异常: {e}")
        pass
        
    return "" # 提取失败返回空

# ==================== 3. 主处理流程 ====================
def process_batch():
    dataset =[]
    error_files =[]
    processed_hashes = set() 
    
    genres =[d for d in os.listdir(AUDIO_DIR) if os.path.isdir(os.path.join(AUDIO_DIR, d))]
    if not genres:
        print(f"⚠️ 找不到流派文件夹！请检查 {AUDIO_DIR} 目录结构。")
        return

    print(f"🚀 启动全量数据引擎... 共发现 {len(genres)} 个流派区块。")

    for genre in genres:
        genre_path = os.path.join(AUDIO_DIR, genre)
        audio_files =[]
        for ext in ('*.mp3', '*.wav', '*.flac', '*.m4a'):
            audio_files.extend(glob.glob(os.path.join(genre_path, ext)))
            
        print(f"\n🎧 正在深度测绘: {genre.upper()} (共 {len(audio_files)} 首)")
        
        for file_path in tqdm(audio_files, desc=f"Extracting {genre}"):
            file_name = os.path.basename(file_path)
            
            try:
                title, artist_str, album, track_num = extract_metadata(file_path, file_name)
                
                song_hash = generate_song_hash(title, artist_str, album)
                if song_hash in processed_hashes:
                    continue 
                processed_hashes.add(song_hash)
                # 基于歌曲元数据生成哈希
                cover_url = extract_and_optimize_cover(file_path)
                
                y, sr = librosa.load(file_path, sr=22050, duration=30.0)
                tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
                mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=20)
                mfcc_mean = np.mean(mfcc.T, axis=0)
                
                artist_list = split_artists(artist_str)
                for artist in artist_list:
                    song_data = {
                        "hash_id": song_hash,     
                        "file_name": file_name,
                        "title": title,
                        "artist": artist,
                        "album": album,           
                        "track_num": track_num,   
                        "true_genre": genre,
                        "bpm": round(tempo[0], 2),
                        "cover_url": cover_url   
                    }
                    for i, val in enumerate(mfcc_mean):
                        song_data[f"mfcc_{i+1}"] = val
                    dataset.append(song_data)
                
            except Exception as e:
                error_files.append((file_name, str(e)))
                continue

    if dataset:
        df = pd.DataFrame(dataset)
        df.to_csv(OUTPUT_CSV, index=False, encoding='utf-8-sig')
        print(f"\n🎉 测绘完成！")
        print(f"📈 有效数据行数: {len(dataset)} 行")
        print(f"📁 核心特征库保存至: {OUTPUT_CSV}")
        print(f"🖼️ 优化后的封面保存在: {COVER_DIR}")
        
        if error_files:
            print(f"\n⚠️ 提取失败记录 (Top 5):")
            for f, err in error_files[:5]: print(f"   - {f}: {err}")

if __name__ == "__main__":
    process_batch()