from pathlib import Path

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from dotenv import load_dotenv

from app.config import AppConfig
from app.logger import setup_logging
from app.orchestrator import JittaOrchestrator
from app.rag import RagStore
from app.runtime_diagnostics import (
    check_openai_compatible_endpoint,
    get_torch_cuda_snapshot,
    resolve_embedding_device,
)
from app.tools import list_dir, read_file, write_file, run_shell_command


load_dotenv()
setup_logging()

cfg = AppConfig()
rag = RagStore(cfg.chroma_dir, cfg.rag_embed_model, cfg.rag_embed_device)
orchestrator = JittaOrchestrator(cfg, rag)


def _is_admin(update: Update) -> bool:
    if not cfg.admin_chat_id:
        return True
    try:
        return str(update.effective_chat.id) == str(cfg.admin_chat_id)
    except Exception:
        return False


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Jitta is online. Use /help for commands.")


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = (
        "/mode fast|quality|auto\n"
        "/status\n"
        "/ingest <text>\n"
        "/ingest_dir <absolute path>\n"
        "/read <path>\n"
        "/write <path>\\n<content>\n"
        "/list <path>\n"
        "/run <command>\n"
    )
    await update.message.reply_text(text)


async def cmd_mode(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _is_admin(update):
        return
    if not context.args:
        await update.message.reply_text(f"Current mode: {orchestrator.mode}")
        return
    orchestrator.set_mode(context.args[0])
    await update.message.reply_text(f"Mode set to: {orchestrator.mode}")


async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    embed_device = resolve_embedding_device(cfg.rag_embed_device)
    torch_snapshot = get_torch_cuda_snapshot()
    fast_health = check_openai_compatible_endpoint(cfg.fast_model_base_url, timeout_sec=2.0)
    quality_health = check_openai_compatible_endpoint(cfg.quality_model_base_url, timeout_sec=2.0)

    fast_ok = "OK" if fast_health.get("ok") else "DOWN"
    quality_ok = "OK" if quality_health.get("ok") else "DOWN"
    torch_ok = "YES" if torch_snapshot.get("available") else "NO"

    text = (
        f"Mode: {orchestrator.mode}\n"
        f"Mock LLM: {cfg.mock_llm}\n"
        f"Fast model: {cfg.fast_model_name}\n"
        f"Fast endpoint: {fast_ok}\n"
        f"Quality model: {cfg.quality_model_name}\n"
        f"Quality endpoint: {quality_ok}\n"
        f"Embed model: {cfg.rag_embed_model}\n"
        f"Embed device: requested={cfg.rag_embed_device}, resolved={embed_device.resolved}\n"
        f"Torch CUDA: {torch_ok}\n"
        f"RAG top_k: {cfg.rag_top_k}\n"
    )
    await update.message.reply_text(text)


async def cmd_ingest(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _is_admin(update):
        return
    content = update.message.text.split(" ", 1)
    if len(content) < 2:
        await update.message.reply_text("Usage: /ingest <text>")
        return
    rag.add_text(content[1], source="telegram")
    await update.message.reply_text("Ingested.")


async def cmd_ingest_dir(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _is_admin(update):
        return
    if not context.args:
        await update.message.reply_text("Usage: /ingest_dir <absolute path>")
        return
    path = " ".join(context.args)
    count = rag.ingest_dir(Path(path))
    await update.message.reply_text(f"Ingested files: {count}")


async def cmd_read(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _is_admin(update):
        return
    if not context.args:
        await update.message.reply_text("Usage: /read <path>")
        return
    path = " ".join(context.args)
    content = read_file(cfg, path)
    await update.message.reply_text(content or "(empty)")


async def cmd_write(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _is_admin(update):
        return
    raw = update.message.text.split(" ", 1)
    if len(raw) < 2 or "\n" not in raw[1]:
        await update.message.reply_text("Usage: /write <path>\\n<content>")
        return
    path, content = raw[1].split("\n", 1)
    write_file(cfg, path.strip(), content)
    await update.message.reply_text("Written.")


async def cmd_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _is_admin(update):
        return
    if not context.args:
        await update.message.reply_text("Usage: /list <path>")
        return
    path = " ".join(context.args)
    items = list_dir(cfg, path)
    await update.message.reply_text("\n".join(items) if items else "(empty)")


async def cmd_run(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _is_admin(update):
        return
    if not context.args:
        await update.message.reply_text("Usage: /run <command>")
        return
    command = " ".join(context.args)
    output = run_shell_command(cfg, command)
    await update.message.reply_text(output or "(no output)")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.message.text:
        return
    if not _is_admin(update):
        return
    reply = await orchestrator.reply(update.message.text)
    await update.message.reply_text(reply)


def main() -> None:
    if not cfg.telegram_bot_token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not set.")
    application = ApplicationBuilder().token(cfg.telegram_bot_token).build()

    application.add_handler(CommandHandler("start", cmd_start))
    application.add_handler(CommandHandler("help", cmd_help))
    application.add_handler(CommandHandler("mode", cmd_mode))
    application.add_handler(CommandHandler("status", cmd_status))
    application.add_handler(CommandHandler("ingest", cmd_ingest))
    application.add_handler(CommandHandler("ingest_dir", cmd_ingest_dir))
    application.add_handler(CommandHandler("read", cmd_read))
    application.add_handler(CommandHandler("write", cmd_write))
    application.add_handler(CommandHandler("list", cmd_list))
    application.add_handler(CommandHandler("run", cmd_run))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.run_polling()


if __name__ == "__main__":
    main()
