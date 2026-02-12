from iposhala_test.scripts.fetch_nse_company_info_into_mongo import main

def run():
    # run full update
    main(limit=None)

if __name__ == "__main__":
    run()
