# python
#!/usr/bin/env python
import sys
import warnings

from datetime import datetime

from my_project.crew import MyProject

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

def run():
    """
    Run the crew.
    """
    try:
        MyProject().crew().kickoff()
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")


def train():
    """
    Train the crew for a given number of iterations.
    """
    try:
        MyProject().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2])
    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")


def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        MyProject().crew().replay(task_id=sys.argv[1])
    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")


def test():
    """
    Test the crew execution and returns the results.
    """
    try:
        MyProject().crew().test(n_iterations=int(sys.argv[1]), eval_llm=sys.argv[2])
    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")


def run_with_trigger():
    """
    Run the crew with trigger payload.
    """
    import json

    if len(sys.argv) < 2:
        raise Exception("No trigger payload provided. Please provide JSON payload as argument.")

    try:
        json.loads(sys.argv[1])  # validate JSON but do not pass it as inputs
    except json.JSONDecodeError:
        raise Exception("Invalid JSON payload provided as argument")

    try:
        result = MyProject().crew().kickoff()
        return result
    except Exception as e:
        raise Exception(f"An error occurred while running the crew with trigger: {e}")