from iposhala_test.scripts.mongo import ipo_past_master
ipo_past_master.update_one({'symbol': 'PACEDIGITK'}, {'$set': {'website': 'https://www.pacedigitek.com/'}})
print("Updated PACEDIGITK website.")
