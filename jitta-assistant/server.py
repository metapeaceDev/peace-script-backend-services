import asyncio
from fastapi import FastAPI
from pydantic import BaseModel

from app.config import AppConfig
from app.rag import RagStore
from app.orchestrator import JittaOrchestrator
from app.logger import setup_logging
from app.runtime_diagnostics import (
    check_openai_compatible_endpoint,
    get_torch_cuda_snapshot,
    resolve_embedding_device,
)


class ChatRequest(BaseModel):
    text: str


class IngestRequest(BaseModel):
    text: str
    source: str = "api"


def create_app(cfg: AppConfig = None, rag: RagStore = None, orchestrator: JittaOrchestrator = None):
    """Create FastAPI app with dependencies."""
    if cfg is None:
        cfg = AppConfig()
        setup_logging()

    if rag is None:
        rag = RagStore(cfg.chroma_dir, cfg.rag_embed_model, cfg.rag_embed_device)

    if orchestrator is None:
        orchestrator = JittaOrchestrator(cfg, rag)

    app = FastAPI(title="Jitta Assistant")

    @app.post("/chat")
    async def chat(req: ChatRequest):
        try:
            reply = await orchestrator.reply(req.text)
            return {"reply": reply, "mode": orchestrator.mode}
        except Exception as e:
            return {"reply": f"Error: {str(e)}", "mode": orchestrator.mode}

    @app.post("/ingest")
    async def ingest(req: IngestRequest):
        try:
            rag.add_text(req.text, req.source)
            return {"status": "ok"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    @app.get("/status/runtime")
    async def runtime_status():
        embed_device = resolve_embedding_device(cfg.rag_embed_device)
        fast_health = check_openai_compatible_endpoint(cfg.fast_model_base_url, timeout_sec=3.0)
        quality_health = check_openai_compatible_endpoint(
            cfg.quality_model_base_url, timeout_sec=3.0
        )
        torch_snapshot = get_torch_cuda_snapshot()

        return {
            "appName": cfg.app_name,
            "mode": orchestrator.mode,
            "mockLlm": cfg.mock_llm,
            "embedding": {
                "model": cfg.rag_embed_model,
                "requestedDevice": cfg.rag_embed_device,
                "resolvedDevice": embed_device.resolved,
                "reason": embed_device.reason,
                "runtimeDevice": getattr(rag, "embedding_device", "unknown"),
            },
            "llm": {
                "fast": {
                    "model": cfg.fast_model_name,
                    "baseUrl": cfg.fast_model_base_url,
                    "health": fast_health,
                },
                "quality": {
                    "model": cfg.quality_model_name,
                    "baseUrl": cfg.quality_model_base_url,
                    "health": quality_health,
                },
            },
            "torch": torch_snapshot,
        }

    return app


# Global instances for production use
cfg = AppConfig()
setup_logging()
rag = RagStore(cfg.chroma_dir, cfg.rag_embed_model, cfg.rag_embed_device)
orchestrator = JittaOrchestrator(cfg, rag)
app = create_app(cfg, rag, orchestrator)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=7071)
