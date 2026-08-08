"""QuantumDNA dependency blast-radius engine."""

from __future__ import annotations

import json
from collections import deque


# Internal QuantumDNA model.
# This is NOT an official NIST formula.

WEIGHT_COUNT = 70
WEIGHT_DEPTH = 30


def count_contribution(affected_count: int) -> int:
    """Score how many downstream assets are affected."""

    if affected_count >= 7:
        return 100

    if affected_count >= 5:
        return 75

    if affected_count >= 3:
        return 50

    if affected_count >= 1:
        return 25

    return 0


def depth_contribution(depth: int) -> int:
    """Score the maximum dependency depth."""

    if depth >= 5:
        return 100

    if depth >= 4:
        return 80

    if depth >= 3:
        return 60

    if depth >= 2:
        return 40

    if depth >= 1:
        return 20

    return 0


def blast_radius_level(score: int) -> str:
    """Convert a 0-100 score into a blast-radius level."""

    if score >= 81:
        return "CRITICAL"

    if score >= 61:
        return "HIGH"

    if score >= 31:
        return "MODERATE"

    return "LOW"


def calculate_blast_radius(
    asset_id: str,
    graph: dict[str, list[str]],
) -> dict:
    """
    Determine the downstream blast radius of a cryptographic asset.

    The starting asset itself is never counted as affected.
    Breadth-first search handles dependency chains and cycles.
    The input graph is not modified.
    """

    if asset_id not in graph:
        return {
            "asset_id": asset_id,
            "direct_dependencies": [],
            "affected_assets": [],
            "affected_asset_count": 0,
            "dependency_depth": 0,
            "blast_radius_score": 0,
            "blast_radius_level": "LOW",
            "explanation": (
                f"{asset_id} was not found in the dependency graph, "
                "so no downstream blast radius could be determined."
            ),
        }

    direct_dependencies = []

    for dependency in graph.get(asset_id, []):
        if dependency not in direct_dependencies:
            direct_dependencies.append(dependency)

    # Breadth-first search through downstream dependencies.
    visited = {asset_id}
    affected_assets = []
    queue = deque()

    for dependency in direct_dependencies:
        if dependency not in visited:
            visited.add(dependency)
            affected_assets.append(dependency)
            queue.append((dependency, 1))

    dependency_depth = 0

    while queue:
        current, depth = queue.popleft()

        dependency_depth = max(
            dependency_depth,
            depth
        )

        for child in graph.get(current, []):
            if child not in visited:
                visited.add(child)
                affected_assets.append(child)
                queue.append((child, depth + 1))

    affected_count = len(affected_assets)

    count_score = count_contribution(
        affected_count
    )

    depth_score = depth_contribution(
        dependency_depth
    )

    score = round(
        (
            WEIGHT_COUNT * count_score
            + WEIGHT_DEPTH * depth_score
        ) / 100
    )

    level = blast_radius_level(score)

    explanation = (
        f"{asset_id} directly affects "
        f"{len(direct_dependencies)} asset(s): "
        f"{', '.join(direct_dependencies) or 'none'}. "
        f"A total of {affected_count} downstream asset(s) "
        f"are impacted across a maximum dependency depth of "
        f"{dependency_depth}. "
        f"Affected-count contribution: {count_score}/100. "
        f"Depth contribution: {depth_score}/100. "
        f"Combined blast radius: {score}/100 ({level})."
    )

    return {
        "asset_id": asset_id,
        "direct_dependencies": direct_dependencies,
        "affected_assets": affected_assets,
        "affected_asset_count": affected_count,
        "dependency_depth": dependency_depth,
        "blast_radius_score": score,
        "blast_radius_level": level,
        "explanation": explanation,
    }


if __name__ == "__main__":

    example_graph = {
        "rsa-payment": [
            "payment-api",
            "auth-service",
            "api-gateway"
        ],
        "payment-api": [
            "payment-db"
        ],
        "auth-service": [
            "identity-db"
        ],
        "api-gateway": [],
        "payment-db": [],
        "identity-db": [],
    }

    result = calculate_blast_radius(
        "rsa-payment",
        example_graph
    )

    print(
        json.dumps(
            result,
            indent=2
        )
    )