iposhala_test/
│
├── data/
│   └── IPO_Past_Issues_main.m.csv        # Canonical CSV input (source data)
│
├── scripts/
│   ├── ingest_past_ipos.py               # CSV → MongoDB ingestion (PAST IPOs)
│   ├── fetch_issue_info.py               # Enrich IPOs with documents (PDFs, ZIPs)
│   ├── fetch_live_upcoming_ipos.py       # Fetch CURRENT / UPCOMING IPOs (WIP)
│   ├── mongo.py                          # MongoDB connection & collections
│   ├── _archive/                         # Deprecated / legacy scripts
│   └── __pycache__/
│
├── nse_ipo_docs/                         # Optional downloaded IPO documents
├── venv/                                 # Python virtual environment
├── .env                                  # Environment variables
├── main.py                               # Entry placeholder (unused for now)
├── requirements.txt                     # Python dependencies
└── README.md                             # This file
