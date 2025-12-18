import sys
import signal
if not hasattr(signal, 'SIGHUP'): signal.SIGHUP = 1

import os
from dotenv import load_dotenv
from crewai import Crew
from src.crew.agents import IDSCrewAgents
from src.crew.tasks import IDSCrewTasks

load_dotenv()

def run_cleaner():
    agents = IDSCrewAgents()
    tasks = IDSCrewTasks()

    cleaner = agents.data_cleaner_agent()
    task = tasks.cleaning_task(cleaner, "data/raw/csv/data.csv", "data/processed/cleaned.csv")

    crew = Crew(agents=[cleaner], tasks=[task], verbose=True)
    crew.kickoff()

if __name__ == "__main__":
    run_cleaner()﻿
