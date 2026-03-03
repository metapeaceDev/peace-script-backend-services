from __future__ import annotations

import subprocess
from pathlib import Path
from typing import List

import httpx
from bs4 import BeautifulSoup

from .config import AppConfig
from .logger import get_logger
from .safety import sanitize_input


logger = get_logger(__name__)


DANGEROUS_COMMAND_HINTS = {
    "rm -rf",
    "del /f",
    "format ",
    "shutdown",
    "reboot",
    "mkfs",
    "diskpart",
    "fdisk",
    "dd if=",
    "> /dev/",
    "chmod 777",
    "chown root",
    "sudo",
    "su ",
    "passwd",
    "crontab",
    "systemctl",
    "service ",
    "killall",
    "pkill",
    "iptables",
    "ufw",
    "firewall",
}


def _safe_path(root: Path, target: str) -> Path:
    """
    Resolve a path safely within the root directory.

    Args:
        root: Root directory
        target: Target path (relative or absolute)

    Returns:
        Resolved path within root

    Raises:
        ValueError: If path is outside root or invalid
    """
    if not target or not target.strip():
        raise ValueError("Empty path provided")

    try:
        if Path(target).is_absolute():
            path = Path(target).resolve()
        else:
            path = (root / target).resolve()

        # Ensure path is within root directory
        try:
            path.relative_to(root)
        except ValueError:
            raise ValueError(f"Path is outside allowed directory: {path}")

        return path
    except Exception as e:
        logger.error(f"Path resolution error: {e}")
        raise ValueError(f"Invalid path: {target}")


def list_dir(cfg: AppConfig, path: str) -> List[str]:
    """
    List contents of a directory.

    Args:
        cfg: Application configuration
        path: Directory path to list

    Returns:
        List of directory contents
    """
    try:
        p = _safe_path(cfg.root_dir, path)
        if not p.exists():
            logger.warning(f"Directory does not exist: {p}")
            return []
        if not p.is_dir():
            logger.warning(f"Path is not a directory: {p}")
            return []

        items = sorted([x.name for x in p.iterdir()])
        logger.debug(f"Listed {len(items)} items in {p}")
        return items
    except Exception as e:
        logger.error(f"Failed to list directory {path}: {e}")
        return []


def read_file(cfg: AppConfig, path: str, max_chars: int = 8000) -> str:
    """
    Read content from a file.

    Args:
        cfg: Application configuration
        path: File path to read
        max_chars: Maximum characters to read

    Returns:
        File content or empty string if error
    """
    try:
        p = _safe_path(cfg.root_dir, path)
        if not p.exists():
            logger.warning(f"File does not exist: {p}")
            return ""
        if not p.is_file():
            logger.warning(f"Path is not a file: {p}")
            return ""

        text = p.read_text(encoding="utf-8", errors="ignore")
        if len(text) > max_chars:
            logger.info(f"File truncated from {len(text)} to {max_chars} characters")
            text = text[:max_chars]

        logger.debug(f"Read {len(text)} characters from {p}")
        return text
    except Exception as e:
        logger.error(f"Failed to read file {path}: {e}")
        return ""


def write_file(cfg: AppConfig, path: str, content: str) -> bool:
    """
    Write content to a file.

    Args:
        cfg: Application configuration
        path: File path to write
        content: Content to write

    Returns:
        True if successful, False otherwise
    """
    try:
        content = sanitize_input(content, max_length=100000)  # Limit content size
        p = _safe_path(cfg.root_dir, path)

        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")

        logger.info(f"Written {len(content)} characters to {p}")
        return True
    except Exception as e:
        logger.error(f"Failed to write file {path}: {e}")
        return False


def run_shell_command(cfg: AppConfig, command: str) -> str:
    """
    Execute a shell command safely.

    Args:
        cfg: Application configuration
        command: Command to execute

    Returns:
        Command output or error message
    """
    if not cfg.allow_shell_commands:
        logger.warning("Shell commands are disabled")
        return "Shell commands are disabled. Set JITTA_ALLOW_SHELL_COMMANDS=true."

    if not command or not command.strip():
        return "Empty command provided"

    command = sanitize_input(command, max_length=1000)
    cmd_lower = command.lower()

    # Check for dangerous commands
    for hint in DANGEROUS_COMMAND_HINTS:
        if hint in cmd_lower:
            logger.warning(f"Blocked dangerous command: {hint}")
            return f"Blocked: command contains '{hint}' which is potentially dangerous."

    try:
        logger.info(f"Executing command: {command}")
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            cwd=str(cfg.root_dir),
            timeout=30,  # 30 second timeout
        )

        output = (result.stdout or "") + (result.stderr or "")
        output = output.strip()[:8000]  # Limit output size

        if result.returncode != 0:
            logger.warning(f"Command failed with exit code {result.returncode}")
            return f"Command failed (exit code {result.returncode}):\n{output}"
        else:
            logger.debug(f"Command executed successfully")
            return output or "(no output)"
    except subprocess.TimeoutExpired:
        logger.error("Command timed out")
        return "Command timed out after 30 seconds"
    except Exception as e:
        logger.error(f"Command execution error: {e}")
        return f"Command error: {e}"


def fetch_url(cfg: AppConfig, url: str, max_chars: int = 8000) -> str:
    """
    Fetch content from a URL.

    Args:
        cfg: Application configuration
        url: URL to fetch
        max_chars: Maximum characters to return

    Returns:
        Fetched content or error message
    """
    if not cfg.allow_web_access:
        logger.warning("Web access is disabled")
        return "Web access is disabled."

    if not url or not url.strip():
        return "Empty URL provided"

    url = sanitize_input(url, max_length=2000)

    # Basic URL validation
    if not url.startswith(("http://", "https://")):
        return "Invalid URL: must start with http:// or https://"

    try:
        logger.info(f"Fetching URL: {url}")
        resp = httpx.get(url, timeout=30, follow_redirects=True)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "lxml")
        text = " ".join(soup.get_text().split())

        if len(text) > max_chars:
            logger.info(f"Content truncated from {len(text)} to {max_chars} characters")
            text = text[:max_chars]

        logger.debug(f"Fetched {len(text)} characters from {url}")
        return text
    except httpx.TimeoutException:
        logger.error("URL fetch timed out")
        return "Request timed out"
    except httpx.HTTPError as e:
        logger.error(f"HTTP error fetching {url}: {e}")
        return f"HTTP error: {e}"
    except Exception as e:
        logger.error(f"Error fetching {url}: {e}")
        return f"Fetch error: {e}"


def ask_digital_mind(cfg: AppConfig, mode: str, payload: dict = None) -> str:
    """
    Interact with the Digital Mind Model (DMM) Backend.

    Args:
        cfg: Application configuration
        mode: Operation mode ('get_scenarios' or 'simulate')
        payload: JSON payload for the request (required for 'simulate')

    Returns:
        JSON string response from DMM or error message
    """
    base_url = "http://localhost:8000/api/simulation"
    
    if mode == "get_scenarios":
        try:
            logger.info("Fetching scenarios from DMM...")
            resp = httpx.get(f"{base_url}/scenarios", timeout=10)
            resp.raise_for_status()
            return resp.text
        except Exception as e:
            logger.error(f"DMM Scenarios Error: {e}")
            return f"Error fetching scenarios: {e}"

    elif mode == "simulate":
        if not payload:
            return "Error: Payload required for simulate mode"
        
        try:
            logger.info(f"Sending simulation request: {payload}")
            resp = httpx.post(f"{base_url}/simulate", json=payload, timeout=30)
            resp.raise_for_status()
            return resp.text
        except Exception as e:
            logger.error(f"DMM Simulation Error: {e}")
            return f"Error running simulation: {e}"

    else:
        return f"Unknown mode: {mode}. Use 'get_scenarios' or 'simulate'."
