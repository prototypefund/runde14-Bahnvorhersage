TRAIN_SPEED_MS = 70  # ~ 250 km/h
MAX_SECONDS_DRIVING_AWAY = int(30_000 / TRAIN_SPEED_MS)  # driving away for 30 km
N_MINIMAL_ROUTES_TO_DESTINATION = 8
MAX_TRANSFERS = 4
NO_TRIP_ID = 0
NO_STOP_ID = 0
MAX_EXPECTED_DELAY_SECONDS = 60 * 30
MINIMAL_DISTANCE_DIFFERENCE = 1000  # 1 km
EXTRA_TIME_BEFORE_EARLY_STOP = 60 * 60 * 2 # 2 hour
MINIMUM_TRANSFER_TIME = 60 * 3  # 3 minutes