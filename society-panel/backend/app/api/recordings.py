"""
API router for managing simulation recording files.
"""

import json
import os
from fastapi import APIRouter, HTTPException

router = APIRouter()

RECORDINGS_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "recordings"))


def _validate_filename(filename: str):
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename.")
    if not filename.endswith(".json"):
        raise HTTPException(status_code=400, detail="Only .json files are supported.")


@router.get("/list")
async def list_recordings():
    """List all recording files with metadata summaries."""
    os.makedirs(RECORDINGS_PATH, exist_ok=True)
    recordings = []
    for fname in sorted(os.listdir(RECORDINGS_PATH), reverse=True):
        if not fname.endswith(".json"):
            continue
        filepath = os.path.join(RECORDINGS_PATH, fname)
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            meta = data.get("metadata", {})
            recordings.append({
                "filename": fname,
                "created_at": meta.get("created_at"),
                "max_ticks": meta.get("max_ticks"),
                "total_ticks_recorded": meta.get("total_ticks_recorded", len(data.get("frames", []))),
                "agent_count": meta.get("agent_count", 0),
                "map_size": meta.get("map_size", 300),
            })
        except Exception:
            recordings.append({"filename": fname, "error": "Failed to read metadata"})
    return recordings


@router.get("/{filename}")
async def get_recording(filename: str):
    """Get full recording data for replay."""
    _validate_filename(filename)
    filepath = os.path.join(RECORDINGS_PATH, filename)
    if not os.path.isfile(filepath):
        raise HTTPException(status_code=404, detail="Recording not found.")
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read recording: {e}")


@router.delete("/{filename}")
async def delete_recording(filename: str):
    """Delete a recording file."""
    _validate_filename(filename)
    filepath = os.path.join(RECORDINGS_PATH, filename)
    if not os.path.isfile(filepath):
        raise HTTPException(status_code=404, detail="Recording not found.")
    try:
        os.remove(filepath)
        return {"status": "deleted", "filename": filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete recording: {e}")
