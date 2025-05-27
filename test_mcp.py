#!/usr/bin/env python3
"""
Reddit Trend MCP Test Script
MCP server'ının fonksiyonlarını test eder.
"""

import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import our MCP functions
from reddit_mcp_server import (
    get_subreddit_hot_posts,
    get_subreddit_trending_topics,
    compare_subreddits,
    get_reddit_search,
    get_subreddit_info,
    init_reddit
)

def test_reddit_connection():
    """Test Reddit API connection"""
    print("🔍 Reddit API bağlantısı test ediliyor...")
    
    if init_reddit():
        print("✅ Reddit API bağlantısı başarılı!")
        return True
    else:
        print("❌ Reddit API bağlantısı başarısız!")
        print("Lütfen .env dosyasında credentials'ları kontrol edin.")
        return False

def test_hot_posts():
    """Test hot posts functionality"""
    print("\n📊 Hot posts testi...")
    
    result = get_subreddit_hot_posts("programming", 5)
    
    if "error" in result:
        print(f"❌ Hata: {result['error']}")
        return False
    
    print(f"✅ {result['analysis']['total_posts']} post getirildi")
    print(f"📈 Ortalama score: {result['analysis']['average_score']}")
    print(f"💬 Toplam yorum: {result['analysis']['total_comments']}")
    
    if result['posts']:
        print(f"🔥 En popüler: {result['posts'][0]['title'][:50]}...")
    
    return True

def test_trending_topics():
    """Test trending topics functionality"""
    print("\n🔥 Trending topics testi...")
    
    result = get_subreddit_trending_topics("programming", "day")
    
    if "error" in result:
        print(f"❌ Hata: {result['error']}")
        return False
    
    print(f"✅ {result['analysis']['total_posts_analyzed']} post analiz edildi")
    print(f"📝 {result['analysis']['unique_words']} benzersiz kelime bulundu")
    
    if result['trending_words']:
        print("🔥 En trending kelimeler:")
        for i, word_data in enumerate(result['trending_words'][:5], 1):
            print(f"   {i}. {word_data['word']} ({word_data['frequency']}x)")
    
    return True

def test_subreddit_comparison():
    """Test subreddit comparison functionality"""
    print("\n⚖️  Subreddit karşılaştırma testi...")
    
    result = compare_subreddits(["python", "javascript"], "activity")
    
    if "error" in result:
        print(f"❌ Hata: {result['error']}")
        return False
    
    print(f"✅ {len(result['comparison'])} subreddit karşılaştırıldı")
    
    if result['winner']:
        winner = result['winner']
        print(f"🏆 Kazanan: r/{winner['name']}")
        print(f"👥 Subscribers: {winner.get('subscribers', 'N/A')}")
        print(f"📊 Engagement: {winner.get('total_engagement', 'N/A')}")
    
    return True

def test_search():
    """Test search functionality"""
    print("\n🔍 Arama testi...")
    
    result = get_reddit_search("python tutorial", "programming", "top", "week")
    
    if "error" in result:
        print(f"❌ Hata: {result['error']}")
        return False
    
    print(f"✅ {result['total_found']} sonuç bulundu")
    
    if result['results']:
        print(f"🔝 İlk sonuç: {result['results'][0]['title'][:50]}...")
        print(f"📊 Score: {result['results'][0]['score']}")
    
    return True

def test_subreddit_info():
    """Test subreddit info functionality"""
    print("\n📋 Subreddit bilgi testi...")
    
    result = get_subreddit_info("programming")
    
    if "error" in result:
        print(f"❌ Hata: {result['error']}")
        return False
    
    print(f"✅ Subreddit: r/{result['name']}")
    print(f"📝 Başlık: {result['title']}")
    print(f"👥 Subscribers: {result['subscribers']:,}")
    print(f"🔴 Aktif kullanıcı: {result.get('active_users', 'N/A')}")
    print(f"👮 Moderatör sayısı: {len(result['moderators'])}")
    
    return True

def run_all_tests():
    """Run all tests"""
    print("🚀 Reddit Trend MCP Test Suite")
    print("=" * 50)
    
    # Test connection first
    if not test_reddit_connection():
        print("\n❌ Reddit API bağlantısı kurulamadığı için testler durduruluyor.")
        return False
    
    tests = [
        ("Hot Posts", test_hot_posts),
        ("Trending Topics", test_trending_topics),
        ("Subreddit Comparison", test_subreddit_comparison),
        ("Search", test_search),
        ("Subreddit Info", test_subreddit_info)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} testi başarısız!")
        except Exception as e:
            print(f"❌ {test_name} testi hata verdi: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Sonuçları: {passed}/{total} başarılı")
    
    if passed == total:
        print("🎉 Tüm testler başarılı! MCP server hazır.")
        return True
    else:
        print("⚠️  Bazı testler başarısız. Lütfen hataları kontrol edin.")
        return False

if __name__ == "__main__":
    # Check environment variables
    required_vars = ['REDDIT_CLIENT_ID', 'REDDIT_CLIENT_SECRET']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print("❌ Eksik environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nLütfen .env dosyasını oluşturun ve gerekli değişkenleri ayarlayın.")
        print("Örnek için env_example.txt dosyasına bakın.")
        exit(1)
    
    # Run tests
    success = run_all_tests()
    exit(0 if success else 1) 