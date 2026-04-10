"""
Seed the database with realistic SAM.gov-style demo opportunities.
Run inside the backend container: python seed.py
"""
import os
import sys
from datetime import datetime, timezone, timedelta

from database import SessionLocal, engine
from models import create_tables, Opportunity
from embeddings import embed_texts_batch, build_opportunity_embedding_text

NOW = datetime.now(timezone.utc)

OPPORTUNITIES = [
    {
        "sam_id": "DEMO-2026-001",
        "title": "Cybersecurity Assessment and Penetration Testing Services for ARCYBER",
        "agency": "Dept of the Army, Army Cyber Command (ARCYBER)",
        "notice_type": "Solicitation",
        "naics_code": "541512",
        "set_aside_type": "8AN",
        "response_deadline": NOW + timedelta(days=5),
        "posted_date": NOW - timedelta(days=3),
        "description": (
            "ARCYBER requires a contractor to perform red team assessments, vulnerability analysis, "
            "and penetration testing across classified and unclassified networks. The contractor must "
            "hold active CMMC Level 3 certification and have personnel with active TS/SCI clearances. "
            "Services include adversarial simulation, STIG compliance review, and remediation reporting. "
            "NAICS 541512. Estimated value $2.1M. Performance period 12 months with two option years."
        ),
    },
    {
        "sam_id": "DEMO-2026-002",
        "title": "Zero Trust Architecture Implementation and Advisory Services",
        "agency": "Defense Information Systems Agency (DISA)",
        "notice_type": "Sources Sought",
        "naics_code": "541519",
        "set_aside_type": "SDVOSBC",
        "response_deadline": NOW + timedelta(days=11),
        "posted_date": NOW - timedelta(days=6),
        "description": (
            "DISA is conducting market research for Zero Trust Architecture (ZTA) implementation support "
            "across DoD enterprise networks. Scope includes identity and access management (IAM), "
            "micro-segmentation, continuous monitoring, and policy enforcement point (PEP) integration. "
            "Prior DoD network experience and familiarity with NIST SP 800-207 required. "
            "Estimated contract value $8.5M over 3 years. Respondents must be SDVOSB certified."
        ),
    },
    {
        "sam_id": "DEMO-2026-003",
        "title": "Advanced RF Electronic Warfare Systems Analysis and Modeling",
        "agency": "Air Force Research Laboratory (AFRL), Wright-Patterson AFB",
        "notice_type": "Presolicitation",
        "naics_code": "541715",
        "set_aside_type": "SBP",
        "response_deadline": NOW + timedelta(days=28),
        "posted_date": NOW - timedelta(days=1),
        "description": (
            "AFRL seeks analytical and modeling support for next-generation electronic warfare (EW) systems. "
            "Work includes RF signal modeling, spectrum deconfliction analysis, jamming waveform design, "
            "and simulation using MATLAB and MATLAB RF Toolbox. Personnel must have experience with "
            "DoD spectrum management and MIL-STD-461 compliance testing. "
            "Total estimated value $1.8M. Small business set-aside."
        ),
    },
    {
        "sam_id": "DEMO-2026-004",
        "title": "Cyber Threat Intelligence Platform Integration Support",
        "agency": "Dept of Homeland Security, Cybersecurity and Infrastructure Security Agency (CISA)",
        "notice_type": "Solicitation",
        "naics_code": "541512",
        "set_aside_type": "8AN",
        "response_deadline": NOW + timedelta(days=32),
        "posted_date": NOW - timedelta(days=5),
        "description": (
            "CISA requires integration support connecting commercial cyber threat intelligence (CTI) feeds "
            "to the EINSTEIN intrusion detection system and CISA's Automated Indicator Sharing (AIS) platform. "
            "Scope includes STIX/TAXII integration, threat feed normalization, SIEM correlation rules, "
            "and SOC analyst tooling. TS/SCI clearance required for key personnel. "
            "Period of performance 24 months. Estimated value $1.8M."
        ),
    },
    {
        "sam_id": "DEMO-2026-005",
        "title": "DoD Cloud Migration and DevSecOps Platform Engineering",
        "agency": "Dept of Defense, Office of the CIO (OCIO)",
        "notice_type": "Solicitation",
        "naics_code": "541511",
        "set_aside_type": "HZC",
        "response_deadline": NOW + timedelta(days=19),
        "posted_date": NOW - timedelta(days=4),
        "description": (
            "DoD OCIO requires cloud migration engineering and DevSecOps platform support for IL4/IL5 "
            "workloads on the Joint Warfighting Cloud Capability (JWCC). Services include CI/CD pipeline "
            "design, container security (STIG hardening, image scanning), IaC using Terraform/Ansible, "
            "and FedRAMP High authorization support. HUBZone certification required. "
            "Estimated value $4.2M over 3 years."
        ),
    },
    {
        "sam_id": "DEMO-2026-006",
        "title": "Intelligence Community IT Infrastructure Modernization Support",
        "agency": "Office of the Director of National Intelligence (ODNI)",
        "notice_type": "Solicitation",
        "naics_code": "541519",
        "set_aside_type": "WOSB",
        "response_deadline": NOW + timedelta(days=45),
        "posted_date": NOW - timedelta(days=2),
        "description": (
            "ODNI requires IT infrastructure modernization support for classified data centers. "
            "Scope includes network architecture design, hyper-converged infrastructure (HCI) deployment, "
            "storage area network (SAN) configuration, and cross-domain solution (CDS) integration. "
            "All personnel must hold active TS/SCI with CI polygraph. WOSB set-aside. "
            "Base period 12 months, four option years. Estimated total value $12M."
        ),
    },
    {
        "sam_id": "DEMO-2026-007",
        "title": "Army C2 Systems Software Development and Sustainment",
        "agency": "Program Executive Office Command, Control, Communications-Tactical (PEO C3T)",
        "notice_type": "Solicitation",
        "naics_code": "541511",
        "set_aside_type": "8AN",
        "response_deadline": NOW + timedelta(days=14),
        "posted_date": NOW - timedelta(days=7),
        "description": (
            "PEO C3T seeks software development and sustainment support for Army tactical command and control "
            "(C2) systems including WIN-T and ATAK. Work includes Android/Java development for ATAK plugins, "
            "backend microservices in Java/Python, MANET network integration, and IV&V testing. "
            "Active Secret clearance required. CMMC Level 2 compliant organization required. "
            "Estimated value $3.4M over 5 years including options."
        ),
    },
    {
        "sam_id": "DEMO-2026-008",
        "title": "Navy Shipboard Network Security Assessment and Remediation",
        "agency": "Naval Information Warfare Systems Command (NAVWAR)",
        "notice_type": "Solicitation",
        "naics_code": "541512",
        "set_aside_type": "SDVOSBC",
        "response_deadline": NOW + timedelta(days=22),
        "posted_date": NOW - timedelta(days=3),
        "description": (
            "NAVWAR requires network security assessment and remediation services for shipboard tactical "
            "networks (CANES and ISNS). Scope includes STIG compliance scanning, RMF A&A support, "
            "vulnerability remediation, and network architecture review per DISA STIGs. "
            "Personnel must hold active Secret clearance and CISSP or equivalent certification. "
            "SDVOSB set-aside. Estimated value $2.8M."
        ),
    },
    {
        "sam_id": "DEMO-2026-009",
        "title": "AI/ML Data Analytics Platform for Defense Intelligence Applications",
        "agency": "Defense Intelligence Agency (DIA)",
        "notice_type": "Presolicitation",
        "naics_code": "541511",
        "set_aside_type": "SBP",
        "response_deadline": NOW + timedelta(days=38),
        "posted_date": NOW - timedelta(days=1),
        "description": (
            "DIA is developing a procurement for AI/ML analytics platform engineering to support "
            "all-source intelligence fusion. Capabilities sought include NLP/NER for multi-source "
            "document processing, graph analytics for link analysis, MLOps pipeline engineering, "
            "and model explainability for intelligence analysts. TS/SCI required. "
            "Estimated value $6.5M. Small business set-aside."
        ),
    },
    {
        "sam_id": "DEMO-2026-010",
        "title": "Space Systems Cybersecurity and Mission Assurance",
        "agency": "Space Systems Command (SSC), Los Angeles AFB",
        "notice_type": "Sources Sought",
        "naics_code": "541512",
        "set_aside_type": "8AN",
        "response_deadline": NOW + timedelta(days=17),
        "posted_date": NOW - timedelta(days=5),
        "description": (
            "SSC seeks market information for cybersecurity and mission assurance services for space "
            "vehicle ground systems and satellite command/control infrastructure. Scope includes "
            "adversarial threat modeling, supply chain risk management (SCRM), and RMF authorization "
            "support for space systems per NSS-1652. 8(a) set-aside. Estimated value $3.1M."
        ),
    },
    {
        "sam_id": "DEMO-2026-011",
        "title": "SOCOM Special Operations IT Infrastructure Support",
        "agency": "US Special Operations Command (USSOCOM), MacDill AFB",
        "notice_type": "Solicitation",
        "naics_code": "541519",
        "set_aside_type": "8AN",
        "response_deadline": NOW + timedelta(days=9),
        "posted_date": NOW - timedelta(days=8),
        "description": (
            "USSOCOM requires IT infrastructure support across SOCOM enterprise including classified "
            "and unclassified networks at OCONUS locations. Services include Tier 2/3 help desk, "
            "network operations center (NOC) support, server/storage administration, "
            "and end-user computing. Active TS/SCI required. 8(a) set-aside. "
            "Estimated value $7.2M over 5 years."
        ),
    },
    {
        "sam_id": "DEMO-2026-012",
        "title": "Signals Intelligence Software Engineering and Algorithm Development",
        "agency": "National Security Agency (NSA), Fort Meade",
        "notice_type": "Solicitation",
        "naics_code": "541511",
        "set_aside_type": "SDVOSBC",
        "response_deadline": NOW + timedelta(days=51),
        "posted_date": NOW - timedelta(days=2),
        "description": (
            "NSA requires software engineering support for SIGINT collection and processing systems. "
            "Work includes DSP algorithm development, C++/Python signal processing pipelines, "
            "FPGA firmware development (VHDL/Verilog), and high-throughput data streaming (Kafka, Spark). "
            "Full-scope polygraph required for all personnel. SDVOSB set-aside. Estimated value $5.8M."
        ),
    },
    {
        "sam_id": "DEMO-2026-013",
        "title": "DoD Financial Management System Modernization",
        "agency": "Defense Finance and Accounting Service (DFAS)",
        "notice_type": "Presolicitation",
        "naics_code": "541511",
        "set_aside_type": "HZC",
        "response_deadline": NOW + timedelta(days=60),
        "posted_date": NOW - timedelta(days=1),
        "description": (
            "DFAS seeks a contractor for financial management system modernization including migration "
            "from legacy COBOL systems to modern Java/Python microservices on AWS GovCloud. "
            "Scope includes data migration, API development, RPA implementation, and FISCAM/FISCAM "
            "compliance testing. HUBZone set-aside. Estimated value $9.1M over 4 years."
        ),
    },
    {
        "sam_id": "DEMO-2026-014",
        "title": "Autonomous Systems Integration and Test Support for Ground Vehicles",
        "agency": "Army DEVCOM Ground Vehicle Systems Center (GVSC)",
        "notice_type": "Solicitation",
        "naics_code": "541715",
        "set_aside_type": "SBP",
        "response_deadline": NOW + timedelta(days=25),
        "posted_date": NOW - timedelta(days=4),
        "description": (
            "GVSC requires engineering support for autonomous and semi-autonomous ground vehicle systems. "
            "Work includes ROS2 integration, LIDAR/radar sensor fusion, path planning algorithm development, "
            "hardware-in-the-loop (HWIL) test support, and MIL-STD-882 safety analysis. "
            "Active Secret clearance required. Small business set-aside. Estimated value $2.4M."
        ),
    },
    {
        "sam_id": "DEMO-2026-015",
        "title": "Satellite Communications Ground Station Engineering and O&M",
        "agency": "Air Force Space Command, 50th Space Wing, Schriever SFB",
        "notice_type": "Solicitation",
        "naics_code": "517410",
        "set_aside_type": "8AN",
        "response_deadline": NOW + timedelta(days=33),
        "posted_date": NOW - timedelta(days=6),
        "description": (
            "50th Space Wing requires engineering and operations and maintenance (O&M) support for "
            "satellite communications ground stations supporting GPS and AEHF constellations. "
            "Work includes RF link budget analysis, antenna system maintenance, MILSTAR/AEHF terminal "
            "operations, and cryptographic key management (KMI). TS/SCI required. 8(a) set-aside. "
            "Estimated value $11.3M over 5 years."
        ),
    },
]


def run():
    print("Creating tables...")
    create_tables(engine)

    db = SessionLocal()
    try:
        # Check how many demo records already exist
        existing = db.query(Opportunity).filter(
            Opportunity.sam_id.like("DEMO-%")
        ).count()
        if existing > 0:
            print(f"Found {existing} existing demo records. Re-seeding...")
            db.query(Opportunity).filter(Opportunity.sam_id.like("DEMO-%")).delete()
            db.commit()

        print(f"Generating embeddings for {len(OPPORTUNITIES)} opportunities...")
        texts = [
            build_opportunity_embedding_text(
                title=o["title"],
                description=o["description"],
                naics_code=o["naics_code"],
                set_aside_type=o["set_aside_type"],
            )
            for o in OPPORTUNITIES
        ]

        embeddings = embed_texts_batch(texts)
        print(f"Embeddings generated ({len(embeddings)} vectors).")

        now = datetime.now(timezone.utc)
        for opp, embedding in zip(OPPORTUNITIES, embeddings):
            record = Opportunity(
                sam_id=opp["sam_id"],
                title=opp["title"],
                agency=opp["agency"],
                notice_type=opp["notice_type"],
                naics_code=opp["naics_code"],
                set_aside_type=opp["set_aside_type"],
                response_deadline=opp["response_deadline"],
                posted_date=opp["posted_date"],
                description=opp["description"],
                opportunity_embedding=embedding,
                synced_at=now,
            )
            db.add(record)

        db.commit()
        print(f"Seeded {len(OPPORTUNITIES)} demo opportunities.")

        # Verify
        total = db.query(Opportunity).count()
        print(f"Total opportunities in DB: {total}")

    except Exception as e:
        print(f"Seed failed: {e}", file=sys.stderr)
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run()
