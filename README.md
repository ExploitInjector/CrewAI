Én külön futtattam az agenteket, a linken megadott helyről zip ből kicsomagoltam a data/raw mappába az ajánlott adatot: 
https://www.kaggle.com/datasets/daniaherzalla/tii-ssrc-23
Első Agent: data_cleaner.py megvártam a 8 millió soros csv végét, első agent 10-15 perc
Második Agent: correlator_full.py kb 5-10 perc, még mindig elég nagy az adat 6 millió adat van
Harmadik Agent: detector_rules ez már gyorsan lefut
Negyedik Agent: explainer.py ez már gyorsan lefut
Ötödik Agent: reportr.py ez már gyorsan lefut

Ha minden egyben van, és letöltöd a rohadt nagy adatot, akkor lefuthat egymás után is az összes Agent a run_pipeline.py scriptel.
A végén ki kell dobjon egy ilyet:

>> python run_pipeline.py

=== IDS PIPELINE START ===
[SKIP] DataCleaner (output exists: data\processed\tii_ssrc23_cleaned_full.csv)
[SKIP] Correlator (output exists: runs\correlated_events_full.csv)
[SKIP] Detector (output exists: runs\detections_top.csv)
[SKIP] Explainer (output exists: runs\explanations_top.json)
[SKIP] Reporter (output exists: runs\incident_cards.json)

=== IDS PIPELINE FINISHED ===
Incident cards total: 3
Incident cards exported: 3

Human-readable report:
  runs/incident_cards.md

Top suspicious entities:
  1) src_ip=192.168.1.70 | events=187 | max_risk=45
  2) src_ip=192.168.1.244 | events=7 | max_risk=45
  3) src_ip=192.168.1.177 | events=6 | max_risk=45

Pipeline completed successfully.
=============================
