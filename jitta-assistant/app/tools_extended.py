import httpx
from typing import Optional, Dict, Any, List
import json
import logging
from duckduckgo_search import DDGS

logger = logging.getLogger(__name__)

# --- External Connectivity Tools ---

async def search_web(query: str, max_results: int = 5) -> str:
    """
    Search the web using DuckDuckGo.
    Returns a markdown formatted list of results.
    """
    try:
        results = ""
        with DDGS() as ddgs:
            # text() returns an iterator
            search_gen = ddgs.text(query, max_results=max_results)
            for i, r in enumerate(search_gen, 1):
                results += f"{i}. [{r['title']}]({r['href']})\n   {r['body']}\n\n"
        
        if not results:
            return "No results found."
        
        return f"Build-in Web Search Results for '{query}':\n\n{results}"
    except Exception as e:
        logger.error(f"Search failed: {e}")
        return f"Error performing web search: {str(e)}"

async def visit_page(url: str) -> str:
    """
    Visit a webpage and extract main text content.
    """
    # Simple validation
    if not url.startswith(("http://", "https://")):
        return "Error: Invalid URL scheme. Use http or https."
    
    # Filter dangerous/blocked domains here if needed (could rely on safety.py too)
    
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        async with httpx.AsyncClient(follow_redirects=True, verify=False) as client:
            resp = await client.get(url, headers=headers, timeout=15.0)
            resp.raise_for_status()
            
            # Basic text extraction
            # If complex parsing is needed, import bs4 inside the function or file
            # Since tools.py imports bs4, we assume it's available.
            try:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(resp.text, 'html.parser')
                
                # Remove scripts and styles
                for script in soup(["script", "style"]):
                    script.extract()
                
                text = soup.get_text()
                
                # Compress whitespace
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                text = '\n'.join(chunk for chunk in chunks if chunk)
                
                return f"Content of {url}:\n\n{text[:4000]}..." # Truncate to avoid context limit
            except ImportError:
                return f"Error: BeautifulSoup not installed. Raw content len: {len(resp.text)}"
                
    except Exception as e:
        logger.error(f"Visit page failed: {e}")
        return f"Error visiting page: {str(e)}"

async def consult_expert_ai(prompt: str) -> str:
    """
    Consult the Expert AI (Quality Model) for complex reasoning or creative tasks.
    """
    # This is a meta-tool that allows the assistant to 'think' using the bigger model
    # even if it's currently running in 'fast' mode, or to explicitly use a different persona.
    # For now, it just loops back to the quality model endpoint.
    return f"[Expert Advice] Please proceed with: {prompt}" # Placeholder, handled by orchestrator loop effectively

# --- Crypto Tools ---

async def get_crypto_price(coin_id: str = "bitcoin", vs_currency: str = "usd") -> str:
    """Fetch current price of a cryptocurrency from CoinGecko."""
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies={vs_currency}&include_market_cap=true&include_24hr_vol=true&include_24hr_change=true"
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(url, timeout=10.0)
            resp.raise_for_status()
            data = resp.json()
            if not data:
                return f"Could not find data for {coin_id}."
            return json.dumps(data, indent=2)
        except Exception as e:
            logger.error(f"Error fetching crypto price: {e}")
            return f"Error fetching crypto price: {str(e)}"

async def get_crypto_trends() -> str:
    """Fetch trending coins on CoinGecko."""
    url = "https://api.coingecko.com/api/v3/search/trending"
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(url, timeout=10.0)
            resp.raise_for_status()
            data = resp.json()
            coins = [item['item']['name'] for item in data.get('coins', [])]
            return f"Trending coins: {', '.join(coins)}"
        except Exception as e:
            return f"Error fetching trends: {str(e)}"

# --- Social Media / Marketing Tools ---

# In a real scenario, this would use Graph API with user tokens.
# For now, we simulate the capability structure.

async def post_to_facebook(content: str, token: Optional[str] = None) -> str:
    """
    Post content to Facebook feed.
    Requires a valid Page Access Token.
    """
    if not token:
        # Check environment or config in real app
        return "Facebook Access Token not configured. Using dry-run mode:\n[MOCK] Posted to Facebook: " + content
    
    # Real implementation would be:
    # url = f"https://graph.facebook.com/v19.0/me/feed?access_token={token}"
    # async with httpx.AsyncClient() as client:
    #     resp = await client.post(url, json={"message": content})
    #     return resp.text
    return "[MOCK] Posted to Facebook (Token provided): " + content

async def comment_on_post(post_id: str, message: str, token: Optional[str] = None) -> str:
    if not token:
        return f"[MOCK] Commented on post {post_id}: {message}"
    return f"[MOCK] Commented on post {post_id} with token: {message}"

async def analyze_comments(post_id: str, limit: int = 5) -> str:
    """
    Fetch and analyze comments (Mock).
    """
    # Mock data
    comments = [
        "Great post!",
        "I disagree with the second point.",
        "How much is this?",
        "Interesting perspective.",
        "Can you share more info?"
    ]
    return f"Analyzed {len(comments)} comments on {post_id}. Sentiment: Mixed-Positive. Top request: More info."


# --- Digital Mind Integration (Phase 3) ---

async def ask_digital_mind(task: str, payload: dict) -> str:
    """
    Interact with the Digital Mind Model (DMM Backend) via HTTP APIs.
    
    Supported Tasks:
    - "simulate_scenario": POST /api/simulation/simulate
    - "process_mind_moment": POST /api/citta-vithi/process
    - "get_scenarios": GET /api/simulation/scenarios
    - "health_check": GET /health

    Args:
        task: The action to perform.
        payload: JSON dictionary containing request parameters.
    """
    base_url = "http://localhost:8000"
    endpoints = {
        "simulate_scenario": ("/api/simulation/simulate", "POST"),
        "process_mind_moment": ("/api/citta-vithi/process", "POST"),
        "get_scenarios": ("/api/simulation/scenarios", "GET"),
        "health_check": ("/docs", "GET"),  # Using /docs to verify uptime as /health might be json
    }

    if task not in endpoints:
        return f"Error: Unknown task '{task}'. Supported: {list(endpoints.keys())}"

    path, method = endpoints[task]
    url = f"{base_url}{path}"
    
    async with httpx.AsyncClient() as client:
        try:
            if method == "GET":
                resp = await client.get(url, params=payload, timeout=15.0)
            else:
                resp = await client.post(url, json=payload, timeout=15.0)
            
            resp.raise_for_status()
            
            # Try to return JSON, else text
            try:
                return json.dumps(resp.json(), indent=2, ensure_ascii=False)
            except json.JSONDecodeError:
                return resp.text[:2000]  # Truncate if too long
                
        except httpx.HTTPError as e:
            logger.error(f"DMM API Error ({task}): {e}")
            return f"Error calling Digital Mind: {str(e)}"
        except Exception as e:
            logger.error(f"DMM System Error ({task}): {e}")
            return f"Error connecting to Digital Mind: {str(e)}"



# --- WEB SEARCH TOOLS ---

async def search_web(query: str, max_results: int = 5) -> str:
    """
    Search the web using DuckDuckGo (privacy-focused).
    Args:
        query: The search string.
        max_results: Number of results to return.
    """
    try:
        from duckduckgo_search import DDGS
        
        results = DDGS().text(query, max_results=max_results)
        
        if not results:
            return "No results found."
            
        formatted = []
        for i, r in enumerate(results, 1):
            formatted.append(f"{i}. [{r['title']}]({r['href']})\n   {r['body']}")
            
        return "\n".join(formatted)
        
    except Exception as e:
        logger.error(f"Search Web Error: {e}")
        return f"Error executing search: {str(e)}"
        
async def visit_page(url: str) -> str:
    """
    Visit a webpage and extract main text content.
    Args:
        url: The URL to visit.
    """
    try:
        # Use a standard browser user-agent to avoid simple blocking
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        async with httpx.AsyncClient(follow_redirects=True, verify=False) as client:
            response = await client.get(url, headers=headers, timeout=15.0)
            response.raise_for_status()
            
            # Use BeautifulSoup to extract text
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'lxml')
            
            # Remove scripts and styles
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.extract()
                
            text = soup.get_text()
            
            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            return text[:4000] # Return first 4000 chars to avoid prompt overflow
            
    except Exception as e:
        logger.error(f"Visit Page Error: {e}")
        return f"Error visiting page: {str(e)}"

def generate_report(task_description: str, outcome: str, learnings: str) -> str:
    """Format a standard report block."""
    return f"""
--- 🏁 TASK REPORT ---
**Task**: {task_description}
**Outcome**: {outcome}
**Learnings**: {learnings}
-----------------------
"""
