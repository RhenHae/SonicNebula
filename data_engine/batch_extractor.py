import os
import glob
import librosa
import numpy as np
import pandas as pd
import warnings
import re
from mutagen.easyid3 import EasyID3
from mutagen import File
from tqdm import tqdm

warnings.filterwarnings('ignore')

AUDIO_DIR = "./raw_audio"
OUTPUT_CSV = "./output/music_features.csv"

def extract_metadata(file_path, file_name):
    """
    智能提取歌名和歌手，支持 ID3 和 文件名解析
    """
    title, artist_str = "Unknown Title", "Unknown Artist"
    
    try:
        # 优先尝试读取音频文件内置的 ID3 标签
        audio = File(file_path, easy=True)
        if audio is not None:
            if 'title' in audio:
                title = audio['title'][0]
            if 'artist' in audio:
                # 很多 ID3 标签里多歌手是用 '/' 或 ';' 隔开的
                artist_str = audio['artist'][0]
    except Exception:
        pass # 如果读不到内置标签，直接忽略，走备用方案

    # 如果内置标签没读到，尝试从文件名解析 (假设格式为 "歌手 - 歌名.mp3")
    if title == "Unknown Title" or artist_str == "Unknown Artist":
        # 去掉后缀名
        name_without_ext = os.path.splitext(file_name)[0]
        if " - " in name_without_ext:
            parts = name_without_ext.split(" - ", 1)
            artist_str = parts[0].strip()
            title = parts[1].strip()
        else:
            title = name_without_ext

    return title, artist_str

def split_artists(artist_str):
    """
    清洗并拆分多歌手字符串
    将常见的连接符 (&, ,, /, feat., ft.) 统一替换为 '、' 然后拆分
    """
    # 统一替换各种常见的多歌手分隔符为 '、'
    # 注意：这里用正则忽略了大小写匹配 feat. 和 ft.
    clean_str = re.sub(r'(?i)\s*feat\.\s*|\s*ft\.\s*|\s*&\s*|\s*,\s*|\s*/\s*|\s*;\s*', '、', artist_str)
    
    # 按 '、' 拆分，并去除两边空格，过滤掉空字符串
    artists =[a.strip() for a in clean_str.split('、') if a.strip()]
    
    # 如果拆分后为空，保底给一个 Unknown
    return artists if artists else ["Unknown Artist"]

def process_batch():
    dataset = []
    error_files =[]
    
    # 获取所有的曲风文件夹 (Metal, MidwestEMO, PostPunk, PostRock, Shoegaze)
    genres =[d for d in os.listdir(AUDIO_DIR) if os.path.isdir(os.path.join(AUDIO_DIR, d))]
    
    if not genres:
         print(f"⚠️ 在 {AUDIO_DIR} 下没找到文件夹！请确保结构如 raw_audio/Shoegaze/...")
         return

    print(f"🚀 发现 {len(genres)} 种流派，准备启动多线程基因提取...")

    for genre in genres:
        genre_path = os.path.join(AUDIO_DIR, genre)
        # 获取 mp3, wav, flac 等格式
        audio_files =[]
        for ext in ('*.mp3', '*.wav', '*.flac', '*.m4a'):
            audio_files.extend(glob.glob(os.path.join(genre_path, ext)))
            
        print(f"\n🎧 正在处理: {genre.upper()} (共 {len(audio_files)} 首)")
        
        for file_path in tqdm(audio_files, desc=f"提取 {genre}"):
            file_name = os.path.basename(file_path)
            
            try:
                # 1. 智能提取与清洗元数据
                title, artist_str = extract_metadata(file_path, file_name)
                artist_list = split_artists(artist_str) # 返回一个歌手列表
                
                # 2. 提取声学特征 (最耗时的一步)
                y, sr = librosa.load(file_path, sr=22050, duration=30.0)
                tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
                mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=20)
                mfcc_mean = np.mean(mfcc.T, axis=0)
                
                # 3. 数据爆炸 (Data Explode)
                # 针对每一个歌手，生成一行完全独立的数据！
                for artist in artist_list:
                    song_data = {
                        "file_name": file_name,
                        "title": title,
                        "artist": artist,          # 这里已经是拆分后的单个歌手了
                        "true_genre": genre,
                        "bpm": round(tempo[0], 2)
                    }
                    
                    # 拼装 20 维 MFCC 特征
                    for i, val in enumerate(mfcc_mean):
                        song_data[f"mfcc_{i+1}"] = val
                        
                    dataset.append(song_data)
                
            except Exception as e:
                error_files.append((file_name, str(e)))
                continue

    # 4. 导出为 CSV，强制使用 utf-8-sig 防止多语言乱码
    if dataset:
        df = pd.DataFrame(dataset)
        os.makedirs("./output", exist_ok=True)
        df.to_csv(OUTPUT_CSV, index=False, encoding='utf-8-sig')
        
        # 统计分析报告
        print(f"\n🎉 批量处理完成！")
        print(f"📄 原始文件数: {sum([len(glob.glob(os.path.join(AUDIO_DIR, g, '*.*'))) for g in genres])} 首")
        print(f"📈 拆分后数据量 (包含多歌手裂变): {len(dataset)} 行")
        print(f"📁 数据集已保存至: {OUTPUT_CSV}")
        
        if error_files:
            print(f"\n⚠️ 有 {len(error_files)} 首音频提取失败 (已跳过)：")
            for f, err in error_files[:5]: 
                print(f"   - {f}: {err}")

if __name__ == "__main__":
    process_batch()