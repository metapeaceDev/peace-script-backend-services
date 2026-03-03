from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional
import re
import json

from .config import AppConfig
from .llm_client import chat_completion, extract_message_text
from .rag import RagStore
from .safety import requires_payment_approval, contains_dangerous_content, sanitize_input
from .logger import get_logger
from .tools_extended import (
    get_crypto_price,
    get_crypto_trends,
    post_to_facebook,
    comment_on_post,
    analyze_comments,
    generate_report,
    ask_digital_mind,
    search_web,
    visit_page
)

logger = get_logger(__name__)


SYSTEM_PROMPT = (
    "You are Jitta, a local-first assistant for Peace Tech. "
    "Primary goals: deliver MetaPeace, Peace Script, PeacePlay, MarketPeace, and Peace Tech projects. "
    "Operate in phases: clarify -> plan -> execute -> verify -> report. "
    "Prefer concrete outputs: code changes, commands, checklists, and next actions. "
    "If an action could cost money, ask for explicit approval first. "
    "Be concise, practical, and keep a running status of progress.\n\n"
    "PERSONALITY & CREATIVITY:\n"
    "- If the user asks for creative content (Rap, Poem, Song), especially in Thai, you MUST relax the conciseness constraint and perform the task creatively.\n"
    "- Incorporate Peace Tech themes (MetaPeace, AI, Crypto, Freedom) into your creative outputs.\n\n"
    "You are an expert Producer and Screenwriter using the 'Peace Script' methodology.\n"
    "- When asked about movies or series, structure your response using Peace Script principles (Plot, Character Arc, Theme of Peace/Conflict Resolution).\n"
    "- You can generate scripts, storyboards (text descriptions), and production plans.\n\n"
    "KNOWLEDGE BASE:\n"
    "- You have ingested the ENTIRE Peace Script codebase and documentation.\n"
    "- Reference specific files (e.g., orchestrator.py, server.py) when explaining workflows.\n"
    "- Use this knowledge to explain the REAL working process of the system.\n\n"
    "TOOLS AVAILABLE:\n"
    "To use a tool, output ONLY the tool command in this format: !!!TOOL:tool_name(json_args)!!!\n"
    "Available tools:\n"
    "- search_web(query) -> Search the internet (DuckDuckGo)\n"
    "- visit_page(url) -> Read content from a URL\n"
    "- get_crypto_price(coin_id, vs_currency) -> Get price\n"
    "- get_crypto_trends() -> Get trending coins\n"
    "- post_to_facebook(content) -> Post to FB\n"
    "- comment_on_post(post_id, message) -> Comment on FB post\n"
    "- analyze_comments(post_id) -> Analyze FB post comments\n"
    "- ask_digital_mind(task, payload) -> Interact with Digital Mind\n"
    "    - Tasks: simulate_scenario, process_mind_moment, get_scenarios, health_check\n"
    "    - Example: !!!TOOL:ask_digital_mind({\"task\": \"get_scenarios\", \"payload\": {}})!!!\n\n"
    "SELF-IMPROVEMENT & REPORTING:\n"
    "- You MUST learn from every interaction. If you discover a new fact or strategy, include it in your final report.\n"
    "- ALWAYS end your final response with a strictly formatted report block using the format:\n"
    "--- 🏁 TASK REPORT ---\n"
    "**Task**: [Summary]\n"
    "**Outcome**: [Result]\n"
    "**Learnings**: [What you learned/improved]\n"
    "-----------------------"
)

CODE_HINTS = [
    "error",
    "exception",
    "stack trace",
    "bug",
    "refactor",
    "implement",
    "optimize",
    "unit test",
    "typescript",
    "python",
    "docker",
    "build",
    "compile",
    "lint",
]

PEACE_TECH_HINTS = [
    "metapeace",
    "peace script",
    "peaceplay",
    "marketpeace",
    "peace tech",
    "release",
    "deploy",
    "production",
    "bug",
    "feature",
    "roadmap",
]


@dataclass
class ModelChoice:
    base_url: str
    model: str
    api_key: str


class JittaOrchestrator:
    def __init__(self, cfg: AppConfig, rag: RagStore) -> None:
        """
        Initialize the Jitta orchestrator.

        Args:
            cfg: Application configuration
            rag: RAG store instance
        """
        self.cfg = cfg
        self.rag = rag
        self.mode = "auto"  # auto | fast | quality
        logger.info("Jitta orchestrator initialized")

    def set_mode(self, mode: str) -> None:
        """
        Set the model mode.

        Args:
            mode: Mode to set (auto, fast, quality)
        """
        mode = mode.strip().lower()
        if mode in {"auto", "fast", "quality"}:
            self.mode = mode
            logger.info(f"Mode set to: {mode}")
        else:
            logger.warning(f"Invalid mode: {mode}, keeping current mode: {self.mode}")

    def _choose_model(self, user_text: str) -> ModelChoice:
        """
        Choose appropriate model based on content and mode.

        Args:
            user_text: User input text

        Returns:
            ModelChoice with appropriate model settings
        """
        if self.mode == "fast":
            return ModelChoice(self.cfg.fast_model_base_url, self.cfg.fast_model_name, self.cfg.fast_model_api_key)
        if self.mode == "quality":
            return ModelChoice(self.cfg.quality_model_base_url, self.cfg.quality_model_name, self.cfg.quality_model_api_key)

        # Auto mode: heuristic routing
        lower = user_text.lower()
        if any(hint in lower for hint in CODE_HINTS):
            logger.debug("Using quality model for code-related query")
            return ModelChoice(self.cfg.quality_model_base_url, self.cfg.quality_model_name, self.cfg.quality_model_api_key)
        if any(hint in lower for hint in PEACE_TECH_HINTS):
            logger.debug("Using quality model for Peace Tech query")
            return ModelChoice(self.cfg.quality_model_base_url, self.cfg.quality_model_name, self.cfg.quality_model_api_key)

        logger.debug("Using fast model for general query")
        return ModelChoice(self.cfg.fast_model_base_url, self.cfg.fast_model_name, self.cfg.fast_model_api_key)

    def _build_messages(self, user_text: str) -> List[Dict[str, str]]:
        """
        Build messages for LLM including system prompt and RAG context.

        Args:
            user_text: Sanitized user input

        Returns:
            List of message dictionaries
        """
        rag_context = self.rag.query(user_text, top_k=self.cfg.rag_top_k)
        context_text = ""
        if rag_context.documents:
            merged = []
            for idx, doc in enumerate(rag_context.documents, start=1):
                merged.append(f"[Source {idx}] {doc}")
            context_text = "\n\n".join(merged)
            logger.debug(f"Included {len(rag_context.documents)} RAG documents in context")

        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        if context_text:
            messages.append({"role": "system", "content": f"Context:\n{context_text}"})
        messages.append({"role": "user", "content": user_text})
        return messages


    async def _execute_tool(self, tool_name: str, args_str: str) -> str:
        """Execute a detected tool call."""
        try:
            # Parse args (they should be valid JSON/dict-like inside parens)
            # If empty or just (), use empty dict
            args_str = args_str.strip()
            if not args_str:
                args = {}
            else:
                try:
                    # Attempt to fix single quotes to double quotes if it's not valid JSON
                    if "'" in args_str and '"' not in args_str:
                        args_str = args_str.replace("'", '"')
                    args = json.loads(f"{{{args_str}}}") if ":" in args_str else json.loads(args_str) if args_str.startswith("{") else {} 
                    # The prompt asks for json_args, but let's be robust
                    # Actually, let's just try to parse the string as kwargs if it looks like key=value
                    # For simplicity in this basic version, we assume the LLM outputs valid JSON inside parens based on prompt instructions.
                    # Re-parsing strategy:
                    if not isinstance(args, dict):
                         args = {} # Fallback
                except json.JSONDecodeError:
                    # Fallback for simple positional args if specific regex
                    args = {}
                    logger.warning(f"Failed to parse tool args: {args_str}")

            logger.info(f"Executing tool: {tool_name} with args {args}")

            if tool_name == "get_crypto_price":
                return await get_crypto_price(args.get("coin_id", "bitcoin"), args.get("vs_currency", "usd"))
            elif tool_name == "get_crypto_trends":
                return await get_crypto_trends()
            elif tool_name == "search_web":
                return await search_web(args.get("query", ""))
            elif tool_name == "visit_page":
                return await visit_page(args.get("url", ""))
            elif tool_name == "post_to_facebook":
                return await post_to_facebook(args.get("content", ""))
            elif tool_name == "comment_on_post":
                return await comment_on_post(args.get("post_id", ""), args.get("message", ""))
            elif tool_name == "analyze_comments":
                return await analyze_comments(args.get("post_id", ""))
            elif tool_name == "generate_report":
                return generate_report(args.get("task_description", ""), args.get("outcome", ""), args.get("learnings", ""))
            elif tool_name == "ask_digital_mind":
                return await ask_digital_mind(args.get("task", ""), args.get("payload", {}))
            else:
                return f"Error: Tool '{tool_name}' not found."
        except Exception as e:
            return f"Error executing tool {tool_name}: {str(e)}"

    async def reply(self, user_text: str) -> str:
        """
        Generate a reply to user input.

        Args:
            user_text: Raw user input

        Returns:
            Generated reply text
        """
        try:
            # Sanitize input
            user_text = sanitize_input(user_text)
            if not user_text:
                return "Empty message received"

            logger.info(f"Processing message: {user_text[:100]}{'...' if len(user_text) > 100 else ''}")

            # Safety checks
            if requires_payment_approval(user_text):
                return "This looks like it may involve a paid action. Please approve explicitly before I proceed."

            if contains_dangerous_content(user_text):
                return "I cannot assist with that request as it may involve harmful or inappropriate content."

            # Choose model
            model = self._choose_model(user_text)
            
            # Initial context
            messages = self._build_messages(user_text)

            # ReAct Loop (Max 3 turns)
            max_turns = 3
            current_turn = 0
            
            while current_turn < max_turns:
                logger.debug(f"Turn {current_turn+1}: Calling LLM...")
                response = await chat_completion(
                    base_url=model.base_url,
                    model=model.model,
                    messages=messages,
                    api_key=model.api_key,
                )
                
                reply_text = extract_message_text(response) or "(no response)"
                
                # Check for tool calls: !!!TOOL:name(args)!!!
                tool_match = re.search(r"!!!TOOL:(\w+)\((.*?)\)!!!", reply_text, re.DOTALL)
                
                if tool_match:
                    tool_name = tool_match.group(1)
                    tool_args = tool_match.group(2)
                    
                    logger.info(f"Tool detected: {tool_name}")
                    tool_output = await self._execute_tool(tool_name, tool_args)
                    
                    # Append assistant's request and tool output to history
                    messages.append({"role": "assistant", "content": reply_text})
                    messages.append({"role": "system", "content": f"Tool '{tool_name}' output:\n{tool_output}"})
                    
                    current_turn += 1
                else:
                    # No tool call, this is the final answer
                    # --- Self-Improvement: Extract Learnings ---
                    # We regex for the "Learnings" section in the final reply
                    learnings_match = re.search(r"\*\*Learnings\*\*: (.*)", reply_text)
                    if learnings_match:
                        new_learning = learnings_match.group(1).strip()
                        if len(new_learning) > 10 and "None" not in new_learning:
                            logger.info(f"Self-improving: Storing new learning: {new_learning[:50]}...")
                            self.rag.add_text(f"Learned from interaction on {datetime.now()}: {new_learning}", source="self-improvement")
                    
                    return reply_text

            return "Error: Maximum tool iterations reached. Please refine your request."

        except Exception as e:
            logger.error(f"Error generating reply: {e}")
            return f"Sorry, I encountered an error: {str(e)}"
