"""
MCP Server for Plan Repair Dynamic Re-Anchoring Skill.
"""

import json
import sys
from client import PlanRepairEngine

ENGINE = PlanRepairEngine()


def handle_request(req: dict) -> dict:
    method = req.get("method")
    params = req.get("params", {})

    if method == "tools/list":
        return {
            "tools": [
                {
                    "name": "register_step",
                    "description": "Register workflow DAG step with dependencies and fallback actions",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "step_name": {"type": "string"},
                            "prerequisites": {"type": "array", "items": {"type": "string"}},
                            "fallback_actions": {"type": "array", "items": {"type": "string"}}
                        },
                        "required": ["step_name", "prerequisites"]
                    }
                },
                {
                    "name": "repair_plan",
                    "description": "Dynamically repair broken plan when a step fails",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "original_plan": {"type": "array", "items": {"type": "string"}},
                            "failed_step": {"type": "string"},
                            "completed_steps": {"type": "array", "items": {"type": "string"}}
                        },
                        "required": ["original_plan", "failed_step", "completed_steps"]
                    }
                }
            ]
        }
    elif method == "tools/call":
        tool_name = params.get("name")
        args = params.get("arguments", {})

        if tool_name == "register_step":
            ENGINE.register_step(
                args["step_name"],
                args["prerequisites"],
                args.get("fallback_actions")
            )
            return {"content": [{"type": "text", "text": json.dumps({"status": "step_registered"})}]}

        elif tool_name == "repair_plan":
            res = ENGINE.repair_plan(
                args["original_plan"],
                args["failed_step"],
                args["completed_steps"]
            )
            return {"content": [{"type": "text", "text": json.dumps(res)}]}

        return {"error": f"Unknown tool: {tool_name}"}

    return {"error": f"Unknown method: {method}"}


def main():
    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            req = json.loads(line)
            resp = handle_request(req)
            resp["id"] = req.get("id")
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()
        except Exception as e:
            sys.stdout.write(json.dumps({"error": str(e)}) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
