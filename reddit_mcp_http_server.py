#!/usr/bin/env python3
"""
Reddit Trend MCP HTTP Server
Smithery deployment için HTTP transport kullanan versiyon.
"""

import os
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

# MCP imports for HTTP
from mcp.server.fastmcp import FastMCP
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions
from mcp.types import Resource, Tool, TextContent, ImageContent, EmbeddedResource

# Reddit API
import praw
import requests

# FastAPI for HTTP server
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn

# Load environment variables
load_dotenv()

# Reddit API credentials
REDDIT_CLIENT_ID = os.getenv('REDDIT_CLIENT_ID')
REDDIT_CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET')
REDDIT_USER_AGENT = os.getenv('REDDIT_USER_AGENT', 'RedditTrendMCP/1.0')

# Initialize MCP server
mcp = FastMCP("Reddit-Trend-MCP")

# Initialize Reddit instance
reddit = None

def init_reddit():
    """Initialize Reddit API connection"""
    global reddit
    try:
        reddit = praw.Reddit(
            client_id=REDDIT_CLIENT_ID,
            client_secret=REDDIT_CLIENT_SECRET,
            user_agent=REDDIT_USER_AGENT
        )
        # Test connection (skip for serverless)
        return True
    except Exception as e:
        print(f"Reddit API initialization failed: {e}")
        return False

@mcp.tool()
def get_subreddit_hot_posts(subreddit_name: str, limit: int = 10) -> Dict[str, Any]:
    """
    Belirtilen subreddit'teki hot (popüler) postları getirir.
    
    Args:
        subreddit_name: Subreddit adı (örn: 'programming', 'python')
        limit: Getirilecek post sayısı (varsayılan: 10, max: 25)
    
    Returns:
        Hot postların listesi ve analiz bilgileri
    """
    if not reddit:
        if not init_reddit():
            return {"error": "Reddit API bağlantısı kurulamadı. Lütfen credentials'ları kontrol edin."}
    
    try:
        # Limit kontrolü
        limit = min(max(1, limit), 25)
        
        subreddit = reddit.subreddit(subreddit_name)
        hot_posts = []
        
        for post in subreddit.hot(limit=limit):
            post_data = {
                "title": post.title,
                "author": str(post.author) if post.author else "[deleted]",
                "score": post.score,
                "upvote_ratio": post.upvote_ratio,
                "num_comments": post.num_comments,
                "created_utc": datetime.fromtimestamp(post.created_utc).isoformat(),
                "url": post.url,
                "permalink": f"https://reddit.com{post.permalink}",
                "selftext": post.selftext[:500] if post.selftext else "",
                "is_video": post.is_video,
                "over_18": post.over_18,
                "flair": post.link_flair_text
            }
            hot_posts.append(post_data)
        
        # Analiz bilgileri
        total_score = sum(post["score"] for post in hot_posts)
        avg_score = total_score / len(hot_posts) if hot_posts else 0
        total_comments = sum(post["num_comments"] for post in hot_posts)
        
        return {
            "subreddit": subreddit_name,
            "posts": hot_posts,
            "analysis": {
                "total_posts": len(hot_posts),
                "total_score": total_score,
                "average_score": round(avg_score, 2),
                "total_comments": total_comments,
                "most_upvoted": max(hot_posts, key=lambda x: x["score"]) if hot_posts else None,
                "most_commented": max(hot_posts, key=lambda x: x["num_comments"]) if hot_posts else None
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {"error": f"Subreddit '{subreddit_name}' analiz edilemedi: {str(e)}"}

@mcp.tool()
def get_subreddit_trending_topics(subreddit_name: str, time_filter: str = "day") -> Dict[str, Any]:
    """
    Subreddit'teki trending (yükselen) konuları analiz eder.
    
    Args:
        subreddit_name: Subreddit adı
        time_filter: Zaman filtresi ('hour', 'day', 'week', 'month', 'year', 'all')
    
    Returns:
        Trending konular ve kelime analizi
    """
    if not reddit:
        if not init_reddit():
            return {"error": "Reddit API bağlantısı kurulamadı."}
    
    try:
        subreddit = reddit.subreddit(subreddit_name)
        
        # Zaman filtresine göre top postları al
        if time_filter == "hour":
            posts = subreddit.top(time_filter="hour", limit=50)
        elif time_filter == "day":
            posts = subreddit.top(time_filter="day", limit=50)
        elif time_filter == "week":
            posts = subreddit.top(time_filter="week", limit=50)
        elif time_filter == "month":
            posts = subreddit.top(time_filter="month", limit=50)
        else:
            posts = subreddit.top(time_filter="day", limit=50)
        
        # Başlıkları topla ve analiz et
        titles = []
        post_data = []
        
        for post in posts:
            titles.append(post.title.lower())
            post_data.append({
                "title": post.title,
                "score": post.score,
                "num_comments": post.num_comments,
                "created_utc": datetime.fromtimestamp(post.created_utc).isoformat()
            })
        
        # Basit kelime frekans analizi
        word_freq = {}
        common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them', 'my', 'your', 'his', 'her', 'its', 'our', 'their'}
        
        for title in titles:
            words = title.split()
            for word in words:
                # Temizle ve filtrele
                word = ''.join(c for c in word if c.isalnum()).lower()
                if len(word) > 2 and word not in common_words:
                    word_freq[word] = word_freq.get(word, 0) + 1
        
        # En popüler kelimeleri sırala
        trending_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:20]
        
        return {
            "subreddit": subreddit_name,
            "time_filter": time_filter,
            "trending_words": [{"word": word, "frequency": freq} for word, freq in trending_words],
            "sample_posts": post_data[:10],
            "analysis": {
                "total_posts_analyzed": len(post_data),
                "unique_words": len(word_freq),
                "most_trending_word": trending_words[0] if trending_words else None
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {"error": f"Trending analizi başarısız: {str(e)}"}

@mcp.tool()
def compare_subreddits(subreddit_names: List[str], metric: str = "activity") -> Dict[str, Any]:
    """
    Birden fazla subreddit'i karşılaştırır.
    
    Args:
        subreddit_names: Karşılaştırılacak subreddit listesi
        metric: Karşılaştırma metriği ('activity', 'engagement', 'growth')
    
    Returns:
        Subreddit karşılaştırma analizi
    """
    if not reddit:
        if not init_reddit():
            return {"error": "Reddit API bağlantısı kurulamadı."}
    
    try:
        comparison_data = []
        
        for sub_name in subreddit_names[:5]:  # Max 5 subreddit
            try:
                subreddit = reddit.subreddit(sub_name)
                
                # Subreddit bilgilerini al
                hot_posts = list(subreddit.hot(limit=10))
                
                if hot_posts:
                    avg_score = sum(post.score for post in hot_posts) / len(hot_posts)
                    avg_comments = sum(post.num_comments for post in hot_posts) / len(hot_posts)
                    total_engagement = sum(post.score + post.num_comments for post in hot_posts)
                else:
                    avg_score = avg_comments = total_engagement = 0
                
                sub_data = {
                    "name": sub_name,
                    "subscribers": subreddit.subscribers,
                    "active_users": getattr(subreddit, 'active_user_count', 0),
                    "avg_score": round(avg_score, 2),
                    "avg_comments": round(avg_comments, 2),
                    "total_engagement": total_engagement,
                    "created_utc": datetime.fromtimestamp(subreddit.created_utc).isoformat(),
                    "description": subreddit.public_description[:200] if subreddit.public_description else ""
                }
                comparison_data.append(sub_data)
                
            except Exception as e:
                comparison_data.append({
                    "name": sub_name,
                    "error": f"Analiz edilemedi: {str(e)}"
                })
        
        # Sıralama
        if metric == "activity":
            comparison_data.sort(key=lambda x: x.get("total_engagement", 0), reverse=True)
        elif metric == "engagement":
            comparison_data.sort(key=lambda x: x.get("avg_score", 0), reverse=True)
        else:  # subscribers
            comparison_data.sort(key=lambda x: x.get("subscribers", 0), reverse=True)
        
        return {
            "comparison": comparison_data,
            "metric": metric,
            "winner": comparison_data[0] if comparison_data else None,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {"error": f"Karşılaştırma analizi başarısız: {str(e)}"}

@mcp.tool()
def get_reddit_search(query: str, subreddit_name: str = None, sort: str = "relevance", time_filter: str = "all") -> Dict[str, Any]:
    """
    Reddit'te arama yapar.
    
    Args:
        query: Arama sorgusu
        subreddit_name: Belirli bir subreddit'te ara (opsiyonel)
        sort: Sıralama ('relevance', 'hot', 'top', 'new', 'comments')
        time_filter: Zaman filtresi ('all', 'year', 'month', 'week', 'day', 'hour')
    
    Returns:
        Arama sonuçları
    """
    if not reddit:
        if not init_reddit():
            return {"error": "Reddit API bağlantısı kurulamadı."}
    
    try:
        if subreddit_name:
            subreddit = reddit.subreddit(subreddit_name)
            search_results = subreddit.search(query, sort=sort, time_filter=time_filter, limit=20)
        else:
            search_results = reddit.subreddit("all").search(query, sort=sort, time_filter=time_filter, limit=20)
        
        results = []
        for post in search_results:
            result_data = {
                "title": post.title,
                "subreddit": str(post.subreddit),
                "author": str(post.author) if post.author else "[deleted]",
                "score": post.score,
                "num_comments": post.num_comments,
                "created_utc": datetime.fromtimestamp(post.created_utc).isoformat(),
                "url": post.url,
                "permalink": f"https://reddit.com{post.permalink}",
                "selftext": post.selftext[:300] if post.selftext else ""
            }
            results.append(result_data)
        
        return {
            "query": query,
            "subreddit": subreddit_name or "all",
            "sort": sort,
            "time_filter": time_filter,
            "results": results,
            "total_found": len(results),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {"error": f"Arama başarısız: {str(e)}"}

@mcp.tool()
def get_subreddit_info(subreddit_name: str) -> Dict[str, Any]:
    """
    Subreddit hakkında detaylı bilgi getirir.
    
    Args:
        subreddit_name: Subreddit adı
    
    Returns:
        Subreddit detay bilgileri
    """
    if not reddit:
        if not init_reddit():
            return {"error": "Reddit API bağlantısı kurulamadı."}
    
    try:
        subreddit = reddit.subreddit(subreddit_name)
        
        # Moderatör listesi
        moderators = []
        try:
            for mod in subreddit.moderator(limit=10):
                moderators.append(str(mod))
        except:
            moderators = ["Bilgi alınamadı"]
        
        # Son postlar
        recent_posts = []
        for post in subreddit.new(limit=5):
            recent_posts.append({
                "title": post.title,
                "score": post.score,
                "created_utc": datetime.fromtimestamp(post.created_utc).isoformat()
            })
        
        return {
            "name": subreddit_name,
            "display_name": subreddit.display_name,
            "title": subreddit.title,
            "description": subreddit.public_description,
            "subscribers": subreddit.subscribers,
            "active_users": getattr(subreddit, 'active_user_count', 0),
            "created_utc": datetime.fromtimestamp(subreddit.created_utc).isoformat(),
            "over18": subreddit.over18,
            "lang": subreddit.lang,
            "moderators": moderators,
            "recent_posts": recent_posts,
            "rules_count": len(list(subreddit.rules)) if hasattr(subreddit, 'rules') else 0,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {"error": f"Subreddit bilgisi alınamadı: {str(e)}"}

# FastAPI app for HTTP transport
app = FastAPI(title="Reddit Trend MCP Server", version="1.0.0")

@app.get("/")
async def root():
    return {"message": "Reddit Trend MCP Server", "version": "1.0.0"}

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# MCP endpoint for Smithery
@app.api_route("/mcp", methods=["GET", "POST", "DELETE"])
async def mcp_endpoint(request: Request):
    """Handle MCP requests according to streamable HTTP specification"""
    try:
        # Initialize Reddit connection for each request (serverless)
        init_reddit()
        
        # Handle the MCP request
        if request.method == "GET":
            # List tools
            return {
                "tools": [
                    {
                        "name": "get_subreddit_hot_posts",
                        "description": "Get hot posts from a subreddit with analysis",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "subreddit_name": {"type": "string"},
                                "limit": {"type": "integer", "default": 10}
                            },
                            "required": ["subreddit_name"]
                        }
                    },
                    {
                        "name": "get_subreddit_trending_topics",
                        "description": "Analyze trending topics and keywords in a subreddit",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "subreddit_name": {"type": "string"},
                                "time_filter": {"type": "string", "default": "day"}
                            },
                            "required": ["subreddit_name"]
                        }
                    },
                    {
                        "name": "compare_subreddits",
                        "description": "Compare multiple subreddits by activity or engagement",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "subreddit_names": {"type": "array", "items": {"type": "string"}},
                                "metric": {"type": "string", "default": "activity"}
                            },
                            "required": ["subreddit_names"]
                        }
                    },
                    {
                        "name": "get_reddit_search",
                        "description": "Search Reddit with advanced filtering options",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "query": {"type": "string"},
                                "subreddit_name": {"type": "string"},
                                "sort": {"type": "string", "default": "relevance"},
                                "time_filter": {"type": "string", "default": "all"}
                            },
                            "required": ["query"]
                        }
                    },
                    {
                        "name": "get_subreddit_info",
                        "description": "Get detailed information about a subreddit",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "subreddit_name": {"type": "string"}
                            },
                            "required": ["subreddit_name"]
                        }
                    }
                ]
            }
        
        elif request.method == "POST":
            # Execute tool
            body = await request.json()
            tool_name = body.get("name")
            arguments = body.get("arguments", {})
            
            if tool_name == "get_subreddit_hot_posts":
                result = get_subreddit_hot_posts(**arguments)
            elif tool_name == "get_subreddit_trending_topics":
                result = get_subreddit_trending_topics(**arguments)
            elif tool_name == "compare_subreddits":
                result = compare_subreddits(**arguments)
            elif tool_name == "get_reddit_search":
                result = get_reddit_search(**arguments)
            elif tool_name == "get_subreddit_info":
                result = get_subreddit_info(**arguments)
            else:
                return {"error": f"Unknown tool: {tool_name}"}
            
            return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}
        
        else:
            return {"error": "Method not allowed"}
            
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    # For local development
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port) 