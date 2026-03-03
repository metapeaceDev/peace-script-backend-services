# Jitta Assistant Update: Internet Connectivity

## New Capabilities
Based on recent system upgrades, Jitta Assistant now has the ability to connect to the external internet. This was achieved by integrating:
- **DuckDuckGo Search**: Allows Jitta to query the web for real-time information.
- **Web Visiting**: Allows Jitta to visit specific URLs and read their content (text-only).

## How to Use
You can ask Jitta natural language queries like:
- "Search for the latest Peace Tech news."
- "What is the current price of Bitcoin?"
- "Read this article: https://example.com/article"

## Technical Details
- **Library**: `duckduckgo-search` (privacy-first, no API key needed).
- **Safety**: Standard user-agent headers are used. Content is sanitized before processing.
- **Integration**: Added to `jitta-assistant/app/tools_extended.py` and registered in `jitta-assistant/app/orchestrator.py`.

## Status
- **Service**: Running on port `8003`.
- **Tests**: `test_internet_tools.py` verified search functionality.
