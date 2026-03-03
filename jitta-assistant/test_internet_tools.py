import asyncio
import sys
import os

# Add local directory to path to find app module
sys.path.append(os.getcwd())

try:
    from app.tools_extended import search_web, visit_page
except ImportError as e:
    print(f"Import Error: {e}")
    sys.exit(1)

async def test_search():
    print("Testing search_web...")
    # Using a simple query unlikely to be blocked or controversial
    result = await search_web("Peace Script AI")
    print("\n--- Search Result ---")
    print(result[:500] + "..." if len(result) > 500 else result)
    
    if "Error" not in result and "No results" not in result:
        print("✅ Search Success")
    else:
        print("⚠️ Search Returned Empty or Error")

async def test_visit():
    print("\nTesting visit_page...")
    # Visit a safe, reliable text page
    result = await visit_page("http://example.com")
    print("\n--- Visit Result ---")
    print(result[:500] + "..." if len(result) > 500 else result)
    
    if "Example Domain" in result:
        print("✅ Visit Success")
    else:
        print("⚠️ Visit Failed")

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(test_search())
    loop.run_until_complete(test_visit())
