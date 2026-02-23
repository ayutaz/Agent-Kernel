"""
Wisdom of Crowds Scaling Experiment Runner.

Tests how collective knowledge scales with agent count.
Runs simulations with varying agent numbers and records collective metrics.

Also includes Disaster Response Survey Scaling Experiment.

Usage:
    uv run python -m examples.standalone_test.run_wisdom_experiment          # wisdom (default)
    uv run python -m examples.standalone_test.run_wisdom_experiment survey   # survey
"""

import sys
import os
import asyncio
import json
import random
import shutil
import time
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

logger = get_logger(__name__)

# Experiment parameters
AGENT_COUNTS = [10, 20, 40, 60, 80, 120]
SEEDS = [42, 123, 456]
MAX_TICKS = 100

PERSONALITIES = [
    "curious and adventurous", "friendly and talkative", "thoughtful and analytical",
    "empathetic and caring", "shrewd and resourceful", "imaginative and philosophical",
    "energetic and optimistic", "calm and patient", "bold and decisive", "playful and witty",
]
OCCUPATIONS = [
    "explorer", "socialite", "scholar", "artist", "healer",
    "merchant", "leader", "builder", "athlete", "dreamer",
]
GOALS = [
    "discover all knowledge fragments on the map",
    "share knowledge with as many agents as possible",
    "collect and spread information across the community",
    "find hidden knowledge and help others learn",
    "explore the map and share discoveries with everyone",
]


def generate_data(n_agents: int, seed: int, data_dir: str):
    """Generate agent profiles, positions, relations, and statuses for n agents."""
    rng = random.Random(seed)
    os.makedirs(data_dir, exist_ok=True)

    # Profiles
    with open(os.path.join(data_dir, "profiles.jsonl"), "w", encoding="utf-8") as f:
        for i in range(n_agents):
            profile = {
                "id": f"Agent_{i}",
                "personality": rng.choice(PERSONALITIES),
                "occupation": rng.choice(OCCUPATIONS),
                "goal": rng.choice(GOALS),
            }
            f.write(json.dumps(profile, ensure_ascii=False) + "\n")

    # Map positions (300x300)
    with open(os.path.join(data_dir, "agents.jsonl"), "w", encoding="utf-8") as f:
        for i in range(n_agents):
            agent = {
                "id": f"Agent_{i}",
                "position": [rng.randint(0, 300), rng.randint(0, 300)],
            }
            f.write(json.dumps(agent) + "\n")

    # Statuses (default values)
    with open(os.path.join(data_dir, "status.jsonl"), "w", encoding="utf-8") as f:
        for i in range(n_agents):
            status = {
                "id": f"Agent_{i}",
                "energy": 70,
                "happiness": 50,
                "stress": 30,
                "socialization": 50,
                "money": 1000,
            }
            f.write(json.dumps(status) + "\n")

    # Relations (each agent gets 2-4 random friends)
    with open(os.path.join(data_dir, "relation.jsonl"), "w", encoding="utf-8") as f:
        agent_ids = [f"Agent_{i}" for i in range(n_agents)]
        for i in range(n_agents):
            n_friends = rng.randint(2, min(4, n_agents - 1))
            others = [aid for aid in agent_ids if aid != f"Agent_{i}"]
            friends = rng.sample(others, min(n_friends, len(others)))
            for friend_id in friends:
                relation = {"source_id": f"Agent_{i}", "target_id": friend_id}
                f.write(json.dumps(relation) + "\n")


def swap_config(project_path: str):
    """Swap simulation_config.yaml with wisdom version. Returns True if backup was created."""
    configs_dir = os.path.join(project_path, "configs")
    original = os.path.join(configs_dir, "simulation_config.yaml")
    backup = os.path.join(configs_dir, "simulation_config.yaml.bak")
    wisdom = os.path.join(configs_dir, "wisdom_simulation_config.yaml")

    if os.path.exists(original):
        shutil.copy2(original, backup)
    shutil.copy2(wisdom, original)
    return True


def restore_config(project_path: str):
    """Restore original simulation_config.yaml from backup."""
    configs_dir = os.path.join(project_path, "configs")
    original = os.path.join(configs_dir, "simulation_config.yaml")
    backup = os.path.join(configs_dir, "simulation_config.yaml.bak")

    if os.path.exists(backup):
        shutil.copy2(backup, original)
        os.remove(backup)


async def run_single_experiment(n_agents: int, seed: int) -> dict:
    """Run a single simulation and return metrics by tick."""
    logger.info(f"\n{'='*60}")
    logger.info(f"Starting experiment: N={n_agents}, seed={seed}")
    logger.info(f"{'='*60}")

    # Generate data
    data_dir = os.path.join(project_path, "data", "wisdom_temp")
    generate_data(n_agents, seed, data_dir)

    controller = None
    system = None
    metrics_by_tick = []
    recording_frames = []
    repo_root = os.path.dirname(os.path.dirname(project_path))
    recordings_path = os.path.join(repo_root, "society-panel", "backend", "recordings")

    try:
        # Swap simulation_config.yaml to wisdom version for Builder
        swap_config(project_path)

        sim_builder = Builder(
            project_path=project_path,
            resource_maps=RESOURCES_MAPS,
        )
        controller, system = await sim_builder.init()

        for tick_num in range(MAX_TICKS):
            tick_start = time.time()

            await controller.step_agent()
            await system.run("messager", "dispatch_messages")

            try:
                await controller.run_environment("status", "apply_tick_decay")
            except Exception as e:
                logger.warning(f"Failed to apply tick decay: {e}")

            tick_duration = time.time() - tick_start

            current_tick = await system.run("timer", "get_tick")
            await system.run("timer", "add_tick", duration_seconds=tick_duration)

            # Collect collective metrics
            try:
                metrics = await controller.run_environment("knowledge", "get_collective_metrics")
                metrics["tick"] = current_tick
                metrics_by_tick.append(metrics)
                logger.info(f"Tick {current_tick}: coverage={metrics['global_coverage']}, "
                           f"avg_knowledge={metrics['avg_individual_knowledge']}, "
                           f"velocity={metrics['knowledge_velocity']}")
            except Exception as e:
                logger.warning(f"Failed to get collective metrics at tick {current_tick}: {e}")

            # Collect messages sent this tick
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
                except Exception:
                    pass

            # Record frame
            try:
                agents = await controller.run_environment("space", "get_all_agents")
                try:
                    all_statuses = await controller.run_environment("status", "get_all_statuses")
                except Exception:
                    all_statuses = {}

                enriched_agents = []
                for a in agents:
                    agent_entry = {"id": a["id"], "position": a["position"]}
                    if a["id"] in all_statuses:
                        agent_entry["status"] = all_statuses[a["id"]]
                    try:
                        last_action = await controller.run_agent_method(
                            a["id"], "state", "get_state", "last_action"
                        )
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
                    "collective_metrics": metrics_by_tick[-1] if metrics_by_tick else {},
                })
            except Exception as e:
                logger.warning(f"Failed to record frame: {e}")

        logger.info(f"Experiment N={n_agents}, seed={seed} completed")

    except Exception as e:
        logger.error(f"Experiment N={n_agents}, seed={seed} failed: {e}")
        logger.exception("Unhandled exception")
    finally:
        # Restore original config
        restore_config(project_path)

        # Save recording
        if recording_frames:
            os.makedirs(recordings_path, exist_ok=True)
            # Load profiles for metadata
            profiles_map = {}
            profiles_path = os.path.join(project_path, "data", "wisdom_temp", "profiles.jsonl")
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

            recording_data = {
                "metadata": {
                    "created_at": datetime.now().isoformat(),
                    "experiment_type": "wisdom_of_crowds",
                    "n_agents": n_agents,
                    "seed": seed,
                    "max_ticks": MAX_TICKS,
                    "map_size": 300,
                    "total_ticks_recorded": len(recording_frames),
                    "agent_count": n_agents,
                    "profiles": profiles_map,
                },
                "frames": recording_frames,
            }
            recording_file = os.path.join(
                recordings_path,
                f"wisdom_N{n_agents}_S{seed}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
            try:
                with open(recording_file, "w", encoding="utf-8") as f:
                    json.dump(recording_data, f, ensure_ascii=False)
                logger.info(f"Recording saved: {recording_file}")
            except Exception as e:
                logger.error(f"Failed to save recording: {e}")

        if controller:
            await controller.close()
        if system:
            await system.close()

    final_metrics = metrics_by_tick[-1] if metrics_by_tick else {}
    convergence_tick = None
    for m in metrics_by_tick:
        if m.get("global_coverage", 0) >= 1.0:
            convergence_tick = m["tick"]
            break

    return {
        "n_agents": n_agents,
        "seed": seed,
        "convergence_tick": convergence_tick,
        "final_metrics": final_metrics,
        "metrics_by_tick": metrics_by_tick,
    }


async def main():
    """Run the full scaling experiment."""
    logger.info("="*60)
    logger.info("Wisdom of Crowds Scaling Experiment")
    logger.info(f"Agent counts: {AGENT_COUNTS}")
    logger.info(f"Seeds: {SEEDS}")
    logger.info(f"Max ticks per run: {MAX_TICKS}")
    logger.info("="*60)

    all_results = []
    repo_root = os.path.dirname(os.path.dirname(project_path))

    for n_agents in AGENT_COUNTS:
        for seed in SEEDS:
            result = await run_single_experiment(n_agents, seed)
            all_results.append(result)

            # Print summary
            final = result.get("final_metrics", {})
            logger.info(f"\n--- Summary N={n_agents}, seed={seed} ---")
            logger.info(f"  Coverage: {final.get('global_coverage', 0):.1%}")
            logger.info(f"  Avg knowledge: {final.get('avg_individual_knowledge', 0):.1f}/{final.get('total_fragments', 20)}")
            logger.info(f"  Fully informed: {final.get('fully_informed_agents', 0)}")
            logger.info(f"  Convergence tick: {result.get('convergence_tick', 'N/A')}")
            logger.info(f"  Gini: {final.get('knowledge_gini', 0):.3f}")

    # Save aggregated results
    results_file = os.path.join(
        repo_root, "society-panel", "backend", "recordings",
        f"wisdom_scaling_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )
    scaling_summary = {
        "experiment": "wisdom_of_crowds_scaling",
        "created_at": datetime.now().isoformat(),
        "parameters": {
            "agent_counts": AGENT_COUNTS,
            "seeds": SEEDS,
            "max_ticks": MAX_TICKS,
            "fragment_count": 20,
            "discovery_distance": 30,
            "map_size": 300,
        },
        "results": [],
    }
    for r in all_results:
        scaling_summary["results"].append({
            "n_agents": r["n_agents"],
            "seed": r["seed"],
            "convergence_tick": r["convergence_tick"],
            "final_coverage": r["final_metrics"].get("global_coverage", 0),
            "final_avg_knowledge": r["final_metrics"].get("avg_individual_knowledge", 0),
            "final_max_knowledge": r["final_metrics"].get("max_individual_knowledge", 0),
            "final_fully_informed": r["final_metrics"].get("fully_informed_agents", 0),
            "final_gini": r["final_metrics"].get("knowledge_gini", 0),
            "metrics_by_tick": r["metrics_by_tick"],
        })

    try:
        os.makedirs(os.path.dirname(results_file), exist_ok=True)
        with open(results_file, "w", encoding="utf-8") as f:
            json.dump(scaling_summary, f, ensure_ascii=False, indent=2)
        logger.info(f"\nScaling results saved: {results_file}")
    except Exception as e:
        logger.error(f"Failed to save scaling results: {e}")

    # Print final scaling table
    logger.info("\n" + "="*70)
    logger.info("SCALING RESULTS SUMMARY")
    logger.info("="*70)
    logger.info(f"{'N':>5} | {'Seed':>5} | {'Coverage':>10} | {'Conv.Tick':>10} | {'AvgKnow':>8} | {'Gini':>6}")
    logger.info("-" * 70)
    for r in scaling_summary["results"]:
        conv = str(r["convergence_tick"]) if r["convergence_tick"] is not None else "N/A"
        logger.info(f"{r['n_agents']:>5} | {r['seed']:>5} | {r['final_coverage']:>9.1%} | {conv:>10} | {r['final_avg_knowledge']:>8.1f} | {r['final_gini']:>6.3f}")


# ===================================================================
# Disaster Response Survey Scaling Experiment
# ===================================================================

SURVEY_OCCUPATIONS = [
    "structural_engineer", "medical_officer", "logistics_coordinator",
    "safety_inspector", "community_liaison"
]

SURVEY_PERSONALITIES = [
    "careful and methodical", "quick and decisive", "thorough and detail-oriented",
    "collaborative and communicative", "calm under pressure", "analytical and logical",
    "empathetic and supportive", "organized and systematic", "adaptive and flexible",
    "experienced and confident",
]

SURVEY_AGENT_COUNTS = [10, 20, 40, 60, 80, 120]
SURVEY_CONTROL_SIZES = [10, 40, 120]
SURVEY_SEEDS = [42, 123, 456]
SURVEY_MAX_TICKS = 50


def generate_survey_data(n_agents: int, seed: int, data_dir: str, control_group: bool = False):
    """Generate agent data for disaster response survey experiment."""
    rng = random.Random(seed)
    os.makedirs(data_dir, exist_ok=True)

    # Profiles - uniform distribution of 5 occupations
    with open(os.path.join(data_dir, "profiles.jsonl"), "w", encoding="utf-8") as f:
        for i in range(n_agents):
            if control_group:
                occupation = "structural_engineer"
            else:
                occupation = SURVEY_OCCUPATIONS[i % len(SURVEY_OCCUPATIONS)]
            profile = {
                "id": f"Agent_{i}",
                "personality": rng.choice(SURVEY_PERSONALITIES),
                "occupation": occupation,
                "goal": f"Assess evacuation sites as a {occupation.replace('_', ' ')}",
            }
            f.write(json.dumps(profile, ensure_ascii=False) + "\n")

    # Map positions (300x300)
    with open(os.path.join(data_dir, "agents.jsonl"), "w", encoding="utf-8") as f:
        for i in range(n_agents):
            agent = {
                "id": f"Agent_{i}",
                "position": [rng.randint(0, 300), rng.randint(0, 300)],
            }
            f.write(json.dumps(agent) + "\n")

    # Statuses
    with open(os.path.join(data_dir, "status.jsonl"), "w", encoding="utf-8") as f:
        for i in range(n_agents):
            status = {
                "id": f"Agent_{i}",
                "energy": 100,
                "happiness": 50,
                "stress": 0,
                "socialization": 30,
                "money": 1000,
            }
            f.write(json.dumps(status) + "\n")

    # Relations (same pattern as wisdom)
    with open(os.path.join(data_dir, "relation.jsonl"), "w", encoding="utf-8") as f:
        agent_ids = [f"Agent_{i}" for i in range(n_agents)]
        for i in range(n_agents):
            n_friends = rng.randint(2, min(4, n_agents - 1))
            others = [aid for aid in agent_ids if aid != f"Agent_{i}"]
            friends = rng.sample(others, min(n_friends, len(others)))
            for friend_id in friends:
                relation = {"source_id": f"Agent_{i}", "target_id": friend_id}
                f.write(json.dumps(relation) + "\n")


def swap_survey_config(project_path: str):
    """Swap simulation_config.yaml with survey version."""
    configs_dir = os.path.join(project_path, "configs")
    original = os.path.join(configs_dir, "simulation_config.yaml")
    backup = os.path.join(configs_dir, "simulation_config.yaml.bak")
    survey = os.path.join(configs_dir, "survey_simulation_config.yaml")
    if os.path.exists(original):
        shutil.copy2(original, backup)
    shutil.copy2(survey, original)
    return True


async def run_single_survey_experiment(n_agents: int, seed: int, max_ticks: int = SURVEY_MAX_TICKS,
                                        control_group: bool = False) -> dict:
    """Run a single disaster response survey simulation."""
    group_name = "control" if control_group else "mixed"
    logger.info(f"\n{'='*60}")
    logger.info(f"Starting survey experiment: N={n_agents}, seed={seed}, group={group_name}")
    logger.info(f"{'='*60}")

    data_dir = os.path.join(project_path, "data", "survey_temp")
    generate_survey_data(n_agents, seed, data_dir, control_group)

    controller = None
    system = None
    metrics_by_tick = []
    recording_frames = []
    repo_root = os.path.dirname(os.path.dirname(project_path))
    recordings_path = os.path.join(repo_root, "society-panel", "backend", "recordings")

    try:
        swap_survey_config(project_path)

        sim_builder = Builder(
            project_path=project_path,
            resource_maps=RESOURCES_MAPS,
        )
        controller, system = await sim_builder.init()

        for tick_num in range(max_ticks):
            tick_start = time.time()

            await controller.step_agent()
            await system.run("messager", "dispatch_messages")

            try:
                await controller.run_environment("status", "apply_tick_decay")
            except Exception as e:
                logger.warning(f"Failed to apply tick decay: {e}")

            tick_duration = time.time() - tick_start
            current_tick = await system.run("timer", "get_tick")
            await system.run("timer", "add_tick", duration_seconds=tick_duration)

            # Collect survey metrics
            try:
                metrics = await controller.run_environment("survey", "get_survey_metrics")
                metrics["tick"] = current_tick
                metrics_by_tick.append(metrics)
                logger.info(
                    f"Tick {current_tick}: RMSE={metrics.get('collective_rmse', 0):.2f}, "
                    f"coverage={metrics.get('attribute_coverage', 0):.1%}, "
                    f"diversity_bonus={metrics.get('diversity_bonus', 0):.2f}"
                )
            except Exception as e:
                logger.warning(f"Failed to get survey metrics at tick {current_tick}: {e}")

            # Collect messages
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
                except Exception:
                    pass

            # Record frame
            try:
                agents = await controller.run_environment("space", "get_all_agents")
                try:
                    all_statuses = await controller.run_environment("status", "get_all_statuses")
                except Exception:
                    all_statuses = {}

                enriched_agents = []
                for a in agents:
                    agent_entry = {"id": a["id"], "position": a["position"]}
                    if a["id"] in all_statuses:
                        agent_entry["status"] = all_statuses[a["id"]]
                    try:
                        last_action = await controller.run_agent_method(
                            a["id"], "state", "get_state", "last_action"
                        )
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
                    "survey_metrics": metrics_by_tick[-1] if metrics_by_tick else {},
                })
            except Exception as e:
                logger.warning(f"Failed to record frame: {e}")

        logger.info(f"Survey experiment N={n_agents}, seed={seed}, group={group_name} completed")

    except Exception as e:
        logger.error(f"Survey experiment failed: {e}")
        logger.exception("Unhandled exception")
    finally:
        restore_config(project_path)

        # Save recording
        if recording_frames:
            os.makedirs(recordings_path, exist_ok=True)
            profiles_map = {}
            profiles_path = os.path.join(project_path, "data", "survey_temp", "profiles.jsonl")
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

            recording_data = {
                "metadata": {
                    "created_at": datetime.now().isoformat(),
                    "experiment_type": "disaster_response_survey",
                    "group": group_name,
                    "n_agents": n_agents,
                    "seed": seed,
                    "max_ticks": max_ticks,
                    "map_size": 300,
                    "total_ticks_recorded": len(recording_frames),
                    "agent_count": n_agents,
                    "profiles": profiles_map,
                },
                "frames": recording_frames,
            }
            recording_file = os.path.join(
                recordings_path,
                f"survey_{group_name}_N{n_agents}_S{seed}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
            try:
                with open(recording_file, "w", encoding="utf-8") as f:
                    json.dump(recording_data, f, ensure_ascii=False)
                logger.info(f"Recording saved: {recording_file}")
            except Exception as e:
                logger.error(f"Failed to save recording: {e}")

        if controller:
            await controller.close()
        if system:
            await system.close()

    final_metrics = metrics_by_tick[-1] if metrics_by_tick else {}
    return {
        "group": group_name,
        "n_agents": n_agents,
        "seed": seed,
        "final_metrics": final_metrics,
        "metrics_by_tick": metrics_by_tick,
    }


async def run_survey_scaling_experiment():
    """Run the full disaster response survey scaling experiment."""
    logger.info("=" * 60)
    logger.info("Disaster Response Survey Scaling Experiment")
    logger.info(f"Mixed group sizes: {SURVEY_AGENT_COUNTS}")
    logger.info(f"Control group sizes: {SURVEY_CONTROL_SIZES}")
    logger.info(f"Seeds: {SURVEY_SEEDS}")
    logger.info(f"Max ticks per run: {SURVEY_MAX_TICKS}")
    logger.info("=" * 60)

    all_results = []
    repo_root = os.path.dirname(os.path.dirname(project_path))

    # Mixed group (diverse specialists)
    for n_agents in SURVEY_AGENT_COUNTS:
        for seed in SURVEY_SEEDS:
            result = await run_single_survey_experiment(n_agents, seed, SURVEY_MAX_TICKS, control_group=False)
            all_results.append(result)
            final = result.get("final_metrics", {})
            logger.info(f"\n--- Summary: Mixed N={n_agents}, seed={seed} ---")
            logger.info(f"  RMSE: {final.get('collective_rmse', '?')}")
            logger.info(f"  Coverage: {final.get('attribute_coverage', 0):.1%}")
            logger.info(f"  Diversity bonus: {final.get('diversity_bonus', 0):.2f}")

    # Control group (all structural_engineer)
    for n_agents in SURVEY_CONTROL_SIZES:
        for seed in SURVEY_SEEDS:
            result = await run_single_survey_experiment(n_agents, seed, SURVEY_MAX_TICKS, control_group=True)
            all_results.append(result)
            final = result.get("final_metrics", {})
            logger.info(f"\n--- Summary: Control N={n_agents}, seed={seed} ---")
            logger.info(f"  RMSE: {final.get('collective_rmse', '?')}")
            logger.info(f"  Coverage: {final.get('attribute_coverage', 0):.1%}")

    # Save aggregated results
    results_file = os.path.join(
        repo_root, "society-panel", "backend", "recordings",
        f"survey_scaling_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )

    scaling_summary = {
        "experiment": "disaster_response_survey_scaling",
        "created_at": datetime.now().isoformat(),
        "parameters": {
            "mixed_agent_counts": SURVEY_AGENT_COUNTS,
            "control_agent_counts": SURVEY_CONTROL_SIZES,
            "seeds": SURVEY_SEEDS,
            "max_ticks": SURVEY_MAX_TICKS,
            "n_regions": 5,
            "n_attributes": 5,
        },
        "results": [],
    }

    for r in all_results:
        m = r.get("final_metrics", {})
        scaling_summary["results"].append({
            "group": r["group"],
            "n_agents": r["n_agents"],
            "seed": r["seed"],
            "collective_rmse": m.get("collective_rmse"),
            "avg_individual_rmse": m.get("avg_individual_rmse"),
            "best_individual_rmse": m.get("best_individual_rmse"),
            "diversity_bonus": m.get("diversity_bonus"),
            "attribute_coverage": m.get("attribute_coverage"),
            "metrics_by_tick": r.get("metrics_by_tick", []),
        })

    try:
        os.makedirs(os.path.dirname(results_file), exist_ok=True)
        with open(results_file, "w", encoding="utf-8") as f:
            json.dump(scaling_summary, f, ensure_ascii=False, indent=2)
        logger.info(f"\nScaling results saved: {results_file}")
    except Exception as e:
        logger.error(f"Failed to save scaling results: {e}")

    # Print final summary table
    logger.info("\n" + "=" * 90)
    logger.info("SURVEY SCALING RESULTS SUMMARY")
    logger.info("=" * 90)
    logger.info(f"{'Group':<10} {'N':>4} {'Seed':>5} {'RMSE':>8} {'IndRMSE':>8} {'Bonus':>8} {'Coverage':>8}")
    logger.info("-" * 90)
    for r in scaling_summary["results"]:
        rmse = f"{r['collective_rmse']:.2f}" if r['collective_rmse'] is not None else "N/A"
        ind = f"{r['avg_individual_rmse']:.2f}" if r['avg_individual_rmse'] is not None else "N/A"
        bonus = f"{r['diversity_bonus']:.2f}" if r['diversity_bonus'] is not None else "N/A"
        cov = f"{r['attribute_coverage']:.1%}" if r['attribute_coverage'] is not None else "N/A"
        logger.info(f"{r['group']:<10} {r['n_agents']:>4} {r['seed']:>5} {rmse:>8} {ind:>8} {bonus:>8} {cov:>8}")


if __name__ == "__main__":
    experiment = "wisdom"  # default
    if len(sys.argv) > 1:
        experiment = sys.argv[1]

    try:
        if experiment == "survey":
            asyncio.run(run_survey_scaling_experiment())
        else:
            asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Experiment interrupted by user.")
    finally:
        logger.info("Experiment ended.")
