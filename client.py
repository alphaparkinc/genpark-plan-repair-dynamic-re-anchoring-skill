"""
Plan Repair Dynamic Re-Anchoring Skill Client
Pure Python Standard Library implementation of Plan Repair & Subgoal Re-Anchoring (Fox et al.).
When an unexpected obstacle breaks a plan step during execution,
calculates the minimum affected subgraph, preserves valid downstream branches,
and splices in alternative recovery actions.
"""

from typing import List, Dict, Any, Tuple, Optional, Set


class PlanRepairEngine:
    """
    Plan repair engine for DAG workflows.
    Repairs broken execution steps without throwing away completed work.
    """

    def __init__(self):
        self.dependencies: Dict[str, Set[str]] = {}  # step -> set of prerequisite steps
        self.alternatives: Dict[str, List[str]] = {}  # step -> list of fallback replacement actions

    def register_step(self, step_name: str, prerequisites: List[str], fallback_actions: Optional[List[str]] = None):
        """Register workflow step with prerequisite dependencies and fallbacks."""
        self.dependencies[step_name] = set(prerequisites)
        if fallback_actions:
            self.alternatives[step_name] = fallback_actions

    def get_dependent_subgraph(self, failed_step: str) -> Set[str]:
        """Compute all downstream steps that transitively depend on failed_step."""
        affected = {failed_step}
        changed = True

        while changed:
            changed = False
            for step, prereqs in self.dependencies.items():
                if step not in affected and prereqs.intersection(affected):
                    affected.add(step)
                    changed = True

        return affected

    def repair_plan(self, original_plan: List[str], failed_step: str, completed_steps: List[str]) -> Dict[str, Any]:
        """
        Synthesize repaired plan by replacing failed_step with alternative and preserving unaffected steps.
        """
        affected = self.get_dependent_subgraph(failed_step)
        unaffected_future_steps = [s for s in original_plan if s not in completed_steps and s not in affected]
        fallbacks = self.alternatives.get(failed_step, [])

        if not fallbacks:
            return {
                "repair_possible": False,
                "error": f"No registered fallback alternatives for failed step '{failed_step}'"
            }

        # Splice fallbacks and reconstruct plan
        repaired_plan = list(fallbacks) + [s for s in original_plan if s in affected and s != failed_step] + unaffected_future_steps

        return {
            "repair_possible": True,
            "failed_step": failed_step,
            "affected_steps": list(affected),
            "preserved_steps": unaffected_future_steps,
            "repaired_plan_suffix": repaired_plan,
            "steps_saved": len(completed_steps) + len(unaffected_future_steps)
        }
