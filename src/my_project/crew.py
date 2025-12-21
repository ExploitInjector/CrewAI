# python
# File: src/my_project/crew.py
import os

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task, tool
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from crewai import LLM

from my_project.tools.clean_dataframe import CleanDataFrameTool
from my_project.tools.analyze_correlation import AnalyzeCorrelationTool
from my_project.tools.detect_attacks import DetectAttacksTool
from my_project.tools.explain_attack_vector import ExplainAttackVectorTool
from my_project.tools.generate_final_report import GenerateFinalReportTool # Import the new tool


@CrewBase
class MyProject:
    def __init__(self):
        self.llm = LLM(
            model="ollama/llama3.1:8b",
            base_url="http://localhost:11434"
        )

    agents: List[BaseAgent]
    tasks: List[Task]

    # --- Tool Definitions ---
    @tool
    def clean_dataframe(self) -> CleanDataFrameTool:
        """
        Returns an instance of the CleanDataFrameTool.
        The tool id 'clean_dataframe' must match agents.yaml entry.
        """
        return CleanDataFrameTool()

    @tool
    def analyze_correlation(self) -> AnalyzeCorrelationTool:
        """
        Returns an instance of the AnalyzeCorrelationTool.
        The tool id 'analyze_correlation' must match agents.yaml entry.
        """
        return AnalyzeCorrelationTool()

    @tool
    def detect_attacks(self) -> DetectAttacksTool:
        """
        Returns an instance of the DetectAttacksTool.
        The tool id 'detect_attacks' must match agents.yaml entry.
        """
        return DetectAttacksTool()

    @tool
    def explain_attack_vector(self) -> ExplainAttackVectorTool: # Define the new tool method
        """
        Returns an instance of the ExplainAttackVectorTool.
        The tool id 'explain_attack_vector' must match agents.yaml entry.
        """
        return ExplainAttackVectorTool()

    @tool
    def generate_final_report(self) -> GenerateFinalReportTool: # Define the new tool method
        """
        Returns an instance of the GenerateFinalReportTool.
        The tool id 'generate_final_report' must match agents.yaml entry.
        """
        return GenerateFinalReportTool()

    # --- Agent Definitions ---
    @agent
    def data_cleaner(self) -> Agent:
        agent_config = self.agents_config['data_cleaner_agent']
        return Agent(
            config=agent_config,
            llm=self.llm,
            max_iter=1,  # Stops after 3 attempts/loops
            cache=False,  # Ensures fresh data processing
            tools=[self.clean_dataframe()]
        )

    @agent
    def correlator(self) -> Agent:
        agent_config = self.agents_config['correlator_agent']
        return Agent(
            config=agent_config,
            llm=self.llm,
            max_iter=1,  # Stops after 3 attempts/loops
            cache=False,  # Ensures fresh data processing
            tools=[self.analyze_correlation()]
        )

    @agent
    def detector(self) -> Agent:
        agent_config = self.agents_config['detector_agent']
        return Agent(
            config=agent_config,
            llm=self.llm,
            max_iter=1,  # Stops after 3 attempts/loops
            cache=False,  # Ensures fresh data processing
            tools=[self.detect_attacks()]
        )

    @agent
    def explainer(self) -> Agent:
        agent_config = self.agents_config['explainer_agent']
        return Agent(
            config=agent_config,
            llm=self.llm,
            max_iter=1,  # Stops after 3 attempts/loops
            cache=False,  # Ensures fresh data processing
            tools=[self.explain_attack_vector()] # Assign the new tool to the explainer agent
        )

    @agent
    def reporter(self) -> Agent:
        agent_config = self.agents_config['reporter_agent']
        return Agent(
            config=agent_config,
            llm=self.llm,
            max_iter=1,  # Stops after 3 attempts/loops
            cache=False,  # Ensures fresh data processing
            tools=[self.generate_final_report()] # Assign the new tool to the reporter agent
        )

    # --- Task Definitions ---
    @task
    def cleaning_task(self) -> Task:
        return Task(
            config=self.tasks_config['cleaning_task'],
        )

    @task
    def correlation_task(self) -> Task:
        return Task(
            config=self.tasks_config['correlation_task'],
        )

    @task
    def detection_task(self) -> Task:
        return Task(
            config=self.tasks_config['detection_task'],
        )

    @task
    def explanation_task(self) -> Task:
        return Task(
            config=self.tasks_config['explanation_task'],
        )

    @task
    def reporting_task(self) -> Task:
        return Task(
            config=self.tasks_config['reporting_task'],
            output_file='final_ids_report.md'
        )

    @crew
    def crew(self) -> Crew:
        """Létrehozza a MyProject legénységet"""

        # 1. Ügynökök példányosítása
        cleaner_agent = self.data_cleaner()
        correlator_agent = self.correlator()
        detector_agent = self.detector()
        explainer_agent = self.explainer()
        reporter_agent = self.reporter()

        # 2. Feladatok példányosítása
        # A context-ben lévő feladatoknak is már létező objektumoknak kell lenniük
        t1 = self.cleaning_task()
        t2 = self.correlation_task()
        t3 = self.detection_task()
        t4 = self.explanation_task()
        t5 = self.reporting_task()

        # 3. Kontextusok beállítása manuálisan az objektumokon (opcionális, de stabilabb)
        t2.context = [t1]
        t3.context = [t2]
        t4.context = [t3]
        t5.context = [t4]

        return Crew(
            agents=[
                cleaner_agent,
                correlator_agent,
                detector_agent,
                explainer_agent,
                reporter_agent
            ],
            tasks=[t1, t2, t3, t4, t5],
            process=Process.sequential,
            verbose=True,
        )