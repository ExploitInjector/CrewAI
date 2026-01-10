import os
import sys
# Biztosítjuk, hogy a Python látja az src mappát
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from crewai import Crew, Process
from src.crew.agents import IDSCrewAgents
from src.crew.tasks import IDSCrewTasks

def run_crew():
    agents_factory = IDSCrewAgents()
    tasks_factory = IDSCrewTasks()

    # Ügynökök inicializálása
    cleaner = agents_factory.data_cleaner_agent()
    correlator = agents_factory.correlator_agent()
    detector = agents_factory.detector_agent()
    explainer = agents_factory.explainer_agent()
    reporter = agents_factory.reporter_agent()

    # Feladatok definíciója és sorrendbe állítása
    t1 = tasks_factory.cleaning_task(cleaner)
    t2 = tasks_factory.correlation_task(correlator, t1)
    t3 = tasks_factory.detection_task(detector, t2)
    t4 = tasks_factory.explanation_task(explainer, t3)
    t5 = tasks_factory.reporting_task(reporter, t4)

    # A csapat (Crew) összeállítása
    ids_system = Crew(
        agents=[cleaner, correlator, detector, explainer, reporter],
        tasks=[t1, t2, t3, t4, t5],
        process=Process.sequential,
        verbose=True
    )

    print("=== IDS AUTOMATIZÁLT ELEMZÉS INDÍTÁSA ===")
    ids_system.kickoff()

if __name__ == "__main__":
    run_crew()
