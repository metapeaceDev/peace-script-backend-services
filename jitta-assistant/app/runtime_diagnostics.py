from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional, Tuple

import httpx


@dataclass
class RuntimeDeviceInfo:
    requested: str
    resolved: str
    cuda_available: bool
    mps_available: bool
    reason: str


def resolve_embedding_device(requested: str) -> RuntimeDeviceInfo:
    requested_norm = (requested or "auto").strip().lower()
    if requested_norm not in {"auto", "cpu", "cuda", "mps"}:
        requested_norm = "auto"

    try:
        import torch  # type: ignore

        cuda_available = bool(torch.cuda.is_available())
        mps_available = bool(
            getattr(torch.backends, "mps", None) and torch.backends.mps.is_available()
        )
    except Exception:
        cuda_available = False
        mps_available = False

    if requested_norm == "cpu":
        return RuntimeDeviceInfo(
            requested=requested_norm,
            resolved="cpu",
            cuda_available=cuda_available,
            mps_available=mps_available,
            reason="Forced CPU by configuration",
        )

    if requested_norm == "cuda":
        if cuda_available:
            return RuntimeDeviceInfo(
                requested=requested_norm,
                resolved="cuda",
                cuda_available=cuda_available,
                mps_available=mps_available,
                reason="Forced CUDA and CUDA is available",
            )
        return RuntimeDeviceInfo(
            requested=requested_norm,
            resolved="cpu",
            cuda_available=cuda_available,
            mps_available=mps_available,
            reason="CUDA requested but not available, fallback to CPU",
        )

    if requested_norm == "mps":
        if mps_available:
            return RuntimeDeviceInfo(
                requested=requested_norm,
                resolved="mps",
                cuda_available=cuda_available,
                mps_available=mps_available,
                reason="Forced MPS and MPS is available",
            )
        return RuntimeDeviceInfo(
            requested=requested_norm,
            resolved="cpu",
            cuda_available=cuda_available,
            mps_available=mps_available,
            reason="MPS requested but not available, fallback to CPU",
        )

    if cuda_available:
        return RuntimeDeviceInfo(
            requested=requested_norm,
            resolved="cuda",
            cuda_available=cuda_available,
            mps_available=mps_available,
            reason="Auto mode selected CUDA",
        )

    if mps_available:
        return RuntimeDeviceInfo(
            requested=requested_norm,
            resolved="mps",
            cuda_available=cuda_available,
            mps_available=mps_available,
            reason="Auto mode selected MPS",
        )

    return RuntimeDeviceInfo(
        requested=requested_norm,
        resolved="cpu",
        cuda_available=cuda_available,
        mps_available=mps_available,
        reason="Auto mode fallback to CPU",
    )


def check_openai_compatible_endpoint(base_url: str, timeout_sec: float = 3.0) -> Dict[str, object]:
    base = (base_url or "").strip()
    if not base:
        return {"ok": False, "error": "empty base URL", "baseUrl": base}

    endpoint = f"{base.rstrip('/')}/models"
    try:
        with httpx.Client(timeout=timeout_sec) as client:
            response = client.get(endpoint)
            response.raise_for_status()
            payload = response.json()
            model_count = len(payload.get("data", [])) if isinstance(payload, dict) else None
            return {
                "ok": True,
                "baseUrl": base,
                "endpoint": endpoint,
                "statusCode": response.status_code,
                "modelCount": model_count,
            }
    except Exception as exc:
        return {
            "ok": False,
            "baseUrl": base,
            "endpoint": endpoint,
            "error": str(exc),
        }


def get_torch_cuda_snapshot() -> Dict[str, object]:
    try:
        import torch  # type: ignore

        cuda_available = bool(torch.cuda.is_available())
        device_count = int(torch.cuda.device_count()) if cuda_available else 0
        devices = []
        for index in range(device_count):
            name = torch.cuda.get_device_name(index)
            devices.append({"index": index, "name": name})

        return {
            "available": cuda_available,
            "deviceCount": device_count,
            "devices": devices,
            "torchVersion": getattr(torch, "__version__", None),
        }
    except Exception as exc:
        return {
            "available": False,
            "deviceCount": 0,
            "devices": [],
            "error": str(exc),
        }
