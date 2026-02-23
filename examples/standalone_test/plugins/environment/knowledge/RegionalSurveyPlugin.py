import random
import math
import hashlib
from typing import Dict, Any, List, Optional, Set
from agentkernel_standalone.mas.environment.base.plugin_base import GenericPlugin
from agentkernel_standalone.toolkit.logger import get_logger

logger = get_logger(__name__)


class RegionalSurveyPlugin(GenericPlugin):
    """Environment plugin managing regional survey for disaster response experiment."""

    COMPONENT_TYPE = "survey"

    ALL_ATTRIBUTES = ["structural", "water", "medical", "supply", "shelter"]

    OCCUPATION_ATTRIBUTES = {
        "structural_engineer": ["structural", "water"],
        "medical_officer": ["water", "medical"],
        "logistics_coordinator": ["medical", "supply"],
        "safety_inspector": ["supply", "shelter"],
        "community_liaison": ["shelter", "structural"],
    }

    REGIONS = [
        {"id": "riverside_park", "name": "Riverside Park", "center": [50, 50], "radius": 40},
        {"id": "central_school", "name": "Central School", "center": [250, 50], "radius": 40},
        {"id": "north_hospital", "name": "North Hospital", "center": [150, 150], "radius": 40},
        {"id": "market_square", "name": "Market Square", "center": [50, 250], "radius": 40},
        {"id": "industrial_complex", "name": "Industrial Complex", "center": [250, 250], "radius": 40},
    ]

    def __init__(self, seed=42):
        super().__init__()
        self.seed = seed

        # Generate true values for each region's 5 attributes
        rng = random.Random(seed)
        self._true_values: Dict[str, Dict[str, float]] = {}
        for region in self.REGIONS:
            # Retry until total is in [60, 90] after clipping
            for _ in range(100):
                attrs = {a: rng.randint(3, 18) for a in self.ALL_ATTRIBUTES}
                total = sum(attrs.values())
                if 60 <= total <= 90:
                    break
                target = rng.uniform(60, 90)
                scale = target / total
                attrs = {a: max(0, min(20, round(v * scale))) for a, v in attrs.items()}
                if 60 <= sum(attrs.values()) <= 90:
                    break
            self._true_values[region["id"]] = attrs

        # Dict[agent_id, Dict[region_id, Dict[attr_name, List[float]]]]
        self._observations: Dict[str, Dict[str, Dict[str, List[float]]]] = {}
        # Track which (from_id, to_id) pairs have already shared to prevent duplicate transfers
        self._shared_pairs: Set[tuple] = set()

        logger.info(
            f"RegionalSurveyPlugin initialized with {len(self.REGIONS)} regions, seed={seed}. "
            f"True totals: {{{', '.join(f'{rid}: {sum(attrs.values())}' for rid, attrs in self._true_values.items())}}}"
        )

    async def observe_region(self, agent_id: str, agent_position: list, occupation: str) -> Optional[Dict]:
        """Observe attributes of a region if agent is within radius."""
        ax, ay = agent_position[0], agent_position[1]

        # Find which region (if any) the agent is in
        target_region = None
        for region in self.REGIONS:
            cx, cy = region["center"]
            dist = math.sqrt((ax - cx) ** 2 + (ay - cy) ** 2)
            if dist <= region["radius"]:
                target_region = region
                break

        if target_region is None:
            return None

        region_id = target_region["id"]
        region_name = target_region["name"]

        # Get the 2 attributes this occupation can observe
        visible_attrs = self.OCCUPATION_ATTRIBUTES.get(occupation)
        if visible_attrs is None:
            return None

        # Skip if already observed this region (same agent always gets same noise)
        if agent_id in self._observations and region_id in self._observations[agent_id]:
            return None

        # Generate deterministic noise using hashlib (reproducible across processes)
        hash_input = f"{agent_id}_{region_id}_{self.seed}".encode()
        noise_seed = int(hashlib.sha256(hash_input).hexdigest(), 16) % (2**31)
        noise_rng = random.Random(noise_seed)

        observations = {}
        if agent_id not in self._observations:
            self._observations[agent_id] = {}
        self._observations[agent_id][region_id] = {}

        for attr in visible_attrs:
            true_val = self._true_values[region_id][attr]
            noisy_val = true_val + noise_rng.uniform(-5, 5)
            noisy_val = max(0.0, min(20.0, round(noisy_val, 1)))

            self._observations[agent_id][region_id][attr] = [noisy_val]
            observations[attr] = noisy_val

        logger.info(f"Agent {agent_id} ({occupation}) observed {region_name}: {observations}")
        return {"region": region_id, "region_name": region_name, "observations": observations}

    async def share_observations(self, from_id: str, to_id: str) -> int:
        """Transfer observations from from_id to to_id. Returns count of new attr-region pairs.
        Each (from, to) pair only transfers once to prevent unbounded list growth."""
        share_key = (from_id, to_id)
        if share_key in self._shared_pairs:
            logger.info(f"Agent {from_id} already shared with {to_id}, skipping")
            return 0

        from_obs = self._observations.get(from_id, {})
        if not from_obs:
            return 0

        if to_id not in self._observations:
            self._observations[to_id] = {}

        new_pairs = 0
        for region_id, attrs in from_obs.items():
            if region_id not in self._observations[to_id]:
                self._observations[to_id][region_id] = {}
            for attr, vals in attrs.items():
                if attr not in self._observations[to_id][region_id]:
                    self._observations[to_id][region_id][attr] = list(vals)
                    new_pairs += 1
                else:
                    # Only add values not already present (deduplicate)
                    existing = set(self._observations[to_id][region_id][attr])
                    for v in vals:
                        if v not in existing:
                            self._observations[to_id][region_id][attr].append(v)
                            existing.add(v)

        self._shared_pairs.add(share_key)
        if new_pairs > 0:
            logger.info(f"Agent {from_id} shared observations with {to_id}: {new_pairs} new attr-region pairs")
        return new_pairs

    async def get_agent_estimates(self, agent_id: str) -> Dict[str, Optional[float]]:
        """Compute agent's estimates for each region's total score."""
        estimates = {}
        agent_obs = self._observations.get(agent_id, {})
        for region in self.REGIONS:
            rid = region["id"]
            if rid not in agent_obs or not agent_obs[rid]:
                estimates[rid] = None
                continue
            attr_means = {}
            for attr, vals in agent_obs[rid].items():
                attr_means[attr] = sum(vals) / len(vals)
            total = sum(attr_means.values())
            n_known = len(attr_means)
            estimates[rid] = round(total * (5 / n_known), 1)  # Extrapolate to 5 attrs
        return estimates

    async def get_survey_metrics(self) -> Dict[str, Any]:
        """Compute collective survey metrics."""
        # Collect all agents' estimates
        agent_estimates: Dict[str, Dict[str, Optional[float]]] = {}
        for agent_id in self._observations:
            est = await self.get_agent_estimates(agent_id)
            agent_estimates[agent_id] = est

        # True totals per region
        true_totals = {rid: sum(attrs.values()) for rid, attrs in self._true_values.items()}

        # Collective estimate: average of all agents' estimates per region
        collective_estimates = {}
        for region in self.REGIONS:
            rid = region["id"]
            vals = [agent_estimates[aid][rid] for aid in agent_estimates if agent_estimates[aid].get(rid) is not None]
            if vals:
                collective_estimates[rid] = sum(vals) / len(vals)
            else:
                collective_estimates[rid] = None

        # Collective RMSE
        collective_errors = []
        for rid, true_total in true_totals.items():
            if collective_estimates.get(rid) is not None:
                collective_errors.append((collective_estimates[rid] - true_total) ** 2)
        collective_rmse = math.sqrt(sum(collective_errors) / len(collective_errors)) if collective_errors else 0.0

        # Individual RMSEs
        individual_rmses = []
        for agent_id, ests in agent_estimates.items():
            errors = []
            for rid, true_total in true_totals.items():
                if ests.get(rid) is not None:
                    errors.append((ests[rid] - true_total) ** 2)
            if errors:
                individual_rmses.append(math.sqrt(sum(errors) / len(errors)))

        avg_individual_rmse = sum(individual_rmses) / len(individual_rmses) if individual_rmses else 0.0
        best_individual_rmse = min(individual_rmses) if individual_rmses else 0.0

        # Diversity bonus
        diversity_bonus = avg_individual_rmse - collective_rmse

        # Attribute coverage
        observed_pairs: Set[tuple] = set()
        for agent_id, regions in self._observations.items():
            for rid, attrs in regions.items():
                for attr in attrs:
                    observed_pairs.add((rid, attr))
        attribute_coverage = len(observed_pairs) / 25.0  # 5 regions x 5 attrs

        # Estimate correlation: mean pairwise Pearson r
        estimate_correlation = self._compute_mean_pairwise_correlation(agent_estimates)

        return {
            "collective_rmse": round(collective_rmse, 4),
            "avg_individual_rmse": round(avg_individual_rmse, 4),
            "best_individual_rmse": round(best_individual_rmse, 4),
            "diversity_bonus": round(diversity_bonus, 4),
            "attribute_coverage": round(attribute_coverage, 4),
            "estimate_correlation": round(estimate_correlation, 4) if estimate_correlation is not None else None,
            "agent_count": len(self._observations),
        }

    def _compute_mean_pairwise_correlation(self, agent_estimates: Dict[str, Dict[str, Optional[float]]]) -> Optional[float]:
        """Compute mean pairwise Pearson correlation of agent estimate vectors."""
        # Build vectors: only include regions where both agents have estimates
        agent_ids = list(agent_estimates.keys())
        region_ids = [r["id"] for r in self.REGIONS]

        # Build complete estimate vectors (agents with estimates for at least 2 regions)
        vectors: Dict[str, List[float]] = {}
        for aid in agent_ids:
            vec = []
            for rid in region_ids:
                val = agent_estimates[aid].get(rid)
                if val is not None:
                    vec.append(val)
                else:
                    vec.append(None)
            vectors[aid] = vec

        # Need at least 2 agents
        valid_agents = [aid for aid in vectors if sum(1 for v in vectors[aid] if v is not None) >= 2]
        if len(valid_agents) < 2:
            return None

        correlations = []
        for i in range(len(valid_agents)):
            for j in range(i + 1, len(valid_agents)):
                r = self._pearson_r(vectors[valid_agents[i]], vectors[valid_agents[j]])
                if r is not None:
                    correlations.append(r)

        if not correlations:
            return None
        return sum(correlations) / len(correlations)

    @staticmethod
    def _pearson_r(x: List[Optional[float]], y: List[Optional[float]]) -> Optional[float]:
        """Compute Pearson correlation between two vectors (skipping None pairs)."""
        pairs = [(xi, yi) for xi, yi in zip(x, y) if xi is not None and yi is not None]
        n = len(pairs)
        if n < 2:
            return None

        xs = [p[0] for p in pairs]
        ys = [p[1] for p in pairs]

        mean_x = sum(xs) / n
        mean_y = sum(ys) / n

        cov = sum((xi - mean_x) * (yi - mean_y) for xi, yi in pairs)
        var_x = sum((xi - mean_x) ** 2 for xi in xs)
        var_y = sum((yi - mean_y) ** 2 for yi in ys)

        denom = math.sqrt(var_x * var_y)
        if denom == 0:
            return None
        return cov / denom

    async def get_agent_observation_summary(self, agent_id: str) -> Dict[str, Any]:
        """Return summary of what this agent has observed for each region."""
        agent_obs = self._observations.get(agent_id, {})
        estimates = await self.get_agent_estimates(agent_id)

        summary = {}
        for region in self.REGIONS:
            rid = region["id"]
            region_obs = agent_obs.get(rid, {})
            observed_attrs = {}
            for attr, vals in region_obs.items():
                observed_attrs[attr] = round(sum(vals) / len(vals), 1)
            summary[rid] = {
                "name": region["name"],
                "observed_attrs": observed_attrs,
                "estimated_total": estimates.get(rid),
                "n_attrs": len(observed_attrs),
            }
        return summary

    async def get_true_values(self) -> Dict[str, Dict[str, float]]:
        """Return true attribute values for all regions."""
        return self._true_values
