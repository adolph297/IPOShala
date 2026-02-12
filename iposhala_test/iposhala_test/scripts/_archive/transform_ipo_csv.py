import csv

INPUT = "data/IPO_Past_Issues_main.m.csv"
OUTPUT = "data/IPO_transform_.csv"

COLUMN_MAP = {
    "Anchor_Allocation_ZIP": "doc_anchor",
    "Red_Herring_Prospectus": "doc_rhp",
    "Bidding_Centers": "doc_bidding",
    "Sample_Application_Forms": "doc_sample",
    "Security_Parameters_Pre_Anchor": "doc_security_pre",
    "Security_Parameters_Post_Anchor": "doc_security_post",
    "Anchor_Allocation_Report": "doc_anchor_report",
}

def clean_url(value):
    if not value:
        return ""
    value = value.strip()
    return value if value.startswith("http") else ""

with open(INPUT, newline="", encoding="utf-8") as fin:
    reader = csv.DictReader(fin)

    original_fields = reader.fieldnames
    new_fields = original_fields + list(COLUMN_MAP.values())

    rows = []

    for row in reader:

        # copy original row
        new_row = dict(row)

        # add structured columns
        for src, dest in COLUMN_MAP.items():
            new_row[dest] = clean_url(row.get(src))

        rows.append(new_row)

with open(OUTPUT, "w", newline="", encoding="utf-8") as fout:
    writer = csv.DictWriter(fout, fieldnames=new_fields)
    writer.writeheader()
    writer.writerows(rows)

print("✅ CSV transformed successfully →", OUTPUT)
