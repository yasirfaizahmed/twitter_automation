"""Using the agent from Python instead of the CLI.

python examples/python_api.py
"""

from android_automation import Agent, StepEvent, Task, load_config, load_task, run_task


def show(ev: StepEvent) -> None:
	print(f"[{ev.index + 1}] {ev.action} -> {ev.feedback}")
	if ev.step.plan:
		print("    plan:", " | ".join(ev.step.plan))


def main() -> None:
	# configs/default.yaml + any overrides you like
	config = load_config(overrides={"agent.max_steps": 20})
	agent = Agent.from_config(config, on_step=show)

	# 1. A free-form goal. Information comes back in result.answer.
	result = run_task(agent, Task(goal="What is the current battery percentage?", app="settings"))
	print(result.status, result.answer, result.run_dir)

	# 2. A reusable task file with parameters.
	task = load_task("examples/tasks/youtube_search.yaml")
	result = run_task(agent, task, params={"query": "Surah Ar-Rahman recitation"})
	print(result.status, result.answer)

	# 3. Chain tasks: only post once the login succeeded.
	if run_task(agent, load_task("examples/tasks/x_login.yaml")).success:
		run_task(agent, load_task("examples/tasks/x_post.yaml"), params={"text": "Bismillah"})


if __name__ == "__main__":
	main()
