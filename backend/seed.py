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
    {
        "sam_id": "DEMO-2026-016",
        "title": "IVAS Mission Software Sustainment and Integration",
        "agency": "PEO Soldier, Project Manager Integrated Visual Augmentation System",
        "notice_type": "Solicitation",
        "naics_code": "541511",
        "set_aside_type": "SBP",
        "response_deadline": NOW + timedelta(days=26),
        "posted_date": NOW - timedelta(days=2),
        "description": (
            "PEO Soldier requires software sustainment, defect remediation, and feature development "
            "for the Integrated Visual Augmentation System (IVAS) mission applications running on "
            "HoloLens-derived hardware. Scope includes Unity/C# app development, DirectX graphics "
            "pipeline optimization, ruggedized device integration, and CMMC Level 2 compliance. "
            "Active Secret clearance required. Small business set-aside. Estimated value $6.4M."
        ),
    },
    {
        "sam_id": "DEMO-2026-017",
        "title": "Virginia-Class Submarine Sonar Signal Processing Software",
        "agency": "Naval Sea Systems Command (NAVSEA), PEO Submarines",
        "notice_type": "Presolicitation",
        "naics_code": "541330",
        "set_aside_type": None,
        "response_deadline": NOW + timedelta(days=42),
        "posted_date": NOW - timedelta(days=4),
        "description": (
            "NAVSEA PEO Submarines seeks engineering services for acoustic signal processing "
            "software development supporting AN/BQQ-10 sonar suites on Virginia-class SSNs. "
            "Work includes DSP algorithm development in C++, real-time embedded Linux integration, "
            "towed array data fusion, and hardware-in-the-loop testing at NUWC Newport. "
            "Full Secret clearance and prior NAVSEA experience required. Estimated value $8.7M."
        ),
    },
    {
        "sam_id": "DEMO-2026-018",
        "title": "GPS III Ground Control Segment Cybersecurity Hardening",
        "agency": "Space Systems Command (SSC), GPS Directorate, Los Angeles AFB",
        "notice_type": "Solicitation",
        "naics_code": "541512",
        "set_aside_type": "SDVOSBC",
        "response_deadline": NOW + timedelta(days=21),
        "posted_date": NOW - timedelta(days=3),
        "description": (
            "SSC GPS Directorate seeks cybersecurity hardening services for the GPS Next Generation "
            "Operational Control System (OCX). Scope includes RMF A&A package support, STIG compliance "
            "across Windows and RHEL hosts, cross-domain solution configuration, and penetration "
            "testing of ground control segment interfaces. TS/SCI with CI polygraph required. "
            "SDVOSB set-aside. Estimated value $4.2M over 3 years."
        ),
    },
    {
        "sam_id": "DEMO-2026-019",
        "title": "VA/DoD Electronic Health Record Interoperability Engineering",
        "agency": "Defense Health Agency (DHA), Cerner Millennium Program Office",
        "notice_type": "Solicitation",
        "naics_code": "541512",
        "set_aside_type": "WOSB",
        "response_deadline": NOW + timedelta(days=38),
        "posted_date": NOW - timedelta(days=5),
        "description": (
            "DHA requires integration and interoperability engineering support for the VA/DoD "
            "joint electronic health record (Cerner Millennium). Work includes HL7 FHIR API "
            "development, HIE gateway configuration, SNOMED/LOINC terminology mapping, and "
            "HIPAA compliance validation. Prior VA or DoD healthcare IT experience required. "
            "WOSB set-aside. Estimated value $5.1M."
        ),
    },
    {
        "sam_id": "DEMO-2026-020",
        "title": "Coast Guard Offshore Patrol Cutter C4ISR Integration Support",
        "agency": "US Coast Guard, Surface Forces Logistics Center",
        "notice_type": "Solicitation",
        "naics_code": "336611",
        "set_aside_type": "HZC",
        "response_deadline": NOW + timedelta(days=47),
        "posted_date": NOW - timedelta(days=7),
        "description": (
            "USCG SFLC requires systems integration support for C4ISR suites aboard Offshore "
            "Patrol Cutter (OPC) platforms. Scope includes Aegis Common Source Library integration, "
            "tactical radio installation (WSC-6, HF/VHF), shipboard network design, and "
            "IA controls validation. HUBZone set-aside. Active Secret required. Estimated value $7.9M."
        ),
    },
    {
        "sam_id": "DEMO-2026-021",
        "title": "PEO STRI Immersive Training Simulation Development",
        "agency": "Program Executive Office Simulation, Training and Instrumentation (PEO STRI), Orlando",
        "notice_type": "Sources Sought",
        "naics_code": "541511",
        "set_aside_type": "SBP",
        "response_deadline": NOW + timedelta(days=54),
        "posted_date": NOW - timedelta(days=2),
        "description": (
            "PEO STRI is conducting market research for immersive VR/AR combat training simulation "
            "development. Capabilities sought include Unreal Engine 5 scenario authoring, biomechanical "
            "motion capture integration, distributed HLA/DIS networking, and AAR analytics. "
            "Small business set-aside. Estimated value $3.6M over 4 years."
        ),
    },
    {
        "sam_id": "DEMO-2026-022",
        "title": "ADVANA Data Fusion Platform ML Engineering",
        "agency": "Office of the Under Secretary of Defense (Comptroller), ADVANA Program",
        "notice_type": "Solicitation",
        "naics_code": "541511",
        "set_aside_type": "SDVOSBC",
        "response_deadline": NOW + timedelta(days=29),
        "posted_date": NOW - timedelta(days=4),
        "description": (
            "ADVANA requires ML engineering support for the DoD enterprise data fusion and analytics "
            "platform. Scope includes Databricks pipeline development, MLflow model lifecycle management, "
            "PySpark ETL at petabyte scale, and dashboard authoring in Qlik Sense. Active Secret required. "
            "SDVOSB set-aside. Estimated value $9.8M over 3 years."
        ),
    },
    {
        "sam_id": "DEMO-2026-023",
        "title": "NSA SIGINT Mission Cloud Migration Engineering",
        "agency": "National Security Agency, Fort Meade",
        "notice_type": "Solicitation",
        "naics_code": "541511",
        "set_aside_type": None,
        "response_deadline": NOW + timedelta(days=35),
        "posted_date": NOW - timedelta(days=6),
        "description": (
            "NSA requires cloud migration engineering support moving SIGINT mission workloads from "
            "on-premises compute to the IC GovCloud (C2S) environment. Work includes Kubernetes "
            "operator development, cross-domain data diode integration, Kafka-based streaming "
            "architecture, and security control inheritance. Full-scope polygraph required. "
            "Unrestricted. Estimated value $14.2M over 4 years."
        ),
    },
    {
        "sam_id": "DEMO-2026-024",
        "title": "GEOINT Imagery Analytics and Foundation Data Engineering",
        "agency": "National Geospatial-Intelligence Agency (NGA), Springfield",
        "notice_type": "Solicitation",
        "naics_code": "541715",
        "set_aside_type": "8AN",
        "response_deadline": NOW + timedelta(days=41),
        "posted_date": NOW - timedelta(days=3),
        "description": (
            "NGA requires engineering services for GEOINT imagery analytics and foundation data "
            "production. Scope includes EO/SAR/HSI processing pipelines, CV/ML model development "
            "for object detection and change analysis, OGC-compliant web services, and foundation "
            "feature data (FFD) conflation. TS/SCI required. 8(a) set-aside. Estimated value $6.8M."
        ),
    },
    {
        "sam_id": "DEMO-2026-025",
        "title": "WMD Detection Algorithm Research and Sensor Fusion",
        "agency": "Defense Threat Reduction Agency (DTRA), Fort Belvoir",
        "notice_type": "Presolicitation",
        "naics_code": "541715",
        "set_aside_type": "SBP",
        "response_deadline": NOW + timedelta(days=62),
        "posted_date": NOW - timedelta(days=1),
        "description": (
            "DTRA is conducting market research for WMD detection algorithm research supporting "
            "chemical, biological, radiological, and nuclear (CBRN) sensor networks. Work includes "
            "Bayesian sensor fusion, spectroscopic signature analysis, anomaly detection ML models, "
            "and field experiment support. Active Secret required. Small business set-aside. "
            "Estimated value $2.9M."
        ),
    },
    {
        "sam_id": "DEMO-2026-026",
        "title": "Directed Energy Weapons Research and Prototype Development",
        "agency": "Air Force Research Laboratory (AFRL), Directed Energy Directorate, Kirtland AFB",
        "notice_type": "Solicitation",
        "naics_code": "541715",
        "set_aside_type": None,
        "response_deadline": NOW + timedelta(days=31),
        "posted_date": NOW - timedelta(days=5),
        "description": (
            "AFRL Directed Energy Directorate requires research and prototype development support "
            "for high-energy laser (HEL) and high-power microwave (HPM) weapon systems. Work includes "
            "beam control and pointing algorithms, adaptive optics, thermal management analysis, "
            "and open-air range testing at Kirtland. Active Secret required. Unrestricted. "
            "Estimated value $18.5M over 5 years."
        ),
    },
    {
        "sam_id": "DEMO-2026-027",
        "title": "G/ATOR Ground Air Task Oriented Radar Sustainment",
        "agency": "Marine Corps Systems Command (MARCORSYSCOM), Quantico",
        "notice_type": "Solicitation",
        "naics_code": "334290",
        "set_aside_type": "SDVOSBC",
        "response_deadline": NOW + timedelta(days=24),
        "posted_date": NOW - timedelta(days=4),
        "description": (
            "MARCORSYSCOM requires sustainment and obsolescence management for the AN/TPS-80 "
            "Ground/Air Task Oriented Radar (G/ATOR). Scope includes depot-level repair of GaN "
            "T/R modules, BIT software updates, cooling subsystem overhaul, and NAVAIR-standard "
            "documentation. SDVOSB set-aside. Estimated value $5.3M."
        ),
    },
    {
        "sam_id": "DEMO-2026-028",
        "title": "USCYBERCOM Offensive Cyber Tool Development Support",
        "agency": "US Cyber Command (USCYBERCOM), Fort Meade",
        "notice_type": "Solicitation",
        "naics_code": "541512",
        "set_aside_type": None,
        "response_deadline": NOW + timedelta(days=18),
        "posted_date": NOW - timedelta(days=8),
        "description": (
            "USCYBERCOM requires tool development and cyber mission force support for offensive "
            "cyber operations. Work includes low-level systems programming (C, Rust, assembly), "
            "vulnerability research, custom C2 framework development, and tool hardening. "
            "TS/SCI with CI polygraph required. Unrestricted. Estimated value $11.6M over 3 years."
        ),
    },
    {
        "sam_id": "DEMO-2026-029",
        "title": "AH-64E Apache Block III Avionics Software Support",
        "agency": "PEO Aviation, Apache Project Office, Redstone Arsenal",
        "notice_type": "Solicitation",
        "naics_code": "541330",
        "set_aside_type": "HZC",
        "response_deadline": NOW + timedelta(days=37),
        "posted_date": NOW - timedelta(days=6),
        "description": (
            "PEO Aviation Apache Project Office requires avionics software engineering support for "
            "the AH-64E Version 6 mission computer. Scope includes DO-178C Level A software "
            "development in Ada/C++, integration with Longbow fire control radar, and Link 16 "
            "data link certification. HUBZone set-aside. Active Secret required. Estimated value $7.4M."
        ),
    },
    {
        "sam_id": "DEMO-2026-030",
        "title": "MQ-25 Stingray Unmanned Aerial Refueler Integration Support",
        "agency": "Naval Air Systems Command (NAVAIR), Patuxent River",
        "notice_type": "Solicitation",
        "naics_code": "541715",
        "set_aside_type": "WOSB",
        "response_deadline": NOW + timedelta(days=28),
        "posted_date": NOW - timedelta(days=3),
        "description": (
            "NAVAIR requires systems integration and flight test support for the MQ-25 Stingray "
            "carrier-based unmanned aerial refueler. Work includes autonomous flight control "
            "validation, CATOBAR compatibility testing, aerial refueling boom dynamics analysis, "
            "and shipboard integration at NAS Pax River. Active Secret required. WOSB set-aside. "
            "Estimated value $9.2M."
        ),
    },
    {
        "sam_id": "DEMO-2026-031",
        "title": "Counter-UAS Rapid Prototyping and Fielding Support",
        "agency": "Army Rapid Capabilities and Critical Technologies Office (RCCTO)",
        "notice_type": "Sources Sought",
        "naics_code": "541715",
        "set_aside_type": "SBP",
        "response_deadline": NOW + timedelta(days=15),
        "posted_date": NOW - timedelta(days=2),
        "description": (
            "RCCTO is conducting market research for rapid prototyping and fielding of counter-UAS "
            "capabilities for Army formations. Capabilities sought include RF detection and "
            "direction finding, kinetic and non-kinetic effectors, AI-driven threat classification, "
            "and integration with FAAD C2. Small business set-aside. Estimated value $4.6M."
        ),
    },
    {
        "sam_id": "DEMO-2026-032",
        "title": "JADC2 Mesh Networking and Gateway Engineering",
        "agency": "DoD Joint All-Domain Command and Control (JADC2) Cross-Functional Team",
        "notice_type": "Solicitation",
        "naics_code": "541511",
        "set_aside_type": None,
        "response_deadline": NOW + timedelta(days=49),
        "posted_date": NOW - timedelta(days=5),
        "description": (
            "The JADC2 CFT requires engineering services to develop mesh networking and translation "
            "gateway capabilities connecting Army, Navy, Air Force, and Space Force tactical networks. "
            "Scope includes Link 16/TTNT/MADL protocol bridging, zero-trust network access, and "
            "cross-service data format normalization. TS/SCI required. Unrestricted. "
            "Estimated value $22.3M over 5 years."
        ),
    },
    {
        "sam_id": "DEMO-2026-033",
        "title": "Defense Health Agency Genomic Medicine Platform",
        "agency": "Defense Health Agency (DHA), Precision Medicine Division",
        "notice_type": "Presolicitation",
        "naics_code": "541511",
        "set_aside_type": "8AN",
        "response_deadline": NOW + timedelta(days=55),
        "posted_date": NOW - timedelta(days=1),
        "description": (
            "DHA is developing a procurement for a genomic medicine platform supporting military "
            "health system precision medicine initiatives. Work includes NGS variant calling pipeline "
            "(GATK, DeepVariant), clinical decision support integration, HIPAA-compliant cloud "
            "hosting on AWS GovCloud, and FHIR Genomics integration. 8(a) set-aside. "
            "Estimated value $8.1M."
        ),
    },
    {
        "sam_id": "DEMO-2026-034",
        "title": "USTRANSCOM Global Deployment Analytics Platform",
        "agency": "US Transportation Command (USTRANSCOM), Scott AFB",
        "notice_type": "Solicitation",
        "naics_code": "541511",
        "set_aside_type": "SDVOSBC",
        "response_deadline": NOW + timedelta(days=33),
        "posted_date": NOW - timedelta(days=4),
        "description": (
            "USTRANSCOM requires analytics platform engineering for global deployment and "
            "distribution operations. Scope includes optimization algorithms for cargo routing, "
            "digital twin simulation of strategic airlift, real-time asset tracking integration, "
            "and Power BI dashboard development. Active Secret required. SDVOSB set-aside. "
            "Estimated value $6.7M over 3 years."
        ),
    },
    {
        "sam_id": "DEMO-2026-035",
        "title": "ARCENT CENTCOM Theater Operations IT Support",
        "agency": "US Army Central (ARCENT), Shaw AFB",
        "notice_type": "Solicitation",
        "naics_code": "541519",
        "set_aside_type": "HZC",
        "response_deadline": NOW + timedelta(days=22),
        "posted_date": NOW - timedelta(days=7),
        "description": (
            "ARCENT requires IT operations and sustainment support for CENTCOM theater networks "
            "across CONUS and OCONUS locations. Scope includes SIPR/NIPR enterprise administration, "
            "help desk support, satellite communications terminal operations, and network "
            "defense. Active Secret required. HUBZone set-aside. Estimated value $12.8M over 5 years."
        ),
    },
    {
        "sam_id": "DEMO-2026-036",
        "title": "INDOPACOM Exercise Planning and Simulation Support",
        "agency": "US Indo-Pacific Command (INDOPACOM), Camp Smith, Hawaii",
        "notice_type": "Solicitation",
        "naics_code": "541611",
        "set_aside_type": "WOSB",
        "response_deadline": NOW + timedelta(days=44),
        "posted_date": NOW - timedelta(days=3),
        "description": (
            "INDOPACOM requires exercise planning, scenario development, and wargaming simulation "
            "support for theater-level joint and combined exercises (Balikatan, Talisman Sabre, "
            "Cobra Gold). Prior J7/J3 planning experience and regional subject matter expertise "
            "required. TS/SCI. WOSB set-aside. Estimated value $4.3M."
        ),
    },
    {
        "sam_id": "DEMO-2026-037",
        "title": "SOCOM Special Reconnaissance ISR Platform Integration",
        "agency": "US Special Operations Command (USSOCOM), SOF AT&L",
        "notice_type": "Solicitation",
        "naics_code": "541715",
        "set_aside_type": "SBP",
        "response_deadline": NOW + timedelta(days=30),
        "posted_date": NOW - timedelta(days=5),
        "description": (
            "SOCOM SOF AT&L requires ISR platform integration support for special reconnaissance "
            "operations. Scope includes Group 1/2 UAS payload integration, SIGINT sensor fusion, "
            "multi-INT processing, exploitation, and dissemination (PED), and backhaul to "
            "distributed common ground system. TS/SCI required. Small business set-aside. "
            "Estimated value $5.9M."
        ),
    },
    {
        "sam_id": "DEMO-2026-038",
        "title": "DDG-51 Flight III Aegis Combat System Software Support",
        "agency": "Naval Sea Systems Command (NAVSEA), DDG-51 Program Office",
        "notice_type": "Solicitation",
        "naics_code": "541511",
        "set_aside_type": None,
        "response_deadline": NOW + timedelta(days=46),
        "posted_date": NOW - timedelta(days=6),
        "description": (
            "NAVSEA DDG-51 Program Office requires software sustainment for the Aegis Baseline 10 "
            "combat system on Flight III destroyers. Scope includes Ada/C++ development, SPY-6 "
            "radar interface integration, CEC data link support, and in-service engineering agent "
            "responsibilities. Active Secret required. Unrestricted. Estimated value $15.7M over 5 years."
        ),
    },
    {
        "sam_id": "DEMO-2026-039",
        "title": "F-35 Mission Data File Production and Reprogramming",
        "agency": "Air Combat Command (ACC), 53rd Wing, Eglin AFB",
        "notice_type": "Solicitation",
        "naics_code": "541715",
        "set_aside_type": "SDVOSBC",
        "response_deadline": NOW + timedelta(days=39),
        "posted_date": NOW - timedelta(days=4),
        "description": (
            "ACC 53rd Wing requires mission data file (MDF) production and reprogramming support "
            "for the F-35 Joint Strike Fighter across USAF, USN, and USMC variants. Work includes "
            "threat signature modeling, EW countermeasure optimization, and USRL/RL lab test support. "
            "TS/SCI required with SAP read-on. SDVOSB set-aside. Estimated value $8.3M."
        ),
    },
    {
        "sam_id": "DEMO-2026-040",
        "title": "M1A2 Abrams SEPv4 Tank Modernization Engineering",
        "agency": "PEO Ground Combat Systems (GCS), Warren",
        "notice_type": "Solicitation",
        "naics_code": "336992",
        "set_aside_type": "SBP",
        "response_deadline": NOW + timedelta(days=58),
        "posted_date": NOW - timedelta(days=8),
        "description": (
            "PEO GCS requires engineering support for the M1A2 SEPv4 Abrams tank modernization. "
            "Scope includes 3rd generation FLIR integration, ammunition data link, advanced "
            "meteorological sensor, and CROWS-LP remote weapons station integration. "
            "Active Secret required. Small business set-aside. Estimated value $6.1M."
        ),
    },
    {
        "sam_id": "DEMO-2026-041",
        "title": "DEVCOM C5ISR Center Rapid Prototyping Support",
        "agency": "Army DEVCOM C5ISR Center, Aberdeen Proving Ground",
        "notice_type": "Presolicitation",
        "naics_code": "541715",
        "set_aside_type": "8AN",
        "response_deadline": NOW + timedelta(days=26),
        "posted_date": NOW - timedelta(days=2),
        "description": (
            "DEVCOM C5ISR Center is developing a procurement for rapid prototyping support across "
            "tactical networking, electronic warfare, and position/navigation/timing (PNT) portfolios. "
            "Work includes software-defined radio development, waveform prototyping, anti-jam "
            "GPS research, and live-sky testing. Active Secret required. 8(a) set-aside. "
            "Estimated value $5.2M."
        ),
    },
    {
        "sam_id": "DEMO-2026-042",
        "title": "Chemical and Biological Defense Program Acquisition Support",
        "agency": "Joint Program Executive Office for CBRN Defense (JPEO-CBRND), APG",
        "notice_type": "Solicitation",
        "naics_code": "541611",
        "set_aside_type": "VSA",
        "response_deadline": NOW + timedelta(days=36),
        "posted_date": NOW - timedelta(days=5),
        "description": (
            "JPEO-CBRND requires acquisition support services for chemical and biological defense "
            "programs across JPM Medical Countermeasure Systems and JPM CBRN Sensors. Scope includes "
            "earned value management, milestone document preparation, and FDA regulatory support "
            "for MCMs. VSA (Vietnam Era Veterans) set-aside. Estimated value $3.8M."
        ),
    },
    {
        "sam_id": "DEMO-2026-043",
        "title": "Army Mission and Installation Contracting Small Business Support",
        "agency": "Army Mission and Installation Contracting Command (MICC), Fort Sam Houston",
        "notice_type": "Solicitation",
        "naics_code": "541611",
        "set_aside_type": "EDWOSB",
        "response_deadline": NOW + timedelta(days=20),
        "posted_date": NOW - timedelta(days=3),
        "description": (
            "Army MICC requires contract specialist and small business advocacy support across "
            "OCONUS installations. Scope includes acquisition planning, market research, source "
            "selection support, and FAR/DFARS compliance review. EDWOSB set-aside. "
            "Estimated value $2.7M."
        ),
    },
    {
        "sam_id": "DEMO-2026-044",
        "title": "DFAS Payroll System Legacy Mainframe Migration",
        "agency": "Defense Finance and Accounting Service (DFAS), Indianapolis",
        "notice_type": "Solicitation",
        "naics_code": "541511",
        "set_aside_type": "HZC",
        "response_deadline": NOW + timedelta(days=52),
        "posted_date": NOW - timedelta(days=7),
        "description": (
            "DFAS requires a contractor for legacy mainframe modernization of military payroll "
            "systems currently running on IBM z/OS with COBOL and JCL. Scope includes refactoring "
            "to Java microservices on AWS GovCloud, DB2 to PostgreSQL data migration, and "
            "parallel run validation. HUBZone set-aside. Estimated value $19.4M over 4 years."
        ),
    },
    {
        "sam_id": "DEMO-2026-045",
        "title": "Air National Guard Cyber Protection Team Support",
        "agency": "Air National Guard Readiness Center, Joint Base Andrews",
        "notice_type": "Solicitation",
        "naics_code": "541512",
        "set_aside_type": "SDVOSBC",
        "response_deadline": NOW + timedelta(days=27),
        "posted_date": NOW - timedelta(days=4),
        "description": (
            "ANG Readiness Center requires cyber protection team (CPT) support across 54 wings. "
            "Scope includes defensive cyber operations (DCO) tool development, host-based analyst "
            "tooling, threat hunting, and exercise support for Cyber Shield. Active Secret required. "
            "SDVOSB set-aside. Estimated value $7.2M."
        ),
    },
    {
        "sam_id": "DEMO-2026-046",
        "title": "OUSD R&E Advanced Manufacturing Research Support",
        "agency": "Office of the Under Secretary of Defense for Research and Engineering",
        "notice_type": "Presolicitation",
        "naics_code": "541715",
        "set_aside_type": None,
        "response_deadline": NOW + timedelta(days=64),
        "posted_date": NOW - timedelta(days=1),
        "description": (
            "OUSD R&E is developing a procurement for advanced manufacturing research support "
            "spanning additive manufacturing for metals, composite tooling, and AI-driven process "
            "control. Work includes DMLS/EBAM process optimization, digital thread implementation, "
            "and ManTech program integration. Unrestricted. Estimated value $16.9M over 5 years."
        ),
    },
    {
        "sam_id": "DEMO-2026-047",
        "title": "Pacific Fleet IT Enterprise Administration Services",
        "agency": "US Pacific Fleet (PACFLT), Pearl Harbor",
        "notice_type": "Solicitation",
        "naics_code": "541519",
        "set_aside_type": "WOSB",
        "response_deadline": NOW + timedelta(days=34),
        "posted_date": NOW - timedelta(days=6),
        "description": (
            "PACFLT requires IT enterprise administration across fleet afloat and ashore commands. "
            "Scope includes Navy Marine Corps Intranet (NMCI) liaison, afloat network operations, "
            "NIPR/SIPR sustainment, and Microsoft 365 GCC High administration. Active Secret "
            "required. WOSB set-aside. Estimated value $10.5M over 5 years."
        ),
    },
    {
        "sam_id": "DEMO-2026-048",
        "title": "DLA Troop Support Medical Supply Chain IT Modernization",
        "agency": "Defense Logistics Agency (DLA) Troop Support, Philadelphia",
        "notice_type": "Solicitation",
        "naics_code": "541511",
        "set_aside_type": "8AN",
        "response_deadline": NOW + timedelta(days=48),
        "posted_date": NOW - timedelta(days=5),
        "description": (
            "DLA Troop Support requires IT modernization for medical supply chain operations "
            "supporting DoD, VA, and FEMA. Scope includes SAP S/4HANA integration, EDI 850/855/856 "
            "transaction processing, FDA UDI compliance, and supplier portal development. "
            "8(a) set-aside. Estimated value $11.9M over 4 years."
        ),
    },
    {
        "sam_id": "DEMO-2026-049",
        "title": "DHS S&T Border Security AI and Computer Vision Research",
        "agency": "DHS Science and Technology Directorate, Border Security Division",
        "notice_type": "Solicitation",
        "naics_code": "541715",
        "set_aside_type": "SBP",
        "response_deadline": NOW + timedelta(days=43),
        "posted_date": NOW - timedelta(days=4),
        "description": (
            "DHS S&T requires AI and computer vision research supporting southern and northern "
            "border security operations. Work includes EO/IR sensor fusion, person/vehicle "
            "detection at range, small drone detection, and edge inference deployment on "
            "ruggedized platforms. Small business set-aside. Estimated value $4.8M over 3 years."
        ),
    },
    {
        "sam_id": "DEMO-2026-050",
        "title": "DTIC Scientific and Technical Information Portal Modernization",
        "agency": "Defense Technical Information Center (DTIC), Fort Belvoir",
        "notice_type": "Solicitation",
        "naics_code": "541511",
        "set_aside_type": "EDWOSB",
        "response_deadline": NOW + timedelta(days=32),
        "posted_date": NOW - timedelta(days=2),
        "description": (
            "DTIC requires modernization engineering for the Scientific and Technical Information "
            "Network (STINET) portal supporting DoD researchers and contractors. Scope includes "
            "Elasticsearch-based full-text search, metadata harvesting, Section 508 accessibility "
            "compliance, and React-based frontend development. Active Secret required. "
            "EDWOSB set-aside. Estimated value $3.4M."
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
