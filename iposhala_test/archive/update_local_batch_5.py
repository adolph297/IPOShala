import os
from pymongo import MongoClient

# FORCE LOCALHOST
MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "iposhala" # Matches .env

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db["ipo_past_master"]

# Dictionary of symbol -> website (Same as before)
updates = {
    # 1-25
    "EXCELSOFT": "https://www.excelsoftcorp.com",
    "CAPILLARY": "https://www.capillarytech.com",
    "FUJIYAMA": "https://www.utlsolarfujiyama.com",
    "TENNECO": "https://www.tennecoindia.com",
    "EMMVEE": "https://www.emmvee.com",
    "PW": "https://www.pw.live",
    "PINELABS": "https://www.pinelabs.com",
    "CURIS": "https://www.curisls.com",
    "FINBUD": "https://www.financebuddha.com",
    "BBGV": "https://groww.in",
    "SHREEJI": "https://www.shreejifmcg.com",
    "LENSKART": "https://www.lenskart.com",
    "STUDDS": "https://www.studds.com",
    "ORKLA": "https://www.orklaindia.com",
    "JLL": "https://www.jayeshlogistics.com",
    "SMC": "https://www.smcindiaonline.com",
    "MIDWEST": "https://www.midwest.in",
    "CANARAHSBC": "https://www.canarahsbclife.com",
    "RUBICON": "https://www.rubicon.co.in",
    "CRAMC": "https://www.canararobeco.com",
    "LGEIL": "https://www.lg.com/in",
    "ANANTAM": "https://www.anantamhighways.com",
    "TATACAP": "https://www.tatacapital.com",
    "SURATMUNI": "https://www.suratmunicipal.gov.in",
    "WEWORK": "https://wework.co.in",

    # 26-50
    "MUNISH": "https://www.munishforge.com",
    "BAGDIGITAL": "https://www.bagconvergence.in",
    "SHEEL": "https://www.sheelbiotech.com",
    "GREENLEAF": "https://www.greenleafenvirotech.in",
    "GLOTTIS": "https://www.glottislogistics.in",
    "FABTECH": "https://www.fabtechnologies.com",
    "VIJAYPD": "http://www.vijaypdceutical.com",
    "SUBAHOTELS": "https://www.subahotels.com",
    "MPEL": "https://www.manaspolymers.com",
    "TRUALT": "https://www.trualtbioenergy.com",
    "JAINREC": "https://www.jainmetalgroup.com",
    "EPACKPEB": "http://www.epackprefab.com",
    "BMWVENTLTD": "https://www.bmwventures.com",
    "GURUNANAK": "https://www.gnagro.com",
    "ARSSBL": "https://www.anandrathi.com",
    "STYL": "https://www.seshaasai.com",
    "SOLARWORLD": "https://www.worldsolar.in",
    "JARO": "https://www.jaroeducation.com",
    "ECOLINE": "https://www.ecoline.net.in",
    "MGSL": "https://www.matrix-geo.com",
    "GANESHCP": "https://ganesh.co.in",
    "ATLANTAELE": "https://www.aetrafo.com",
    "PRIMECAB": "https://www.primecabindia.com",
    "SAATVIK": "https://www.saatvikgroup.com",
    "GKENERGY": "https://www.gkenergy.in",

    # 51-75
    "SIDDHICOTS": "https://www.siddhicotspin.com",
    "IVALUE": "https://www.ivalue.co.in",
    "VMSTMT": "https://www.vmstmt.com",
    "EUROPRATIK": "https://www.europratik.com",
    "TECHD": "https://www.techdefencelabs.com",
    "URBANCO": "https://www.urbancompany.com",
    "SHRINGARMS": "https://www.shringar.ms",
    "DEVX": "https://devx.work",
    "GML": "https://galaxy.in",
    "TAURIAN": "https://www.taurianmps.com",
    "VIGOR": "https://vigorplastindia.com",
    "OPTIVALUE": "https://optivaluetek.com",
    "AMANTA": "https://amanta.co.in",
    "SNEHAA": "https://www.snehaaorganics.com",
    "VIKRAN": "https://www.vikrangroup.com",
    "AHCL": "https://www.anlon.in",
    "CURRENT": "http://www.currentinfra.com",
    "SATTVAENGG": "https://sattvaengg.in",
    "ANONDITA": "https://www.anonditamedicare.com",
    "SHIVASHRIT": "https://www.shivashritfoods.com",
    "CLASSICEIL": "https://classicelectrodes.com",
    "ARCIIL": "https://www.arcinsulations.com",
    "MEIL": "https://mangals.com",
    "VIKRAMSOLR": "https://www.vikramsolar.com",
    "SHREEJISPG": "https://shreejishipping.in",

    # 76-100
    "GEMAROMA": "https://gemaromatics.in",
    "PATELRMART": "https://patelrpl.in",
    "STUDIOLSD": "https://www.studiolsd.in",
    "REGAAL": "https://regaal.in",
    "MRIL": "https://www.mripl.net",
    "BLUESTONE": "https://www.bluestone.com",
    "AMCL": "https://anbmetalcast.com",
    "MEDISTEP": "http://www.medistephc.com",
    "JSWCEMENT": "https://www.jswcement.in",
    "ALLTIME": "https://www.alltimeplastics.com",
    "CONNPLEX": "https://www.theconnplex.com",
    "SAWALIYA": "https://sawaliyafood.com",
    "KRT": "https://www.knowledgerealtytrust.com",
    "HILINFRA": "https://www.highwayinfrastructure.in",
    "BHADORA": "https://www.vidhutcables.com",
    "AARADHYA": "https://aaradhyadisposalindustries.co.in",
    "PARTH": "https://parthelectricals.in",
    "JYOTIGLOBL": "https://jyotiglobalplast.com",
    "FLYSBS": "https://www.sbsaviation.in",
    "RNPL": "https://www.renolpolychem.com",
    "CUDML": "https://www.cashurdrive.com",
    "NSDL": "https://nsdl.co.in",
    "MBEL": "https://mbel.in",
    "LOTUSDEV": "https://lotusdevelopers.com",
    "CPPLUS": "https://www.cpplusworld.com",
}

def update_websites():
    print(f"Updating Local DB: {DB_NAME} at {MONGO_URI}")
    count = 0
    for symbol, website in updates.items():
        if website:
            result = collection.update_one(
                {"symbol": symbol},
                {"$set": {"company_website": website}}
            )
            if result.modified_count > 0:
                print(f"Updated {symbol}: {website}")
                count += 1
            else:
                 # Check existence
                doc = collection.find_one({"symbol": symbol})
                if doc:
                    if doc.get("company_website") == website:
                        pass # Already updated
                    else:
                        print(f"Skipped {symbol}: Document found but update failed?")
                else:
                    print(f"Warning: Symbol {symbol} not found in Local DB")

    print(f"Total companies updated in local batch: {count}")

if __name__ == "__main__":
    update_websites()
