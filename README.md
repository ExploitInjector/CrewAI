ids-crewai-project/

│

├── src/                        # MINDEN Python kód

├── __init__.py

│   │

│   ├── crew/                   # CrewAI-specifikus réteg (KÖTELEZŐ)

│   │   ├── __init__.py

│   │   ├── agents.py           # 5 agent definíció

│   │   ├── tasks.py            # task lánc

│   │   └── crew_runner.py      # CrewAI indító

│   │

│   ├── tools/                  # Konkrét feldolgozó lépések

│   │   ├── __init__.py

│   │   ├── datacleaner.py      # 1. Adattisztító

│   │   ├── correlator.py       # 2. Korrelátor

│   │   ├── detector.py         # 3. Detektor

│   │   ├── explainer.py        # 4. Magyarázó

│   │   └── reporter.py         # 5. Tudósító

│   │

│   └── utils/                  # Segédfüggvények (opcionális)

│       └── __init__.py

│

├── data/                       # ADAT (lokálisan kötelező, Git-en nem)
│   ├── raw/                    # Nyers bemenet
│   │   ├── csv/
│   │   │   └── data.csv        # ~5 GB flow CSV (NEM GIT)
│   │   └── pcap/               # ~25 GB PCAP (opcionális)
│   │
│   └── processed/              # Feldolgozott adat
│       └── cleaned.csv         # DataCleaner kimenet
│
├── runs/                       # Futási artefaktumok
│   ├── correlated.csv
│   ├── detections.csv
│   └── explanations.json
│
├── results/                    # Ember által olvasható végtermék
│   ├── incident_cards.json
│   └── incident_cards.md
│
├── tests/                      # (opcionális) tesztek
│
├── .env                        # API kulcsok (NEM GIT)
├── .env.example                # minta (GIT)
├── .gitignore
├── requirements.txt
└── README.md
