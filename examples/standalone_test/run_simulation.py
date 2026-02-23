"python -m examples.standalone_test.run_simulation"

import sys
import os
import asyncio
import yaml
import time
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

project_path = os.path.dirname(os.path.abspath(__file__))

os.environ["MAS_PROJECT_ABS_PATH"] = project_path
os.environ["MAS_EVENT_LOG_DIR"] = project_path
if "MAS_PROJECT_REL_PATH" not in os.environ:
    os.environ["MAS_PROJECT_REL_PATH"] = "examples.standalone_test"

from agentkernel_standalone.mas.builder import Builder
from examples.standalone_test.registry import RESOURCES_MAPS
from agentkernel_standalone.toolkit.logger import get_logger

from examples.standalone_test.custom_controller import CustomController

logger = get_logger(__name__)


async def main():
    """Async main function to assemble and start the simulation"""
    controller = None
    system = None
    recording_frames = []
    repo_root = os.path.dirname(os.path.dirname(project_path))
    recordings_path = os.path.join(repo_root, "society-panel", "backend", "recordings")
    recording_metadata = {}
    try:
        logger.info(f"Project path set to: {project_path}")

        logger.info("Creating simulation builder...")
        sim_builder = Builder(project_path=project_path, resource_maps=RESOURCES_MAPS)

        logger.info("Assembling all simulation components...")
        controller, system = await sim_builder.init()

        # --- Recording setup ---
        os.makedirs(recordings_path, exist_ok=True)
        recording_metadata = {
            "created_at": datetime.now().isoformat(),
            "max_ticks": sim_builder.config.simulation.max_ticks,
            "map_size": 300,
        }

        # --- Load agent profiles for recording metadata ---
        profiles_path = os.path.join(project_path, "data", "agents", "profiles.jsonl")
        profiles_map = {}
        if os.path.exists(profiles_path):
            with open(profiles_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        p = json.loads(line)
                        profiles_map[p["id"]] = {
                            "personality": p.get("personality", ""),
                            "occupation": p.get("occupation", ""),
                            "goal": p.get("goal", ""),
                        }
        recording_metadata["profiles"] = profiles_map

        # --- Simulation Loop ---
        max_ticks = sim_builder.config.simulation.max_ticks
        logger.info(f"--- Starting Simulation Run for {max_ticks} ticks ---")

        num_ticks_to_run = max_ticks

        total_duration = 0
        for i in range(num_ticks_to_run):

            tick_start_time = time.time()

            await controller.step_agent()
            await system.run("messager", "dispatch_messages")

            # Apply natural tick decay to all agent statuses
            try:
                await controller.run_environment("status", "apply_tick_decay")
            except Exception as e:
                logger.warning(f"Failed to apply tick decay: {e}")

            tick_end_time = time.time()
            actual_tick_duration = tick_end_time - tick_start_time
            total_duration += actual_tick_duration

            current_tick = await system.run("timer", "get_tick")
            await system.run("timer", "add_tick", duration_seconds=actual_tick_duration)

            logger.info(f"--- Tick {current_tick} finished in {actual_tick_duration:.4f} seconds ---")

            # Collect messages sent this tick (from invoke plugin)
            tick_messages = []
            for agent_id in controller.get_agent_ids():
                try:
                    msgs = await controller.run_agent_method(agent_id, "invoke", "sent_messages")
                    if msgs:
                        for msg in msgs:
                            tick_messages.append({
                                "from_id": msg.get("from_id", ""),
                                "to_id": msg.get("to_id", ""),
                                "content": msg.get("content", ""),
                            })
                except Exception as e:
                    logger.warning(f"Failed to get messages for {agent_id}: {e}")

            # Record frame for Society Panel replay
            try:
                agents = await controller.run_environment("space", "get_all_agents")

                # Get dynamic statuses from environment plugin
                try:
                    all_statuses = await controller.run_environment("status", "get_all_statuses")
                except Exception:
                    all_statuses = {}

                enriched_agents = []
                for a in agents:
                    agent_entry = {"id": a["id"], "position": a["position"]}
                    if a["id"] in all_statuses:
                        agent_entry["status"] = all_statuses[a["id"]]
                    # Get last action type
                    try:
                        last_action = await controller.run_agent_method(a["id"], "state", "get_state", "last_action")
                        if last_action and isinstance(last_action, dict):
                            agent_entry["action"] = last_action.get("action", "unknown")
                    except Exception:
                        pass
                    enriched_agents.append(agent_entry)

                recording_frames.append({
                    "tick": current_tick,
                    "timestamp": datetime.now().isoformat(),
                    "agents": enriched_agents,
                    "messages": tick_messages,
                })
            except Exception as rec_err:
                logger.warning(f"Failed to record frame at tick {current_tick}: {rec_err}")

        if num_ticks_to_run > 0:
            average_time_per_tick = total_duration / num_ticks_to_run
            logger.info(f"\n--- Ran {num_ticks_to_run} ticks. Average time per tick: {average_time_per_tick:.4f} seconds ---")

        logger.info("\n--- Simulation Finished ---")
    except Exception as e:
        logger.error(f"Simulation failed: {e}")
        logger.exception("An unhandled exception occurred during simulation.")
    finally:
        if recording_frames:
            recording_metadata["total_ticks_recorded"] = len(recording_frames)
            recording_metadata["agent_count"] = len(recording_frames[0].get("agents", []))
            recording_data = {"metadata": recording_metadata, "frames": recording_frames}
            recording_file = os.path.join(
                recordings_path,
                f"recording_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
            try:
                with open(recording_file, "w", encoding="utf-8") as f:
                    json.dump(recording_data, f, ensure_ascii=False)
                logger.info(f"Recording saved: {recording_file}")
            except Exception as e:
                logger.error(f"Failed to save recording: {e}")

        if controller:
            result = await controller.close()
            logger.info(f"Controller close result is {result}")
        if system:
            result = await system.close()
            logger.info(f"System close result is {result}")


if __name__ == "__main__":
    try:
        asyncio.run(main())

    except KeyboardInterrupt:
        logger.info("Simulation interrupted by user. Exiting.")
    finally:
        logger.info("Simulation ended.")
