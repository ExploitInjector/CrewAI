# Professional Network Correlation Report

**Analysis Scope:** 100000 network flows processed.

## 1. Traffic Intensity (Heavy Talkers)
High connection counts between specific IP pairs may indicate DoS activity or automated data exfiltration.

| src_ip       | dst_ip        |   connection_count |
|:-------------|:--------------|-------------------:|
| 192.168.1.70 | 192.168.1.90  |              98894 |
| 192.168.1.90 | 192.168.1.70  |                884 |
| 192.168.1.90 | 192.168.1.3   |                 82 |
| 136.162.16.0 | 255.255.255.1 |                 59 |
| 192.168.1.70 | 192.168.1.3   |                 48 |
| 192.168.1.3  | 192.168.1.90  |                 33 |

## 2. Scanning Activity (Port Diversity)
Sources contacting a high number of unique destination ports are likely performing reconnaissance/port scanning.

| src_ip       |   unique_ports_hit |
|:-------------|-------------------:|
| 192.168.1.90 |                663 |
| 192.168.1.70 |                  7 |
| 192.168.1.3  |                  4 |
| 136.162.16.0 |                  1 |

## 3. Protocol & Payload Statistics
Summary of data volume distributed across protocols.

|   protocol |    mean |    max |   count |
|-----------:|--------:|-------:|--------:|
|          0 |    0    |      0 |      60 |
|          6 | 2557.7  | 519561 |   13126 |
|         17 | 2088.76 |   7554 |   86814 |

### Dataset Label Distribution

| label     |   count |
|:----------|--------:|
| Malicious |   99778 |
| Benign    |     222 |

--- 
*Generated automatically by the AnalyzeCorrelationTool for SOC analysis.*## Traffic Label Distribution

| label     |   count |
|:----------|--------:|
| Malicious |   99778 |
| Benign    |     222 |

