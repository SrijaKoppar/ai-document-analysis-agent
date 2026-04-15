"""
Executor — runs a plan of skills in sequence, passing outputs forward.
Includes logging and error handling.
"""
from app.skills.registry import registry
from app.utils.logger import AgentLogger


def execute_plan(plan, context, logger=None):
    """
    Execute a list of skills in order, threading outputs through.

    Args:
        plan: list of skill names to execute
        context: dict of initial data (e.g. {"text": "...", "file_path": "..."})
        logger: optional AgentLogger for step tracking

    Returns:
        Updated context dict with all skill outputs merged in.
    """
    if logger is None:
        logger = AgentLogger()

    data = dict(context)  # don't mutate caller's dict

    for step_name in plan:
        skill = registry.get(step_name)

        if not skill:
            logger.log_error("Executor", f"Skill not found: {step_name}")
            data[f"error_{step_name}"] = f"Skill not found: {step_name}"
            continue  # skip missing skills instead of aborting

        try:
            logger.log_step("Executing skill", step_name)

            # Filter only inputs the skill expects
            required_inputs = skill.input_schema.keys()
            filtered_input = {
                key: value for key, value in data.items() if key in required_inputs
            }

            output = skill.run(**filtered_input)

            if isinstance(output, dict):
                data.update(output)
                logger.log_result("Skill complete", f"{step_name} → {list(output.keys())}")
            else:
                logger.log_result("Skill complete", f"{step_name} → {type(output).__name__}")

        except Exception as e:
            logger.log_error("Skill failed", f"{step_name}: {str(e)}")
            data[f"error_{step_name}"] = str(e)
            # Continue with remaining skills

    return data