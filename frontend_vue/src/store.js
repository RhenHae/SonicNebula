import { reactive } from 'vue'

export const store = reactive({
  lang: 'zh',
  theme: 'dark',
  qualityMode: true,
  currentFilter: 'default',
  currentPage: 'explorer',
  
  activeSong: {
    id: null,
    title: '等待信号接入...',
    artist: '未知',
    genre: 'Unknown',
    bpm: 0,
    x: 0,
    y: 0,
    album: '未知专辑',
    ai_review: '系统正在通过 Librosa 提取声学特征并等待大模型生成听感报告...'
  }
})