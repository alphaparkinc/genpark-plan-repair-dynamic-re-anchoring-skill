"""
Example usage of Plan Repair Dynamic Re-Anchoring Skill.
"""

from client import PlanRepairEngine


def main():
    print("=== Plan Repair Dynamic Re-Anchoring Demonstration ===")
    repair_engine = PlanRepairEngine()

    # Define build pipeline DAG:
    # clone_repo -> [compile_binary, fetch_assets]
    # compile_binary -> run_fast_tests -> deploy_binary
    # fetch_assets -> upload_cdn
    # deploy_binary + upload_cdn -> verify_release
    repair_engine.register_step("clone_repo", [])
    repair_engine.register_step("compile_binary", ["clone_repo"], fallback_actions=["compile_container_fallback"])
    repair_engine.register_step("fetch_assets", ["clone_repo"])
    repair_engine.register_step("run_fast_tests", ["compile_binary"])
    repair_engine.register_step("deploy_binary", ["run_fast_tests"])
    repair_engine.register_step("upload_cdn", ["fetch_assets"])
    repair_engine.register_step("verify_release", ["deploy_binary", "upload_cdn"])

    original_plan = ["clone_repo", "compile_binary", "fetch_assets", "run_fast_tests", "upload_cdn", "deploy_binary", "verify_release"]
    completed = ["clone_repo"]
    failed = "compile_binary"

    print("Original Plan:", original_plan)
    print("Failure at step:", failed)

    repair_res = repair_engine.repair_plan(original_plan, failed, completed)
    print("\nPlan Repair Result:")
    print("  Repair Possible: ", repair_res["repair_possible"])
    print("  Affected Subgraph:", repair_res["affected_steps"])
    print("  Preserved Steps: ", repair_res["preserved_steps"])
    print("  Repaired Plan:   ", repair_res["repaired_plan_suffix"])
    print(f"  Efficiency: Saved {repair_res['steps_saved']} steps from total invalidation!")


if __name__ == "__main__":
    main()
