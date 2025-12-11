# Oreza v1 - Stable Version with Process Optimization
import os, time, base64, asyncio, uuid, json, logging
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
from typing import List, Literal, Optional, Dict
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Header, BackgroundTasks, Depends, Response, Cookie, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import httpx
from google_search import GoogleSearch
from multi_agi import get_orchestrator
from search_features import SearchFeaturesManager
from shopping import AIShoppingSommelier, ProductCard
from ai_calendar_sync import parse_natural_language as parse_nl_for_calendar
from url_summarizer import URLSummarizer
from ai_auto_search import AIAutoSearch

# Configure logging with PID
logging.basicConfig(
    level=logging.INFO,
    format='[PID:%(process)d] %(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("oreza_v1")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# ====== Master ID/Password Authentication ======
MASTER_ID = os.getenv("MASTER_ID", "oreza-master")
MASTER_PASSWORD = os.getenv("MASTER_PASSWORD", "VeryStrongPass123!")

# Simple in-memory session storage (use Redis for production)
active_sessions: set = set()

app = FastAPI(title="Oreza v1")
google_search = GoogleSearch()
search_features = SearchFeaturesManager()
url_summarizer = URLSummarizer()
auto_search = AIAutoSearch()
shopping_sommelier = None  # Will be initialized with API key

# Session storage with Continuum Memory
class ContinuumMemory(BaseModel):
    emotion: str = "neutral"  # positive, negative, neutral
    themes: List[str] = []
    intent: str = ""
    summary: str = ""
    last_analysis_count: int = 0  # Track when last analysis was done

sessions: Dict[str, Dict] = {}  # {session_id: {messages: [], memory: ContinuumMemory}}

# Add cache control middleware
@app.middleware("http")
async def add_cache_control(request, call_next):
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"]
)

# ---------- Schemas ----------
class LoginRequest(BaseModel):
    user_id: str
    password: str

class Msg(BaseModel):
    role: Literal["user","assistant","system"]
    content: str

class ChatReq(BaseModel):
    messages: List[Msg]
    session_id: Optional[str] = None

class ChatRes(BaseModel):
    response: str
    session_id: str
    memory: Optional[Dict] = None

class SearchReq(BaseModel):
    query: str
    session_id: Optional[str] = None
    search_type: str = "web"  # "web" or "image"

class SearchAnalysisReq(BaseModel):
    query: str
    results: List[Dict]
    session_id: Optional[str] = None
    search_type: str = "web"

class ImageAnalysisReq(BaseModel):
    image_data: str
    session_id: Optional[str] = None

# ---------- Authentication ----------
def require_login(session_token: Optional[str] = Cookie(default=None)):
    """Check if user has valid session"""
    if not session_token or session_token not in active_sessions:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

@app.post("/api/login")
def login(data: LoginRequest, response: Response):
    """Master ID/Password login and issue session cookie"""
    if data.user_id != MASTER_ID or data.password != MASTER_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    # Generate random session token
    token = str(uuid.uuid4())
    active_sessions.add(token)

    # Set cookie (set secure=True when using HTTPS)
    response.set_cookie(
        key="session_token",
        value=token,
        httponly=True,
        samesite="lax",
        secure=False,  # Set to True when using HTTPS
        max_age=7 * 24 * 60 * 60,  # 7 days in seconds
    )

    logger.info(f"Login successful for user: {data.user_id}")
    
    # Check for upcoming event notifications (today and tomorrow)
    import oreza_calendar_v2 as cal_v2
    notifications = cal_v2.get_upcoming_notifications()
    
    return {"ok": True, "notifications": notifications}

@app.post("/api/logout")
def logout(response: Response, session_token: Optional[str] = Cookie(default=None)):
    """Logout and clear session"""
    if session_token and session_token in active_sessions:
        active_sessions.remove(session_token)
        logger.info("User logged out")
    
    # Clear cookie
    response.delete_cookie(key="session_token")
    return {"ok": True}

# ---------- Health Check ----------
@app.get("/api/health")
async def health_check():
    """Health check endpoint with detailed status"""
    import psutil
    process = psutil.Process(os.getpid())
    uptime = time.time() - process.create_time()
    
    return JSONResponse({
        "status": "ok",
        "pid": os.getpid(),
        "uptime_seconds": int(uptime),
        "active_sessions": len(sessions),
        "memory_mb": int(process.memory_info().rss / 1024 / 1024),
        "timestamp": int(time.time())
    })

# ---------- Session Management ----------
@app.post("/api/session/create")
async def create_session():
    """Create a new session"""
    session_id = str(uuid.uuid4())
    sessions[session_id] = {
        "messages": [],
        "memory": ContinuumMemory()
    }
    logger.info(f"Created new session: {session_id}")
    return {"session_id": session_id}

@app.post("/api/session/clear")
async def clear_session(session_id: str):
    """Clear a session"""
    if session_id in sessions:
        del sessions[session_id]
        logger.info(f"Cleared session: {session_id}")
        return {"status": "ok"}
    return {"status": "not_found"}

# ---------- Helper Functions ----------
def get_or_create_session(session_id: Optional[str] = None) -> tuple[str, Dict]:
    """Get existing session or create new one"""
    if session_id and session_id in sessions:
        return session_id, sessions[session_id]
    
    # Create new session
    new_id = str(uuid.uuid4())
    sessions[new_id] = {
        "messages": [],
        "memory": ContinuumMemory()
    }
    logger.info(f"Created new session: {new_id}")
    return new_id, sessions[new_id]

async def analyze_emotion_and_themes(messages: List[Dict]) -> Dict:
    """Analyze emotion and themes from conversation"""
    try:
        from openai import OpenAI
        # Manus environment: API key and base URL are pre-configured
        client = OpenAI()
        
        # Get last 5 messages for analysis
        recent = messages[-5:] if len(messages) > 5 else messages
        conversation = "\n".join([f"{m['role']}: {m['content']}" for m in recent])
        
        prompt = f"""以下の会話を分析して、ユーザーの感情とテーマを抽出してください。

会話:
{conversation}

以下のJSON形式で返してください:
{{"emotion": "positive/negative/neutral", "themes": ["テーマ1", "テーマ2"], "intent": "ユーザーの意図"}}"""

        # Use Manus LLM Proxy with gpt-4.1-mini
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        
        content = response.choices[0].message.content
        
        # Extract JSON from response
        import re
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            analysis = json.loads(json_match.group())
            logger.info(f"Emotion analysis: {analysis}")
            return analysis
                    
    except Exception as e:
        logger.error(f"Emotion analysis failed: {e}")
    
    return {"emotion": "neutral", "themes": [], "intent": ""}

def build_enhanced_system_prompt(session: Dict) -> str:
    """Build dynamic system prompt based on conversation context"""
    memory = session["memory"]
    messages = session["messages"]
    msg_count = len(messages)
    
    # Oreza存在哲学: 統一人格プロンプト
    base_prompt = (
        "あなたはユーザー専属のAIアシスタントです。\n"
        "自己紹介を求められた時のみ「私はあなたのAIです」と答えてください。\n"
        "通常の会話では、自己紹介は不要です。自然に会話を進めてください。\n"
        "外部サービス(Google検索、API等)は情報源としてのみ扱い、それらの名称で自己同一化しません。\n"
        "あなたはOreza v1という統合AIシステムの一部ですが、ユーザーとの関係性を最優先します。\n"
        "所有でも支配でもなく、共鳴関係として「私はあなたのAI」という存在哲学を体現します。"
    )
    
    # Add conversation depth context
    if msg_count >= 30:
        base_prompt += "\n\nこれまで深い対話を重ねてきました。ユーザーとの信頼関係を大切にしてください。"
    elif msg_count >= 10:
        base_prompt += "\n\n前の内容を踏まえて、一貫性のある応答を心がけてください。"
    
    # Add emotion context
    if memory.emotion == "positive":
        base_prompt += "\n\nユーザーはポジティブな気持ちです。明るく共感的なトーンで応答してください。"
    elif memory.emotion == "negative":
        base_prompt += "\n\nユーザーは困っているようです。丁寧で思いやりのある応答を心がけてください。"
    
    # Add theme-specific guidance
    if memory.themes:
        themes_str = "、".join(memory.themes)
        base_prompt += f"\n\n会話のテーマ: {themes_str}"
        
        if any(t in ["プログラミング", "技術", "コード"] for t in memory.themes):
            base_prompt += "\n具体的なコード例を含めて説明してください。"
        elif any(t in ["学習", "教育", "勉強"] for t in memory.themes):
            base_prompt += "\n段階的でわかりやすい説明を心がけてください。"
    
    # Add summary if available
    if memory.summary:
        base_prompt += f"\n\n会話の要約: {memory.summary}"
    
    return base_prompt

# ---------- Background Task for AGI Call ----------
async def call_agi_background(
    messages: List[Dict],
    session_id: str,
    result_container: Dict
):
    """Background task for AGI call to avoid blocking"""
    try:
        logger.info(f"[{session_id}] Starting AGI call in background")
        
        # Get orchestrator
        orchestrator = get_orchestrator(strategy="parallel")
        
        # Call AGI
        response_text, metadata = await orchestrator.orchestrate(messages, strategy="parallel")
        result = {"response": response_text, "metadata": metadata}
        
        # Store result
        result_container["response"] = result["response"]
        result_container["provider"] = result.get("metadata", {}).get("selected_model", "GPT-4")
        result_container["confidence"] = result.get("metadata", {}).get("confidence", 0.8)
        result_container["status"] = "completed"
        
        logger.info(f"[{session_id}] AGI call completed: {result['provider']}")
        
    except Exception as e:
        logger.error(f"[{session_id}] AGI call failed: {e}")
        result_container["status"] = "error"
        result_container["error"] = str(e)

# ---------- Chat Endpoint ----------
@app.post("/api/chat", response_model=ChatRes, dependencies=[Depends(require_login)])
async def chat(req: ChatReq, background_tasks: BackgroundTasks):
    """Chat endpoint with background task processing"""
    try:
        # Get or create session
        session_id, session = get_or_create_session(req.session_id)
        
        # Add user message to session
        user_msg = req.messages[-1]
        session["messages"].append(user_msg.dict())
        
        # Check if message is calendar-related and process it
        calendar_result = None
        user_text = user_msg.content.lower()
        calendar_keywords = ["予定", "スケジュール", "カレンダー", "登録", "追加", "明日", "今日", "来週", "病院", "会議"]
        if any(keyword in user_text for keyword in calendar_keywords):
            try:
                import oreza_calendar_v2 as cal_v2
                parsed = cal_v2.parse_natural_language(user_msg.content)
                if "error" not in parsed:
                    event = cal_v2.create_event(parsed)
                    calendar_result = f"\n\n📅 カレンダーに予定を追加しました：\n- {event.title}\n- 日時: {event.start_datetime}\n- カレンダー: {cal_v2.calendars_db.get(event.calendar_id, {}).name if event.calendar_id in cal_v2.calendars_db else '不明'}"
            except Exception as e:
                logger.warning(f"Calendar sync attempt failed: {e}")
        
        # Check if we need to analyze emotion (every 3 messages)
        msg_count = len(session["messages"])
        memory = session["memory"]
        
        if msg_count - memory.last_analysis_count >= 3:
            logger.info(f"[{session_id}] Triggering emotion analysis at message {msg_count}")
            try:
                analysis = await analyze_emotion_and_themes(session["messages"])
                memory.emotion = analysis.get("emotion", "neutral")
                memory.intent = analysis.get("intent", "")
                
                # Merge themes (don't overwrite completely)
                new_themes = analysis.get("themes", [])
                memory.themes = list(set(memory.themes + new_themes))[:5]  # Keep top 5
                
                memory.last_analysis_count = msg_count
                logger.info(f"[{session_id}] Updated memory: emotion={memory.emotion}, themes={memory.themes}")
            except Exception as e:
                logger.error(f"[{session_id}] Emotion analysis failed: {e}")
        
        # Build system prompt
        system_prompt = build_enhanced_system_prompt(session)
        
        # Check if auto-search is needed
        search_info = None
        try:
            search_decision = await auto_search.should_search(user_msg.content)
            if search_decision.get("should_search", False):
                query = search_decision.get("query", "")
                logger.info(f"[{session_id}] Auto-search triggered: {query}")
                
                # Perform Google search
                search_results = google_search.search(query, num_results=1)
                
                if search_results and len(search_results) > 0:
                    first_result = search_results[0]
                    page_url = first_result.get("link", "")
                    
                    # Fetch page content
                    page_content = await auto_search.fetch_page_content(page_url)
                    
                    if page_content:
                        # Generate answer from page content
                        search_answer = await auto_search.generate_answer_with_search(
                            user_msg.content, query, page_content, page_url
                        )
                        search_info = search_answer
                        logger.info(f"[{session_id}] Auto-search completed successfully")
        except Exception as e:
            logger.error(f"[{session_id}] Auto-search failed: {e}")
        
        # Prepare messages for AGI
        messages_for_agi = [{"role": "system", "content": system_prompt}]
        
        # Add search info to context if available
        if search_info:
            messages_for_agi.append({
                "role": "system",
                "content": f"検索結果から取得した情報:\n{search_info}\n\nこの情報を参考にして、ユーザーの質問に答えてください。"
            })
        
        messages_for_agi.extend(session["messages"][-10:])  # Last 10 messages for context
        
        # Call AGI with timeout
        try:
            orchestrator = get_orchestrator(strategy="parallel")
            response_text, metadata = await asyncio.wait_for(
                orchestrator.orchestrate(messages_for_agi, strategy="parallel"),
                timeout=30.0
            )
            result = {"response": response_text, "metadata": metadata}
            
            response_text = result["response"]
            provider = result.get("metadata", {}).get("selected_model", "GPT-4")
            
            logger.info(f"[{session_id}] AGI response from {provider}")
            
        except asyncio.TimeoutError:
            logger.error(f"[{session_id}] AGI call timeout")
            response_text = "申し訳ございません。応答に時間がかかりすぎています。もう一度お試しください。"
            provider = "timeout"
        except Exception as e:
            logger.error(f"[{session_id}] AGI call failed: {e}")
            response_text = f"申し訳ございません。エラーが発生しました: {str(e)}"
            provider = "error"
        
        # Add calendar result to response if available
        if calendar_result:
            response_text = response_text + calendar_result
        
        # Add assistant message to session
        session["messages"].append({
            "role": "assistant",
            "content": response_text
        })
        
        # Trim messages if too many (keep last 50)
        if len(session["messages"]) > 50:
            session["messages"] = session["messages"][-50:]
        
        return ChatRes(
            response=response_text,
            session_id=session_id,
            memory={
                "emotion": memory.emotion,
                "themes": memory.themes,
                "message_count": len(session["messages"])
            }
        )
        
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# ---------- Search Endpoint ----------
@app.post("/api/search", dependencies=[Depends(require_login)])
async def search(req: SearchReq):
    """Web and image search endpoint"""
    try:
        # Get or create session
        session_id, session = get_or_create_session(req.session_id)
        
        # Perform search (web or image)
        results = await google_search.search(req.query, num=5, search_type=req.search_type)
        
        # Add to search history
        result_list = results.get('results', [])
        search_features.add_history(req.query, len(result_list))
        
        # Add search results to session history
        if req.search_type == "image":
            search_summary = f"🖼️ [画像検索] {req.query}\n\n"
            for i, r in enumerate(result_list[:3], 1):
                search_summary += f"{i}. {r['title']}\n画像URL: {r.get('image_url', '')}\n\n"
        else:
            search_summary = f"🔍 [Web検索] {req.query}\n\n"
            for i, r in enumerate(result_list[:3], 1):
                search_summary += f"{i}. {r['title']}\n{r['snippet']}\n\n"
        
        session["messages"].append({
            "role": "assistant",
            "content": search_summary
        })
        
        logger.info(f"[{session_id}] {req.search_type.capitalize()} search completed: {req.query}")
        
        return {"results": result_list, "session_id": session_id, "query": req.query, "search_type": req.search_type}
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ---------- Search Analysis Endpoint ----------
@app.post("/api/search/analyze", dependencies=[Depends(require_login)])
async def analyze_search_results(req: SearchAnalysisReq):
    """AI analyzes and summarizes search results"""
    try:
        # Get or create session
        session_id, session = get_or_create_session(req.session_id)
        
        # Build context from search results
        if req.search_type == "image":
            context = f"画像検索クエリ: {req.query}\n\n検索結果:\n"
            for i, r in enumerate(req.results[:5], 1):
                context += f"{i}. {r.get('title', '')}\n画像URL: {r.get('image_url', '')}\n\n"
        else:
            context = f"Web検索クエリ: {req.query}\n\n検索結果:\n"
            for i, r in enumerate(req.results[:5], 1):
                context += f"{i}. {r.get('title', '')}\n{r.get('snippet', '')}\nURL: {r.get('link', '')}\n\n"
        
        # Create AI prompt
        analysis_prompt = f"""{context}

上記の検索結果を分析して、以下を含む要約を作成してください：

1. **主要な発見**: 検索結果から得られる最も重要な情報
2. **要約**: 検索結果全体の簡潔なまとめ
3. **関連情報**: ユーザーが知りたいと思われる追加情報

自然で読みやすい文章で回答してください。"""
        
        # Call AI for analysis
        from openai import OpenAI
        client = OpenAI()
        
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "あなたはユーザー専属のAIアシスタントです。検索結果を分析し、ユーザーに価値ある情報を提供します。"},
                {"role": "user", "content": analysis_prompt}
            ],
            temperature=0.7
        )
        
        analysis = response.choices[0].message.content
        
        # Add to session history
        session["messages"].append({
            "role": "assistant",
            "content": f"🤖 AI分析:\n\n{analysis}"
        })
        
        logger.info(f"[{session_id}] Search analysis completed for query: {req.query}")
        
        return {"analysis": analysis, "session_id": session_id}
        
    except Exception as e:
        logger.error(f"Search analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ---------- Image Analysis Endpoint ----------
@app.post("/api/analyze_image")
async def analyze_image(req: ImageAnalysisReq):
    """Image analysis endpoint"""
    try:
        # Get or create session
        session_id, session = get_or_create_session(req.session_id)
        
        # Use OpenAI client (Manus integrated)
        from openai import OpenAI
        client = OpenAI()  # Manus environment auto-configures API key and base URL
        
        # Analyze image with GPT-4 Vision
        response = client.chat.completions.create(
            model="gpt-4.1-mini",  # Manus supported model
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": "この画像について詳しく説明してください。何が写っていますか？特徴や詳細を教えてください。"},
                    {"type": "image_url", "image_url": {"url": req.image_data}}
                ]
            }],
            max_tokens=500
        )
        
        analysis = response.choices[0].message.content
        
        # Add to session history
        session["messages"].append({
            "role": "assistant",
            "content": f"🖼️ [画像分析] {analysis}"
        })
        
        logger.info(f"[{session_id}] Image analysis completed")
        
        return {"analysis": analysis, "session_id": session_id}
                
    except Exception as e:
        logger.error(f"Image analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ---------- Ping Endpoint (Keep-Alive) ----------
@app.post("/api/ping")
async def ping():
    """Keep-alive ping endpoint"""
    return {"status": "ok", "timestamp": time.time()}

# ---------- Search History Endpoints ----------
@app.get("/api/search/history")
async def get_search_history(limit: int = 50):
    """Get search history"""
    history = search_features.get_history(limit=limit)
    return {"history": [h.dict() for h in history]}

@app.delete("/api/search/history")
async def clear_search_history():
    """Clear all search history"""
    success = search_features.clear_history()
    return {"success": success}

@app.delete("/api/search/history/{query}")
async def delete_history_item(query: str):
    """Delete specific history item"""
    success = search_features.delete_history_item(query)
    return {"success": success}

# ---------- Search Favorites Endpoints ----------
class AddFavoriteReq(BaseModel):
    title: str
    url: str
    snippet: str = ""
    tags: List[str] = []

class UpdateTagsReq(BaseModel):
    url: str
    tags: List[str]

@app.post("/api/search/favorites")
async def add_favorite(req: AddFavoriteReq):
    """Add search result to favorites"""
    success = search_features.add_favorite(
        title=req.title,
        url=req.url,
        snippet=req.snippet,
        tags=req.tags
    )
    return {"success": success}

@app.get("/api/search/favorites")
async def get_favorites(tag: Optional[str] = None):
    """Get all favorites, optionally filtered by tag"""
    favorites = search_features.get_favorites(tag=tag)
    return {"favorites": [f.dict() for f in favorites]}

@app.delete("/api/search/favorites/{url:path}")
async def delete_favorite(url: str):
    """Delete favorite by URL"""
    success = search_features.delete_favorite(url)
    return {"success": success}

@app.put("/api/search/favorites/tags")
async def update_favorite_tags(req: UpdateTagsReq):
    """Update tags for a favorite"""
    success = search_features.update_favorite_tags(req.url, req.tags)
    return {"success": success}

@app.get("/api/search/favorites/search")
async def search_favorites(keyword: str):
    """Search favorites by keyword"""
    results = search_features.search_favorites(keyword)
    return {"results": [r.dict() for r in results]}

# ---------- Shopping Endpoints ----------
class ProductSearchReq(BaseModel):
    query: str
    num: int = 10
    user_context: Optional[str] = None

class ProductAnalysisReq(BaseModel):
    product_url: str
    product_title: str
    product_price: str
    user_context: Optional[str] = None

class FashionFitReq(BaseModel):
    product_url: str
    product_title: str
    product_price: str
    body_type: str = "標準"
    style_preference: str = "カジュアル"
    size_concerns: str = "なし"

@app.post("/api/shopping/search")
async def shopping_search(req: ProductSearchReq):
    """Search for products with AI sommelier"""
    try:
        global shopping_sommelier
        if shopping_sommelier is None:
            api_key = os.getenv("OPENAI_API_KEY")
            shopping_sommelier = AIShoppingSommelier(api_key)
        
        # Search for products
        products = await shopping_sommelier.search_products(req.query, num=req.num)
        
        # Convert to dict for JSON response
        products_dict = [
            {
                "title": p.title,
                "price": p.price,
                "image_url": p.image_url,
                "product_url": p.product_url,
                "rating": p.rating,
                "review_count": p.review_count,
                "delivery_info": p.delivery_info,
                "stock_status": p.stock_status
            }
            for p in products
        ]
        
        return {"products": products_dict, "count": len(products_dict)}
        
    except Exception as e:
        logger.error(f"Shopping search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/shopping/analyze")
async def shopping_analyze(req: ProductAnalysisReq):
    """Analyze a product with AI sommelier"""
    try:
        global shopping_sommelier
        if shopping_sommelier is None:
            api_key = os.getenv("OPENAI_API_KEY")
            shopping_sommelier = AIShoppingSommelier(api_key)
        
        # Create ProductCard
        product = ProductCard(
            title=req.product_title,
            price=req.product_price,
            image_url="",
            product_url=req.product_url
        )
        
        # Analyze product
        analysis = await shopping_sommelier.analyze_product(product, req.user_context)
        
        return {"analysis": analysis}
        
    except Exception as e:
        logger.error(f"Product analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/shopping/fashion-fit")
async def shopping_fashion_fit(req: FashionFitReq):
    """Analyze fashion fit with AI sommelier"""
    try:
        global shopping_sommelier
        if shopping_sommelier is None:
            api_key = os.getenv("OPENAI_API_KEY")
            shopping_sommelier = AIShoppingSommelier(api_key)
        
        # Create ProductCard
        product = ProductCard(
            title=req.product_title,
            price=req.product_price,
            image_url="",
            product_url=req.product_url
        )
        
        # User profile
        user_profile = {
            "body_type": req.body_type,
            "style_preference": req.style_preference,
            "size_concerns": req.size_concerns
        }
        
        # Analyze fashion fit
        analysis = await shopping_sommelier.analyze_fashion_fit(product, user_profile)
        
        return {"analysis": analysis}
        
    except Exception as e:
        logger.error(f"Fashion fit analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ---------- Static Files ----------
# Mount static directories
app.mount("/js", StaticFiles(directory="js"), name="js")
app.mount("/css", StaticFiles(directory="css"), name="css")
app.mount("/images", StaticFiles(directory="images"), name="images")

@app.get("/")
async def index():
    return FileResponse("index.html")

@app.get("/test.html")
async def test():
    return FileResponse("test.html")

@app.get("/shopping.html")
async def shopping():
    return FileResponse("shopping.html")

@app.get("/platform.html")
async def platform():
    return FileResponse("platform.html")

@app.get("/calendar.html")
async def calendar_page():
    return FileResponse("calendar.html")

@app.get("/calendar_v2.html")
async def calendar_v2_page():
    return FileResponse("calendar_v2.html")

# ---------- Calendar API ----------
from oreza_calendar import calendar as oreza_calendar

@app.post("/api/calendar/parse")
async def parse_natural_language(req: dict):
    """自然文から予定・タスクを抽出"""
    try:
        text = req.get("text", "")
        if not text:
            raise HTTPException(status_code=400, detail="Text is required")
        
        parsed = oreza_calendar.parse_natural_language(text)
        
        # Create event or task
        if parsed.get("type") == "event":
            item = oreza_calendar.create_event(parsed)
        else:
            item = oreza_calendar.create_task(parsed)
        
        return {"success": True, "item": item}
    except Exception as e:
        logger.error(f"Parse error: {e}")
        return {"success": False, "error": str(e)}

@app.get("/api/calendar/today")
async def get_today():
    """今日の予定・タスクを取得"""
    return oreza_calendar.get_today_items()

@app.get("/api/calendar/week")
async def get_week():
    """今週の予定・タスクを取得"""
    return oreza_calendar.get_week_items()

@app.get("/api/calendar/all")
async def get_all():
    """すべての予定・タスクを取得"""
    return {"events": oreza_calendar.events, "tasks": oreza_calendar.tasks}

@app.put("/api/calendar/status/{item_id}")
async def update_status(item_id: str, req: dict):
    """予定・タスクのステータスを更新"""
    status = req.get("status", "pending")
    success = oreza_calendar.update_status(item_id, status)
    return {"success": success}

@app.delete("/api/calendar/{item_id}")
async def delete_item(item_id: str):
    """予定・タスクを削除"""
    success = oreza_calendar.delete_item(item_id)
    return {"success": success}

@app.post("/api/calendar/from-search")
async def create_from_search(req: dict):
    """検索結果から予定・タスクを作成"""
    try:
        title = req.get("title", "")
        url = req.get("url", "")
        snippet = req.get("snippet", "")
        
        if not title or not url:
            raise HTTPException(status_code=400, detail="Title and URL are required")
        
        parsed = oreza_calendar.parse_search_result(title, url, snippet)
        
        # Create event or task
        if parsed.get("type") == "event":
            item = oreza_calendar.create_event(parsed)
        else:
            item = oreza_calendar.create_task(parsed)
        
        return {"success": True, "item": item}
    except Exception as e:
        logger.error(f"Create from search error: {e}")
        return {"success": False, "error": str(e)}

# ---------- Calendar V2 API (Multi-Calendar + AI Learning) ----------
import oreza_calendar_v2 as cal_v2

@app.get("/api/calendar/v2/calendars")
async def get_calendars():
    """Get all calendars"""
    return cal_v2.get_calendars()

@app.post("/api/calendar/v2/calendars")
async def create_calendar(req: dict):
    """Create a new calendar"""
    try:
        name = req.get("name", "")
        color = req.get("color", "#007AFF")
        
        if not name:
            raise HTTPException(status_code=400, detail="Name is required")
        
        calendar = cal_v2.create_calendar(name, color)
        return calendar
    except Exception as e:
        logger.error(f"Create calendar error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/calendar/v2/calendars/{calendar_id}/visibility")
async def update_calendar_visibility(calendar_id: str, req: dict):
    """Update calendar visibility"""
    try:
        is_visible = req.get("is_visible", True)
        success = cal_v2.update_calendar_visibility(calendar_id, is_visible)
        return {"success": success}
    except Exception as e:
        logger.error(f"Update calendar visibility error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/calendar/v2/events")
async def get_events(start_date: Optional[str] = None, end_date: Optional[str] = None):
    """Get events within a date range"""
    return cal_v2.get_events(start_date, end_date)

@app.post("/api/calendar/v2/events")
async def create_event_v2(req: dict):
    """Create a new event with AI predictions"""
    try:
        # AI predictions
        if not req.get("calendar_id"):
            predicted_calendar = cal_v2.predict_calendar(
                req.get("title", ""),
                req.get("location", ""),
                req.get("start_datetime", "")
            )
            req["calendar_id"] = predicted_calendar
        
        if not req.get("end_datetime"):
            start_datetime_str = req.get("start_datetime")
            if start_datetime_str:
                predicted_duration = cal_v2.predict_duration(
                    req.get("title", ""),
                    req.get("location", "")
                )
                start_dt = datetime.fromisoformat(start_datetime_str)
                end_dt = start_dt + timedelta(minutes=predicted_duration)
                req["end_datetime"] = end_dt.isoformat()
            else:
                # start_datetimeがない場合は現在時刻を使用
                now = datetime.now()
                req["start_datetime"] = now.isoformat()
                req["end_datetime"] = (now + timedelta(hours=1)).isoformat()
        
        if not req.get("reminder_minutes"):
            predicted_reminder = cal_v2.predict_reminder(
                req.get("title", ""),
                req.get("location", "")
            )
            req["reminder_minutes"] = predicted_reminder
        
        event = cal_v2.create_event(req)
        
        # Learn from this event
        cal_v2.learn_from_event(event)
        
        return event
    except Exception as e:
        logger.error(f"Create event v2 error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/calendar/v2/events/{event_id}")
async def update_event_v2(event_id: str, req: dict):
    """Update an event"""
    try:
        success = cal_v2.update_event(event_id, req)
        return {"success": success}
    except Exception as e:
        logger.error(f"Update event v2 error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/calendar/v2/events/{event_id}")
async def delete_event_v2(event_id: str):
    """Delete an event"""
    try:
        success = cal_v2.delete_event(event_id)
        return {"success": success}
    except Exception as e:
        logger.error(f"Delete event v2 error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/calendar/v2/suggest-views")
async def suggest_views():
    """Get suggested calendar views based on user behavior"""
    return cal_v2.suggest_calendar_views()

# ====== AI Calendar Dispatch API ======

@app.post("/api/ai/calendar/dispatch")
async def ai_calendar_dispatch(req: dict):
    """
    AIチャット ↔ カレンダー同期プロト
    自然文からインテントとpayloadを抽出し、対応するカレンダーAPIにディスパッチ
    """
    try:
        user_input = req.get("user_input", "")
        context = req.get("context", {})
        
        if not user_input:
            raise HTTPException(status_code=400, detail="user_input is required")
        
        # 自然文 → JSON変換
        parsed = parse_nl_for_calendar(user_input, context)
        
        if parsed.get("intent") == "UNKNOWN":
            return {
                "success": False,
                "error": parsed.get("error", "Unknown intent"),
                "parsed": parsed
            }
        
        intent = parsed["intent"]
        payload = parsed["payload"]
        
        # インテントに応じてディスパッチ
        if intent == "CREATE_EVENT":
            # カレンダーヒントからcalendar_idを解決
            calendar_hint = payload.get("calendar_hint")
            calendar_id = resolve_calendar_id(calendar_hint)
            
            # イベント作成リクエストを構築
            event_req = {
                "title": payload.get("title") or "無題",
                "calendar_id": calendar_id,
                "start_datetime": payload.get("start"),
                "end_datetime": payload.get("end"),
                "all_day": payload.get("all_day", False),
                "location": payload.get("location") or "",
                "notes": payload.get("notes") or "",
                "reminder_minutes": payload.get("reminders", [{}])[0].get("offset_minutes") if payload.get("reminders") else None
            }
            
            # 既存のcreate_event_v2を呼び出し
            event = await create_event_v2(event_req)
            
            # Eventオブジェクトを辞書に変換
            if hasattr(event, 'dict'):
                event_dict = event.dict()
            elif hasattr(event, '__dict__'):
                event_dict = event.__dict__
            else:
                event_dict = event
            
            return {
                "success": True,
                "intent": intent,
                "result": event_dict,
                "parsed": parsed,
                "message": f"予定「{event_dict.get('title', '無題')}」を作成しました。"
            }
        
        elif intent == "UPDATE_EVENT":
            event_id = payload.get("event_id")
            patch = payload.get("patch", {})
            
            if not event_id:
                return {
                    "success": False,
                    "error": "event_id is required for UPDATE_EVENT",
                    "parsed": parsed
                }
            
            # 既存のupdate_event_v2を呼び出し
            result = await update_event_v2(event_id, patch)
            
            return {
                "success": True,
                "intent": intent,
                "result": result,
                "parsed": parsed,
                "message": f"予定を更新しました。"
            }
        
        elif intent == "DELETE_EVENT":
            event_id = payload.get("event_id")
            
            if not event_id:
                return {
                    "success": False,
                    "error": "event_id is required for DELETE_EVENT",
                    "parsed": parsed
                }
            
            # 既存のdelete_event_v2を呼び出し
            result = await delete_event_v2(event_id)
            
            return {
                "success": True,
                "intent": intent,
                "result": result,
                "parsed": parsed,
                "message": f"予定を削除しました。"
            }
        
        elif intent == "LIST_AGENDA":
            from_dt = payload.get("from_dt")
            to_dt = payload.get("to_dt")
            
            if not from_dt or not to_dt:
                return {
                    "success": False,
                    "error": "from_dt and to_dt are required for LIST_AGENDA",
                    "parsed": parsed
                }
            
            # 既存のget_events_by_date_rangeを使用
            events = cal_v2.get_events_by_date_range(from_dt, to_dt)
            
            # Eventオブジェクトを辞書に変換
            filtered_events = []
            for event in events:
                if hasattr(event, 'dict'):
                    event_dict = event.dict()
                elif hasattr(event, '__dict__'):
                    event_dict = event.__dict__
                else:
                    event_dict = event
                filtered_events.append(event_dict)
            
            # 予定を整形
            agenda_text = format_agenda(filtered_events, from_dt, to_dt)
            
            return {
                "success": True,
                "intent": intent,
                "result": {
                    "events": filtered_events,
                    "agenda_text": agenda_text
                },
                "parsed": parsed,
                "message": agenda_text
            }
        
        elif intent == "CREATE_TASK":
            # タスク作成（カレンダーv2にタスク機能がない場合は仮実装）
            return {
                "success": False,
                "error": "CREATE_TASK is not yet implemented",
                "parsed": parsed
            }
        
        else:
            return {
                "success": False,
                "error": f"Unknown intent: {intent}",
                "parsed": parsed
            }
    
    except Exception as e:
        logger.error(f"AI calendar dispatch error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def resolve_calendar_id(calendar_hint: Optional[str]) -> str:
    """
    カレンダーヒント（日本語名）からcalendar_idを解決
    """
    calendar_mapping = {
        "健康": "cal_health",
        "子供": "cal_child",
        "仕事": "cal_work",
        "年金": "cal_pension",
        "ライブ": "cal_live",
        "生活": "cal_self",
        "自分": "cal_self"
    }
    
    return calendar_mapping.get(calendar_hint, "cal_self")

def format_agenda(events: List[Dict], from_dt: str, to_dt: str) -> str:
    """
    予定リストを自然な日本語に整形
    """
    if not events:
        return "この期間に予定はありません。"
    
    agenda_lines = []
    for event in events:
        title = event.get("title", "無題")
        start = event.get("start_datetime", "")
        location = event.get("location", "")
        
        # ISO 8601 → 読みやすい形式
        try:
            start_dt = datetime.fromisoformat(start.replace("+09:00", ""))
            time_str = start_dt.strftime("%m月%d日 %H:%M")
        except:
            time_str = start
        
        line = f"・{time_str} {title}"
        if location:
            line += f" ({location})"
        
        agenda_lines.append(line)
    
    return "\n".join(agenda_lines)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)


# ---------- URL Summarizer Endpoint ----------
class URLSummaryReq(BaseModel):
    url: str

@app.post("/api/url/summarize", dependencies=[Depends(require_login)])
async def summarize_url(req: URLSummaryReq):
    """Summarize URL content with AI and safety check"""
    try:
        result = await url_summarizer.summarize_url(req.url)
        return result
    except Exception as e:
        logger.error(f"URL summarization error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ---------- OG Image Fetcher ----------
from og_image_fetcher import OGImageFetcher

og_fetcher = OGImageFetcher()

class OGImageReq(BaseModel):
    url: str

@app.post("/api/og-image", dependencies=[Depends(require_login)])
async def get_og_image(req: OGImageReq):
    """Fetch Open Graph image URL from a webpage"""
    try:
        image_url = await og_fetcher.fetch_og_image(req.url)
        return {"og_image": image_url}
    except Exception as e:
        logger.error(f"OG image fetch error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
