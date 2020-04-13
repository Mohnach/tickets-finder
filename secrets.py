import os


travelpayouts_token = ''
if 'TRAVEL_PAYOUTS_TOKEN' in os.environ:
    travelpayouts_token = os.environ['TRAVEL_PAYOUTS_TOKEN']
