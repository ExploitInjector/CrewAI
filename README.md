 ids-crewai-project/

 │
 
 ├── src/                        # ALL Python source code
 
 │   ├── __init__.py
 
 │   │
 
 │   ├── crew/                   # CrewAI orchestration layer (MANDATORY)
 
 │   │   ├── __init__.py
 
 │   │   ├── agents.py           # Agent definitions (5 roles)
 
 │   │   ├── tasks.py            # Task definitions and chaining
 
 │   │   └── crew_runner.py      # Crew execution entrypoint
 
 │   │
 
 │   ├── tools/                  # Processing tools used by agents
 
 │   │   ├── __init__.py
 
 │   │   ├── datacleaner.py      # Step 1 – data cleaning
 
 │   │   ├── correlator.py       # Step 2 – flow correlation
 
 │   │   ├── detector.py         # Step 3 – rule-based detection
 
 │   │   ├── explainer.py        # Step 4 – LLM / logic explanation
 
 │   │   └── reporter.py         # Step 5 – human-readable output
 
 │   │
 
 │   └── utils/                  # Optional helper functions
 
 │       └── __init__.py
 
 │
 
 ├── data/                       # DATA (LOCAL ONLY – NOT IN GIT)
 
 │   ├── raw/
 
 │   │   ├── csv/
 
 │   │   │   └── data.csv        # ~5 GB labeled flow dataset
 
 │   │   └── pcap/               # ~25 GB packet captures (optional)
 
 │   │
 
 │   └── processed/
 
 │       └── cleaned.csv         # Output of datacleaner
 
 │
 
 ├── runs/                       # Runtime artifacts (LOCAL ONLY)
 
 │   ├── correlated.csv
 
 │   ├── detections.csv
 
 │   └── explanations.json
 
 │
 
 ├── results/                    # Final human-readable outputs
 
 │   ├── incident_cards.json
 
 │   └── incident_cards.md
 
 │
 
 ├── tests/                      # Optional tests
 
 │
 
 ├── .env                        # API keys / secrets (NOT IN GIT)
 
 ├── .env.example                # Environment template (IN GIT)
 
 ├── .gitignore
 
 ├── requirements.txt
 
 └── README.md
END OF STRUCTURE

