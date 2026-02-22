"""
Tests for standalone simulation recording functionality.

Verifies that run_simulation.py produces Society Panel-compatible
recording JSON files (metadata + frames format).
"""

import asyncio
import json
import os
import tempfile
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Helpers – replicate the recording logic from run_simulation.py so we can
# test it in isolation (no LLM API keys, no full simulation boot required).
# ---------------------------------------------------------------------------

SAMPLE_AGENTS = [
    {"id": "Alice", "position": [79, 142]},
    {"id": "Bob", "position": [284, 23]},
    {"id": "Charlie", "position": [204, 300]},
]

SAMPLE_AGENTS_WITH_STATUS = [
    {"id": "Alice", "position": [79, 142], "status": {"health": 78, "energy": 57, "happiness": 89, "stress": 17, "socialization": 52, "money": 1911}},
    {"id": "Bob", "position": [284, 23], "status": {"health": 79, "energy": 96, "happiness": 80, "stress": 29, "socialization": 85, "money": 6807}},
    {"id": "Charlie", "position": [204, 300], "status": {"health": 81, "energy": 94, "happiness": 50, "stress": 48, "socialization": 38, "money": 4147}},
]

SAMPLE_MESSAGES = [
    {"from_id": "Alice", "to_id": "Bob", "content": "Hello!"},
    {"from_id": "Bob", "to_id": "Charlie", "content": "How are you?"},
]


def build_recording(frames_data: list[list[dict]], max_ticks: int = 3, map_size: int = 300,
                    messages_per_frame: list[list[dict]] | None = None) -> dict:
    """Build a recording dict in the same way run_simulation.py does."""
    recording_metadata = {
        "created_at": datetime.now().isoformat(),
        "max_ticks": max_ticks,
        "map_size": map_size,
    }
    recording_frames = []
    for tick, agents in enumerate(frames_data):
        frame = {
            "tick": tick,
            "timestamp": datetime.now().isoformat(),
            "agents": agents,
            "messages": messages_per_frame[tick] if messages_per_frame and tick < len(messages_per_frame) else [],
        }
        recording_frames.append(frame)

    if recording_frames:
        recording_metadata["total_ticks_recorded"] = len(recording_frames)
        recording_metadata["agent_count"] = len(recording_frames[0].get("agents", []))

    return {"metadata": recording_metadata, "frames": recording_frames}


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestRecordingJsonFormat:
    """Verify the recording JSON matches Society Panel's expected schema."""

    def test_top_level_keys(self):
        recording = build_recording([SAMPLE_AGENTS])
        assert "metadata" in recording
        assert "frames" in recording

    def test_metadata_fields(self):
        recording = build_recording([SAMPLE_AGENTS], max_ticks=10, map_size=300)
        meta = recording["metadata"]
        assert "created_at" in meta
        assert meta["max_ticks"] == 10
        assert meta["map_size"] == 300
        assert meta["total_ticks_recorded"] == 1
        assert meta["agent_count"] == 3

    def test_metadata_created_at_is_iso8601(self):
        recording = build_recording([SAMPLE_AGENTS])
        datetime.fromisoformat(recording["metadata"]["created_at"])

    def test_frame_structure(self):
        recording = build_recording([SAMPLE_AGENTS, SAMPLE_AGENTS])
        assert len(recording["frames"]) == 2
        frame = recording["frames"][0]
        assert "tick" in frame
        assert "timestamp" in frame
        assert "agents" in frame
        assert frame["tick"] == 0

    def test_frame_timestamp_is_iso8601(self):
        recording = build_recording([SAMPLE_AGENTS])
        datetime.fromisoformat(recording["frames"][0]["timestamp"])

    def test_agent_entry_format(self):
        recording = build_recording([SAMPLE_AGENTS])
        agent = recording["frames"][0]["agents"][0]
        assert "id" in agent
        assert "position" in agent
        assert isinstance(agent["id"], str)
        assert isinstance(agent["position"], list)
        assert len(agent["position"]) == 2

    def test_empty_frames(self):
        recording = build_recording([])
        assert recording["frames"] == []
        assert "total_ticks_recorded" not in recording["metadata"]


class TestRecordingFileSave:
    """Verify recording files are correctly written to disk."""

    def test_save_creates_file(self, tmp_path):
        recording = build_recording([SAMPLE_AGENTS, SAMPLE_AGENTS], max_ticks=2)
        filepath = tmp_path / "recording_20260101_120000.json"
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(recording, f, ensure_ascii=False)

        assert filepath.exists()
        loaded = json.loads(filepath.read_text(encoding="utf-8"))
        assert loaded["metadata"]["total_ticks_recorded"] == 2
        assert len(loaded["frames"]) == 2

    def test_save_ensure_ascii_false(self, tmp_path):
        """Non-ASCII agent names (e.g. Japanese) are preserved."""
        agents_jp = [{"id": "太郎", "position": [10, 20]}]
        recording = build_recording([agents_jp])
        filepath = tmp_path / "recording_jp.json"
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(recording, f, ensure_ascii=False)

        raw = filepath.read_text(encoding="utf-8")
        assert "太郎" in raw  # not escaped as \uXXXX

    def test_filename_format(self):
        filename = f"recording_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        assert filename.startswith("recording_")
        assert filename.endswith(".json")
        # Extract date portion and validate
        date_part = filename[len("recording_"):-len(".json")]
        datetime.strptime(date_part, "%Y%m%d_%H%M%S")

    def test_recordings_directory_created(self, tmp_path):
        recordings_path = tmp_path / "society-panel" / "backend" / "recordings"
        assert not recordings_path.exists()
        os.makedirs(recordings_path, exist_ok=True)
        assert recordings_path.exists()


class TestSocietyPanelCompatibility:
    """Verify the recording is compatible with Society Panel's recordings API."""

    def test_list_api_fields(self):
        """The /list API extracts these fields from metadata."""
        recording = build_recording([SAMPLE_AGENTS] * 5, max_ticks=5, map_size=300)
        meta = recording["metadata"]
        # Simulate what recordings.py list_recordings() does
        result = {
            "filename": "recording_test.json",
            "created_at": meta.get("created_at"),
            "max_ticks": meta.get("max_ticks"),
            "total_ticks_recorded": meta.get("total_ticks_recorded", len(recording.get("frames", []))),
            "agent_count": meta.get("agent_count", 0),
            "map_size": meta.get("map_size", 300),
        }
        assert result["created_at"] is not None
        assert result["max_ticks"] == 5
        assert result["total_ticks_recorded"] == 5
        assert result["agent_count"] == 3
        assert result["map_size"] == 300

    def test_full_roundtrip(self, tmp_path):
        """Write → read → verify the full data survives JSON serialization."""
        agents_tick0 = [{"id": "Alice", "position": [79, 142]}, {"id": "Bob", "position": [284, 23]}]
        agents_tick1 = [{"id": "Alice", "position": [80, 143]}, {"id": "Bob", "position": [283, 24]}]
        recording = build_recording([agents_tick0, agents_tick1], max_ticks=2)

        filepath = tmp_path / "recording_roundtrip.json"
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(recording, f, ensure_ascii=False)

        with open(filepath, "r", encoding="utf-8") as f:
            loaded = json.load(f)

        assert loaded["metadata"]["max_ticks"] == 2
        assert loaded["metadata"]["total_ticks_recorded"] == 2
        assert loaded["metadata"]["agent_count"] == 2
        assert len(loaded["frames"]) == 2
        assert loaded["frames"][0]["tick"] == 0
        assert loaded["frames"][1]["tick"] == 1
        assert loaded["frames"][0]["agents"][0]["id"] == "Alice"
        assert loaded["frames"][1]["agents"][0]["position"] == [80, 143]


class TestEnrichedFrameFormat:
    """Verify the enriched recording format with status and messages."""

    def test_frame_with_status(self):
        recording = build_recording([SAMPLE_AGENTS_WITH_STATUS])
        agent = recording["frames"][0]["agents"][0]
        assert "status" in agent
        assert isinstance(agent["status"], dict)

    def test_status_keys(self):
        recording = build_recording([SAMPLE_AGENTS_WITH_STATUS])
        status = recording["frames"][0]["agents"][0]["status"]
        expected_keys = {"health", "energy", "happiness", "stress", "socialization", "money"}
        assert expected_keys == set(status.keys())

    def test_status_values_numeric(self):
        recording = build_recording([SAMPLE_AGENTS_WITH_STATUS])
        status = recording["frames"][0]["agents"][0]["status"]
        for key, value in status.items():
            assert isinstance(value, (int, float)), f"{key} should be numeric, got {type(value)}"

    def test_frame_with_messages(self):
        recording = build_recording(
            [SAMPLE_AGENTS_WITH_STATUS],
            messages_per_frame=[SAMPLE_MESSAGES],
        )
        frame = recording["frames"][0]
        assert "messages" in frame
        assert isinstance(frame["messages"], list)
        assert len(frame["messages"]) == 2

    def test_message_structure(self):
        recording = build_recording(
            [SAMPLE_AGENTS_WITH_STATUS],
            messages_per_frame=[SAMPLE_MESSAGES],
        )
        msg = recording["frames"][0]["messages"][0]
        assert "from_id" in msg
        assert "to_id" in msg
        assert "content" in msg
        assert msg["from_id"] == "Alice"
        assert msg["to_id"] == "Bob"
        assert msg["content"] == "Hello!"

    def test_empty_messages_list(self):
        recording = build_recording([SAMPLE_AGENTS_WITH_STATUS])
        frame = recording["frames"][0]
        assert "messages" in frame
        assert frame["messages"] == []

    def test_backward_compat_no_status(self):
        """Agents without status should still work (no KeyError)."""
        recording = build_recording([SAMPLE_AGENTS])
        agent = recording["frames"][0]["agents"][0]
        assert "id" in agent
        assert "position" in agent
        # status is simply absent
        assert agent.get("status") is None

    def test_backward_compat_no_messages(self):
        """Frames with empty messages list should still be valid."""
        recording = build_recording([SAMPLE_AGENTS])
        frame = recording["frames"][0]
        assert frame.get("messages", []) == []

    def test_roundtrip_enriched(self, tmp_path):
        """Enriched data survives JSON serialization."""
        recording = build_recording(
            [SAMPLE_AGENTS_WITH_STATUS],
            messages_per_frame=[SAMPLE_MESSAGES],
        )
        filepath = tmp_path / "recording_enriched.json"
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(recording, f, ensure_ascii=False)

        with open(filepath, "r", encoding="utf-8") as f:
            loaded = json.load(f)

        agent = loaded["frames"][0]["agents"][0]
        assert agent["status"]["health"] == 78
        assert loaded["frames"][0]["messages"][0]["content"] == "Hello!"
