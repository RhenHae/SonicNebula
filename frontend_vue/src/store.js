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
    y: 0
  }
})