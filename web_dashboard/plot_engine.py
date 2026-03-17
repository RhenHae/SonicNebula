# plot_engine.py
import plotly.express as px
import plotly.graph_objects as go
from i18n_config import get_text

def get_theme_config(theme):
    """根据主题返回对应的配色配置"""
    if theme == "dark":
        return {
            "template": "plotly_dark",
            "bg_color": "rgba(0,0,0,0)",
            "radar_avg_line": "rgba(150, 150, 150, 0.4)",
            "radar_avg_fill": "rgba(150, 150, 150, 0.1)",
            "radar_cur_line": "#00FFCC",
            "radar_cur_fill": "rgba(0, 255, 204, 0.4)",
            "font_color": "white"
        }
    else:
        return {
            "template": "plotly_white",
            "bg_color": "rgba(255,255,255,0)",
            "radar_avg_line": "rgba(100, 100, 100, 0.5)",
            "radar_avg_fill": "rgba(100, 100, 100, 0.2)",
            "radar_cur_line": "#0066FF",
            "radar_cur_fill": "rgba(0, 102, 255, 0.3)",
            "font_color": "black"
        }

def draw_minimap(df, selected_genre, selected_song_title, theme):
    tc = get_theme_config(theme)
    fig_map = go.Figure()

    if selected_genre == "全部" or selected_genre == "All":
        fig_map.add_trace(go.Scatter(
            x=df['x'], y=df['y'], mode='markers',
            marker=dict(size=df['star_size'], color=df['cluster_id'].astype(int), colorscale='Turbo', opacity=0.8),
            hoverinfo='text', text=df['title']
        ))
        x_range = [df['x'].min()-5, df['x'].max()+5]
        y_range =[df['y'].min()-5, df['y'].max()+5]
    else:
        df_other = df[df['true_genre'] != selected_genre]
        df_focus = df[df['true_genre'] == selected_genre]
        
        # 暗色星星
        fig_map.add_trace(go.Scatter(
            x=df_other['x'], y=df_other['y'], mode='markers',
            marker=dict(size=df_other['star_size'], color='rgba(150,150,150,0.1)'), hoverinfo='skip'
        ))
        # 高亮流派
        fig_map.add_trace(go.Scatter(
            x=df_focus['x'], y=df_focus['y'], mode='markers',
            marker=dict(size=df_focus['star_size'], color=tc['radar_cur_line'], opacity=0.7),
            hoverinfo='text', text=df_focus['title']
        ))
        
        if selected_song_title and selected_song_title not in ["未选择", "None"]:
            target_song = df_focus[df_focus['title'] == selected_song_title].iloc[0]
            for radius, opac in[(25, 0.2), (15, 0.5), (8, 1.0)]:
                fig_map.add_trace(go.Scatter(
                    x=[target_song['x']], y=[target_song['y']], mode='markers',
                    marker=dict(size=radius, color='#FFD700', opacity=opac, line=dict(width=0)), hoverinfo='skip'
                ))
                
        padding_x = (df_focus['x'].max() - df_focus['x'].min()) * 0.1
        padding_y = (df_focus['y'].max() - df_focus['y'].min()) * 0.1
        x_range = [df_focus['x'].min() - padding_x, df_focus['x'].max() + padding_x]
        y_range = [df_focus['y'].min() - padding_y, df_focus['y'].max() + padding_y]

    fig_map.update_layout(
        xaxis=dict(showgrid=False, zeroline=False, visible=False, range=x_range, fixedrange=True),
        yaxis=dict(showgrid=False, zeroline=False, visible=False, range=y_range, fixedrange=True, scaleanchor="x", scaleratio=1),
        margin=dict(l=0, r=0, b=0, t=0),
        paper_bgcolor=tc['bg_color'], plot_bgcolor=tc['bg_color'],
        showlegend=False, height=450, dragmode=False, hovermode='closest'
    )
    return fig_map

def draw_radar(genre_centroid, song_vector, categories, global_min, global_max, theme):
    tc = get_theme_config(theme)
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=genre_centroid, theta=categories, fill='toself', name='Avg', line_color=tc['radar_avg_line'], fillcolor=tc['radar_avg_fill']))
    fig.add_trace(go.Scatterpolar(r=song_vector, theta=categories, fill='toself', name='Cur', line_color=tc['radar_cur_line'], fillcolor=tc['radar_cur_fill']))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=False, range=[global_min, global_max])),
        showlegend=False, template=tc['template'], height=280, margin=dict(l=20, r=20, t=20, b=20),
        paper_bgcolor=tc['bg_color'], plot_bgcolor=tc['bg_color']
    )
    return fig

def draw_vibe(df_focus, target_song, lang, theme):
    from i18n_config import get_text as t
    tc = get_theme_config(theme)
    
    fig = px.scatter(df_focus, x='mfcc_2', y='mfcc_1', template=tc['template'])
    fig.add_trace(go.Scatter(x=[target_song['mfcc_2']], y=[target_song['mfcc_1']], mode='markers', marker=dict(size=12, color='#FFD700', symbol='star')))
    
    fig.update_layout(
        xaxis=dict(title=f"← {t(lang, 'vibe_y_dark')}    {t(lang, 'vibe_y_bright')} →", showgrid=False), 
        yaxis=dict(title='', showgrid=False),
        height=280, margin=dict(l=40, r=0, t=20, b=0), paper_bgcolor=tc['bg_color'], plot_bgcolor=tc['bg_color'], showlegend=False
    )
    
    # 垂直文字
    v_text = f"{t(lang, 'vibe_x_explosive')}<br>↑<br><br>↓<br>{t(lang, 'vibe_x_calm')}"
    # 如果是英文，做一点排版适配
    if lang == "en": v_text = "Exp<br>↑<br><br>↓<br>Calm"
        
    fig.add_annotation(
        x=-0.05, y=0.5, xref="paper", yref="paper", text=v_text,
        showarrow=False, font=dict(size=12, color="gray"), textangle=0
    )
    return fig

def draw_bpm(df_focus, target_song, theme):
    tc = get_theme_config(theme)
    fig = px.violin(df_focus, y='bpm', box=True, points="all", template=tc['template'])
    fig.add_hline(y=target_song['bpm'], line_dash="dash", line_color="#FFD700")
    fig.update_layout(
        xaxis=dict(visible=False), yaxis=dict(title='BPM', showgrid=True),
        height=280, margin=dict(l=0, r=0, t=20, b=0), paper_bgcolor=tc['bg_color'], plot_bgcolor=tc['bg_color']
    )
    return fig

def draw_dna(song_mfcc_all, theme):
    tc = get_theme_config(theme)
    fig = px.imshow(song_mfcc_all, x=[f"F-{i}" for i in range(1, 21)], y=[""], color_continuous_scale="Plasma", aspect="auto")
    fig.update_layout(template=tc['template'], height=100, margin=dict(l=0, r=0, t=10, b=0), coloraxis_showscale=False, yaxis=dict(visible=False), paper_bgcolor=tc['bg_color'])
    return fig