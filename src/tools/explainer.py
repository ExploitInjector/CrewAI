from langchain.tools import tool

@tool("explain_attack_vector")
def explain_attack_vector(detection_label: str):
    """
    A TII-SSRC-23 adatset osztályozási címkéje (label) alapján 
    ad részletes technikai és üzleti magyarázatot.
    Bemenet: A detektált támadás neve (string).
    """
    
    # Normalizáljuk a bemenetet (kisbetűsre, szóközök nélkül), hogy biztosan megtaláljuk
    key = detection_label.strip().lower()

    # TII-SSRC-23 Tudásbázis (Ezt bővítsd a pontos címkékkel!)
    # A kulcsok legyenek kisbetűsek!
    knowledge_base = {
        "normal": (
            "NORMÁL FORGALOM: A hálózati tevékenység megfelel a bázisvonalnak (baseline). "
            "Nem szükséges beavatkozás."
        ),
        "ddos_tcp": (
            "DDoS TCP FLOOD: A támadó nagy mennyiségű TCP csomaggal árasztotta el a szervert. "
            "Cél: A hálózati kapcsolatok (connections table) kimerítése, hogy a valós felhasználók ne érjék el a szolgáltatást."
        ),
        "ddos_udp": (
            "DDoS UDP FLOOD: Elosztott túlterheléses támadás UDP protokollon keresztül. "
            "Cél: A sávszélesség telítése hamisított (spoofed) csomagokkal."
        ),
        "port_scan": (
            "FELDERÍTÉS (PORT SCAN): A forgalom arra utal, hogy egy külső fél feltérképezi a nyitott portokat. "
            "Kockázat: A támadó sebezhető szolgáltatásokat keres a későbbi behatoláshoz."
        ),
        "brute_force": (
            "JELSZÓFELTÖRÉS (BRUTE FORCE): Sorozatos, gyors bejelentkezési kísérletek. "
            "Kockázat: Gyenge jelszavak esetén illetéktelen hozzáférés a rendszerhez."
        ),
        "backdoor": (
            "HÁTSÓ KAPU (BACKDOOR): A rendszeren lévő, korábban telepített kártékony kód aktivitása. "
            "Kockázat: A támadónak állandó hozzáférése van a belső hálózathoz."
        ),
        "xss": (
            "WEBES TÁMADÁS (XSS): Cross-Site Scripting kísérlet a HTTP forgalomban. "
            "Cél: Kártékony szkriptek futtatása a felhasználók böngészőjében."
        ),
        "ransomware": (
            "ZSAROLÓVÍRUS AKTIVITÁS: Gyanús fájlrendszer-műveletek vagy ismert C&C kommunikáció. "
            "Kritikus kockázat: Adatvesztés titkosítás miatt."
        )
    }

    # Keresés a tudásbázisban
    # Ha pontos egyezés van:
    if key in knowledge_base:
        return f"TII-SSRC-23 ADATSET ELEMZÉS:\n{knowledge_base[key]}"
    
    # Ha nincs pontos egyezés, de részleges van (pl. 'ddos_tcp_syn' -> 'ddos'):
    for known_attack, explanation in knowledge_base.items():
        if known_attack in key:
             return f"TII-SSRC-23 ADATSET ELEMZÉS (Részleges egyezés: {known_attack}):\n{explanation}"

    # Ha ismeretlen a címke
    return (
        f"ISMERETLEN TÁMADÁSI MINTA ({detection_label}). "
        "A rendszer detektálta az anomáliát, de a TII-SSRC-23 tudásbázisban nincs hozzá specifikus leírás. "
        "Javasolt a manuális log-elemzés."
    )