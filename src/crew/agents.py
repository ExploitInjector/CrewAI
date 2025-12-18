from crewai import Agent
from langchain_community.llms import Ollama

# Közös LLM beállítás
local_llm = Ollama(model="llama3.1", base_url="http://localhost:11434")

class IDSCrewAgents:
    def data_cleaner_agent(self):
        return Agent(
            role="Adattisztító",
            goal="A nyers adatok előkészítése",
            backstory="Te vagy az 1. számú szakértő, feladatod a tisztítás.",
            llm=local_llm,
            verbose=True
        )

    def correlator_agent(self):
        return Agent(
            role="Korrelátor",
            goal="Összefüggések keresése a logokban",
            backstory="Te vagy a 2. számú szakértő, feladatod a kapcsolódási pontok keresése.",
            llm=local_llm,
            verbose=True
        )

    def detector_agent(self):
        return Agent(
            role="Detektor",
            goal="Támadások azonosítása",
            backstory="Te vagy a 3. számú szakértő, feladatod az anomáliák jelzése.",
            llm=local_llm,
            verbose=True
        )

    def explainer_agent(self):
        return Agent(
            role="Magyarázó",
            goal="Eredmények érthetővé tétele",
            backstory="Te vagy a 4. számú szakértő, feladatod a technikai adatok lefordítása.",
            llm=local_llm,
            verbose=True
        )

    def reporter_agent(self):
        return Agent(
            role="Tudósító",
            goal="Végső riport elkészítése",
            backstory="Te vagy az 5. számú szakértő, feladatod az összegzés.",
            llm=local_llm,
            verbose=True
        )
