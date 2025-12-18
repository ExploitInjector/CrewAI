from crewai import Agent
from langchain_community.llms import Ollama
from src.tools.datacleaner import clean_dataframe

local_llm = Ollama(model="llama3.1", base_url="http://localhost:11434")

class IDSCrewAgents:
    def data_cleaner_agent(self):
        return Agent(
            role="Adattisztító (DataCleaner)",
            goal="A nyers IDS logok tisztítása és egy kisebb, elemzésre alkalmas minta létrehozása.",
            backstory="Tapasztalt SOC adatmérnök vagy, aki precízen készíti elő az adatokat.",
            tools=[clean_dataframe],
            llm=local_llm,
            verbose=True,
            allow_delegation=False
        )﻿
