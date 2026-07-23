from __future__ import annotations


def calculate_reaction_increase(before_reactions: dict[str, float], after_reactions: dict[str, float]) -> dict[str, dict[str, float]]:
    changes: dict[str, dict[str, float]] = {}
    support_ids = set(before_reactions) | set(after_reactions)
    for support_id in sorted(support_ids):
        before = float(before_reactions.get(support_id, 0.0))
        after = float(after_reactions.get(support_id, 0.0))
        delta = after - before
        if before > 0:
            percent = (delta / before) * 100.0
        elif after > 0:
            percent = 100.0
        else:
            percent = 0.0
        changes[support_id] = {
            "before_kn": before,
            "after_kn": after,
            "delta_kn": delta,
            "increase_percent": percent,
        }
    return changes
