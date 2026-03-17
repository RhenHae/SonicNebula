import streamlit as st
import pandas as pd
import json
import os
from i18n_config import get_text as t
import plot_engine as pe

# ==========================================
# 📌 1. 初始化设置状态
# ==========================================
st.set_page_config(page_title="MusicSpectrum", page_icon="🎵", layout="wide", initial_sidebar_state="collapsed")

if 'lang' not in st.session_state:
    st.session_state.lang = "zh"
if 'theme' not in st.session_state:
    st.session_state.theme = "dark"

# ==========================================
# 📌 2. 动态 CSS Navbar & 吸顶设置
# ==========================================
nav_bg = "rgba(20, 20, 24, 0.85)" if st.session_state.theme == "dark" else "rgba(240, 242, 246, 0.85)"
nav_text = "#FFFFFF" if st.session_state.theme == "dark" else "#000000"

st.markdown(f"""
<style>
    /* 隐藏默认 Header 和调整 Padding */
    header {{ visibility: hidden !important; display: none !important; }}
    .block-container {{ padding-top: 5rem !important; padding-bottom: 0rem !important; max-width: 95% !important; }}
    
    /* 吸顶导航栏基础样式 */
    .custom-navbar {{
        position: fixed; top: 0; left: 0; width: 100%; height: 60px;
        background-color: {nav_bg};
        backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
        z-index: 99998; display: flex; justify-content: space-between; align-items: center;
        padding: 0 40px; border-bottom: 1px solid rgba(0, 255, 204, 0.3);
    }}
    .navbar-title {{ color: {nav_text}; font-size: 22px; font-weight: 800; margin: 0; }}
    .navbar-menu {{ display: flex; gap: 30px; align-items: center; margin-right: 300px; /* 留出右侧空间给 Streamlit 按钮 */ }}
    .nav-item {{ color: gray; font-size: 15px; font-weight: 500; cursor: not-allowed; }}
    .nav-item.active {{ color: #00FFCC; font-weight: 700; border-bottom: 2px solid #00FFCC; padding-bottom: 5px; }}

    /* 💡 黑科技：将 Streamlit 的 st.columns 强行吸顶到导航栏右侧 */
    div[data-testid="stColumns"]:first-of-type {{
        position: fixed !important;
        top: 10px !important;
        right: 40px !important;
        width: 250px !important;
        z-index: 99999 !important;
        background: transparent !important;
    }}
    
    /* 缩小 radio 按钮的体积，使其看起来像精致的 Navbar 图标 */
    div[data-testid="stRadio"] > div {{ flex-direction: row; gap: 10px; }}
    div[data-testid="stRadio"] label {{ padding: 0; margin: 0; font-size: 12px; }}
    div[data-testid="stRadio"] [role="radiogroup"] {{ gap: 5px; }}
</style>

<div class="custom-navbar">
    <div class="navbar-title">{t(st.session_state.lang, 'nav_title')}</div>
    <div class="navbar-menu">
        <div class="nav-item active">{t(st.session_state.lang, 'nav_explorer')}</div>
        <div class="nav-item">{t(st.session_state.lang, 'nav_intro')} 🔒</div>
        <div class="nav-item">{t(st.session_state.lang, 'nav_analysis')} 🔒</div>
        <div class="nav-item">{t(st.session_state.lang, 'nav_about')} 🔒</div>
    </div>
</div>
""", unsafe_allow_html=True)

# 💡 黑科技实现：紧接着 HTML 输出第一组 columns，它会被 CSS 抓取并钉在右上角！
set_col1, set_col2 = st.columns(2)
with set_col1:
    new_lang = st.radio("🌐", ["zh", "en"], index=0 if st.session_state.lang=="zh" else 1, label_visibility="collapsed")
    if new_lang != st.session_state.lang:
        st.session_state.lang = new_lang
        st.rerun()
with set_col2:
    new_theme = st.radio("🌗", ["dark", "light"], index=0 if st.session_state.theme=="dark" else 1, label_visibility="collapsed")
    if new_theme != st.session_state.theme:
        st.session_state.theme = new_theme
        st.rerun()


# ==========================================
# 📌 3. 数据加载与基础处理
# ==========================================
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)

@st.cache_data
def load_cached_data():
    csv_path = os.path.join(PROJECT_ROOT, "data_lake", "dashboard_data.csv")
    json_path = os.path.join(PROJECT_ROOT, "data_lake", "genre_centroids.json")
    
    if not os.path.exists(csv_path) or not os.path.exists(json_path): return None, None
    
    df = pd.read_csv(csv_path)
    df['cluster_id'] = df['cluster_id'].astype(str)
    with open(json_path, 'r', encoding='utf-8') as f:
        centroids_map = json.load(f)
    return df, centroids_map

df, centroids_map = load_cached_data()
if df is None: 
    st.error("❌ Data not found!")
    st.stop()

radar_cols =[f"mfcc_{i}" for i in range(1, 7)]
lang = st.session_state.lang
theme = st.session_state.theme

# ==========================================
# 📌 4. 页面主体布局 (去除了 Title，直奔主题)
# ==========================================

# 筛选器
col_sel1, col_sel2 = st.columns(2)
with col_sel1:
    all_txt = t(lang, 'all')
    genre_list =[all_txt] + sorted(df['true_genre'].unique().tolist())
    selected_genre = st.selectbox(t(lang, 'step1'), genre_list)

with col_sel2:
    unsel_txt = t(lang, 'unselected')
    if selected_genre != all_txt:
        songs_in_genre = df[df['true_genre'] == selected_genre]['title'].tolist()
        selected_song_title = st.selectbox(t(lang, 'step2'), [unsel_txt] + songs_in_genre)
    else:
        st.selectbox(t(lang, 'step2'),[t(lang, 'lock_first')], disabled=True)
        selected_song_title = unsel_txt

# 渲染小地图 (直接紧跟筛选器)
st.markdown("<br>", unsafe_allow_html=True)
st.subheader(t(lang, 'map_title'))
fig_map = pe.draw_minimap(df, selected_genre, selected_song_title, theme)
st.plotly_chart(fig_map, use_container_width=True)

st.markdown("---")

# ==========================================
# 📌 5. 详情分析面板
# ==========================================
if selected_genre != all_txt and selected_song_title != unsel_txt:
    target_song = df[df['title'] == selected_song_title].iloc[0]
    
    # 指标栏
    m1, m2, m3, m4 = st.columns(4)
    m1.metric(label=t(lang, 'metric_artist'), value=target_song['artist'])
    m2.metric(label=t(lang, 'metric_bpm'), value=f"{target_song['bpm']:.0f}")
    m3.metric(label=t(lang, 'metric_cluster'), value=f"ID: {target_song['cluster_id']}")
    
    purity_score = target_song['purity_score']
    m4.metric(label=t(lang, 'pure_level'), value=f"{purity_score:.1f}%")
    st.progress(purity_score / 100)
    
    st.markdown("---")

    # 三分栏图表
    col_radar, col_vibe, col_bpm = st.columns([1.2, 1, 1])
    
    with col_radar:
        st.subheader(t(lang, 'radar_title'))
        global_min, global_max = df[radar_cols].min().min() - 10, df[radar_cols].max().max() + 10
        categories =['E', 'Bright', 'Centroid', 'Rough', 'Mid', 'High'] if lang == "en" else['能量密度', '音色明暗', '频谱质心', '粗糙度', '中频厚度', '高频泛音']
        
        fig_radar = pe.draw_radar(centroids_map[selected_genre][:6], target_song[radar_cols].values.tolist(), categories, global_min, global_max, theme)
        st.plotly_chart(fig_radar, use_container_width=True)

    with col_vibe:
        st.subheader(t(lang, 'vibe_title'))
        df_focus = df[df['true_genre'] == selected_genre]
        fig_vibe = pe.draw_vibe(df_focus, target_song, lang, theme)
        st.plotly_chart(fig_vibe, use_container_width=True)

    with col_bpm:
        st.subheader(t(lang, 'bpm_title'))
        fig_bpm = pe.draw_bpm(df_focus, target_song, theme)
        st.plotly_chart(fig_bpm, use_container_width=True)

    # 基因条码
    st.subheader(t(lang, 'dna_title'))
    mfcc_cols_all =[f"mfcc_{i}" for i in range(1, 21)]
    fig_dna = pe.draw_dna(target_song[mfcc_cols_all].values.reshape(1, -1), theme)
    st.plotly_chart(fig_dna, use_container_width=True)