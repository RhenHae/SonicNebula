# i18n_config.py

TEXTS = {
    "zh": {
        "nav_title": "🎵 MusicSpectrum",
        "nav_explorer": "探索发现",
        "nav_intro": "简介",
        "nav_analysis": "歌曲解析",
        "nav_about": "关于",
        
        "step1": "音乐风格",
        "step2": "歌曲选择",
        "all": "全部",
        "unselected": "请选择",
        "lock_first": "请先选择音乐风格",
        
        "map_title": "音乐风格空间分布图",
        "pure_level": "流派特征吻合度",
        "radar_title": "多维声学特征对比",
        "vibe_title": "音乐情绪分布矩阵",
        "bpm_title": "流派 BPM (节拍) 分布",
        "dna_title": "MFCC 频谱特征热力图",
        
        "vibe_y_dark": "低沉",
        "vibe_y_bright": "明亮",
        "vibe_x_calm": "舒缓",
        "vibe_x_explosive": "激烈",
        
        "metric_artist": "艺术家",
        "metric_bpm": "节拍速率",
        "metric_cluster": "所属聚类"
    },
    
    "en": {
        "nav_title": "🎵 MusicSpectrum",
        "nav_explorer": "Explorer",
        "nav_intro": "Intro",
        "nav_analysis": "Analysis",
        "nav_about": "About",
        
        "step1": "Music Genre",
        "step2": "Song Selection",
        "all": "All",
        "unselected": "Select...",
        "lock_first": "Select genre first",
        
        "map_title": "Spatial Distribution of Genres",
        "pure_level": "Genre Match Score",
        "radar_title": "Acoustic Features Comparison",
        "vibe_title": "Musical Mood Matrix",
        "bpm_title": "BPM Distribution",
        "dna_title": "MFCC Feature Heatmap",
        
        "vibe_y_dark": "Dark",
        "vibe_y_bright": "Bright",
        "vibe_x_calm": "Calm",
        "vibe_x_explosive": "Intense",
        
        "metric_artist": "Artist",
        "metric_bpm": "BPM",
        "metric_cluster": "Cluster"
    }
}

def get_text(lang, key):
    return TEXTS.get(lang, TEXTS["zh"]).get(key, key)