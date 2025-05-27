# 🔥 Reddit Trend MCP Server

AI destekli Reddit trend analizi için **Model Context Protocol (MCP)** server'ı. Subreddit'lerdeki hot konuları, trending kelimeleri ve engagement metriklerini analiz eder.

## 🚀 Özellikler

### 📊 Ana Fonksiyonlar
- **Hot Posts Analizi**: Subreddit'lerdeki popüler postları getirir
- **Trending Kelime Analizi**: En çok konuşulan konuları tespit eder  
- **Subreddit Karşılaştırması**: Birden fazla subreddit'i karşılaştırır
- **Reddit Arama**: Gelişmiş arama ve filtreleme
- **Detaylı Subreddit Bilgileri**: Moderatörler, kurallar, istatistikler

### 🎯 Kullanım Senaryoları
- "r/programming'de bugün neler konuşuluyor?"
- "Python vs JavaScript subreddit'lerini karşılaştır"
- "AI konusunda trending olan kelimeler neler?"
- "r/MachineLearning'de en popüler postlar"

## 📋 Gereksinimler

- Python 3.8+
- Reddit API credentials
- MCP destekli AI client (Claude, Cursor, vb.)

## 🛠️ Kurulum

### 1. Projeyi İndirin
```bash
git clone <your-repo>
cd reddit-trend-mcp
```

### 2. Bağımlılıkları Yükleyin
```bash
pip install -r requirements.txt
```

### 3. Reddit API Anahtarları

#### Reddit App Oluşturma:
1. [Reddit Apps](https://www.reddit.com/prefs/apps) sayfasına gidin
2. "Create App" veya "Create Another App" tıklayın
3. **App türü**: "script" seçin
4. **Name**: "Reddit Trend MCP" 
5. **Description**: "MCP server for Reddit trend analysis"
6. **Redirect URI**: `http://localhost:8080` (gerekli değil ama zorunlu alan)

#### Credentials'ları Kaydedin:
```bash
# env_example.txt dosyasını .env olarak kopyalayın
cp env_example.txt .env

# .env dosyasını düzenleyin:
REDDIT_CLIENT_ID=your_14_character_client_id
REDDIT_CLIENT_SECRET=your_27_character_secret
REDDIT_USER_AGENT=RedditTrendMCP/1.0
```

### 4. Test Edin
```bash
python reddit_mcp_server.py
```

✅ Başarılı çıktı:
```
✅ Reddit MCP Server başlatılıyor...
🔧 Kullanılabilir araçlar:
   - get_subreddit_hot_posts: Hot postları getir
   - get_subreddit_trending_topics: Trending konuları analiz et
   - compare_subreddits: Subreddit'leri karşılaştır
   - get_reddit_search: Reddit'te arama yap
   - get_subreddit_info: Subreddit detay bilgileri
```

## 🔧 MCP Client Entegrasyonu

### Cursor IDE ile Kullanım

1. **Cursor Settings** → **MCP** → **Add new global MCP server**

2. `mcp.json` dosyasına ekleyin:
```json
{
  "mcpServers": {
    "reddit-trend": {
      "command": "python",
      "args": ["/tam/yol/reddit_mcp_server.py"],
      "env": {
        "REDDIT_CLIENT_ID": "your_client_id",
        "REDDIT_CLIENT_SECRET": "your_client_secret",
        "REDDIT_USER_AGENT": "RedditTrendMCP/1.0"
      }
    }
  }
}
```

3. **Cursor'u yeniden başlatın**

4. **Chat'te test edin**:
```
"r/programming'de bugün en popüler 5 post nedir?"
```

### Claude Desktop ile Kullanım

`claude_desktop_config.json` dosyasına:
```json
{
  "mcpServers": {
    "reddit-trend": {
      "command": "python",
      "args": ["/tam/yol/reddit_mcp_server.py"]
    }
  }
}
```

## 📚 API Referansı

### `get_subreddit_hot_posts(subreddit_name, limit=10)`
```python
# Örnek kullanım
result = get_subreddit_hot_posts("programming", 15)
```
**Döner**: Hot postlar, upvote analizi, yorum istatistikleri

### `get_subreddit_trending_topics(subreddit_name, time_filter="day")`
```python
# Örnek kullanım  
result = get_subreddit_trending_topics("MachineLearning", "week")
```
**Döner**: Trending kelimeler, frekans analizi

### `compare_subreddits(subreddit_names, metric="activity")`
```python
# Örnek kullanım
result = compare_subreddits(["python", "javascript", "golang"], "engagement")
```
**Döner**: Karşılaştırmalı analiz, kazanan subreddit

### `get_reddit_search(query, subreddit_name=None, sort="relevance")`
```python
# Örnek kullanım
result = get_reddit_search("machine learning", "programming", "top")
```
**Döner**: Arama sonuçları, relevans skoru

### `get_subreddit_info(subreddit_name)`
```python
# Örnek kullanım
result = get_subreddit_info("programming")
```
**Döner**: Subreddit detayları, moderatörler, kurallar

## 🎯 Örnek Kullanımlar

### 1. Trend Analizi
```
"r/artificial'da bu hafta en çok konuşulan konular neler?"
```

### 2. Subreddit Karşılaştırması  
```
"r/MachineLearning ve r/deeplearning subreddit'lerini activity bazında karşılaştır"
```

### 3. Popüler İçerik Keşfi
```
"r/programming'de bugün en çok upvote alan 10 post"
```

### 4. Arama ve Filtreleme
```
"Reddit'te 'Python tutorial' araması yap, son 1 hafta içinde"
```

## 🚀 Smithery'e Deploy

### 1. Smithery Hesabı
[Smithery.ai](https://smithery.ai) hesabı oluşturun

### 2. MCP Server'ı Paketleyin
```bash
# Dockerfile oluşturun (opsiyonel)
# Veya direkt Python script olarak deploy edin
```

### 3. Environment Variables
Smithery dashboard'da:
- `REDDIT_CLIENT_ID`
- `REDDIT_CLIENT_SECRET`  
- `REDDIT_USER_AGENT`

### 4. Deploy Edin
```bash
smithery deploy reddit-trend-mcp
```

## 🤖 Mastra Agent Entegrasyonu

### 1. Mastra Projesi Oluşturun
```bash
npx create-mastra-app reddit-agent
cd reddit-agent
```

### 2. MCP Integration
```typescript
// mastra.config.ts
import { Mastra } from '@mastra/core';

export const mastra = new Mastra({
  name: 'Reddit Trend Agent',
  tools: [
    {
      name: 'reddit-trend',
      type: 'mcp',
      config: {
        serverUrl: 'your-smithery-mcp-url',
        // veya local: 'python reddit_mcp_server.py'
      }
    }
  ]
});
```

### 3. Agent Workflow
```typescript
// workflows/reddit-analysis.ts
export const redditAnalysisWorkflow = {
  name: 'Reddit Trend Analysis',
  steps: [
    {
      tool: 'reddit-trend',
      action: 'get_subreddit_hot_posts',
      params: { subreddit_name: 'programming', limit: 10 }
    },
    {
      tool: 'reddit-trend', 
      action: 'get_subreddit_trending_topics',
      params: { subreddit_name: 'programming', time_filter: 'day' }
    }
  ]
};
```

## 🔍 Troubleshooting

### Reddit API Hataları
```
Error: Reddit API bağlantısı kurulamadı
```
**Çözüm**: 
- Client ID/Secret'ı kontrol edin
- User Agent formatını kontrol edin
- Reddit app türünün "script" olduğundan emin olun

### MCP Connection Hataları
```
Error: MCP server bulunamadı
```
**Çözüm**:
- Python path'ini kontrol edin
- Dependencies yüklü mü kontrol edin
- Port çakışması var mı kontrol edin

### Rate Limiting
```
Error: Too Many Requests
```
**Çözüm**:
- Request sayısını azaltın
- Time delay ekleyin
- Reddit API limits'e uyun

## 📈 Gelecek Özellikler

- [ ] **Sentiment Analysis**: Post ve yorum duygu analizi
- [ ] **Real-time Monitoring**: Canlı trend takibi
- [ ] **Advanced Metrics**: Engagement rate, growth trends
- [ ] **Multi-language Support**: Türkçe subreddit analizi
- [ ] **Data Export**: CSV, JSON export seçenekleri
- [ ] **Visualization**: Grafik ve chart entegrasyonu

## 🤝 Katkıda Bulunma

1. Fork edin
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit edin (`git commit -m 'Add amazing feature'`)
4. Push edin (`git push origin feature/amazing-feature`)
5. Pull Request açın

## 📄 Lisans

MIT License - detaylar için `LICENSE` dosyasına bakın.

## 🙏 Teşekkürler

- [Reddit API](https://www.reddit.com/dev/api/) - Veri kaynağı
- [PRAW](https://praw.readthedocs.io/) - Python Reddit API Wrapper
- [MCP Protocol](https://modelcontextprotocol.io/) - Model Context Protocol
- [Smithery](https://smithery.ai) - MCP hosting platform
- [Mastra](https://mastra.ai) - Agent framework

---

**🔥 Reddit Trend MCP ile AI'ınızı Reddit'in nabzına bağlayın!** 🚀 