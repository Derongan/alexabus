import sys
from pygtfsdb.GtfsDb import GtfsDb
from TransitFeedAPI import TransitFeedAPI
from config import *
import traceback
import logging


if __name__ == "__main__":
    tapi = TransitFeedAPI(TRANSIT_FEED_API_KEY)

    # DB_ENDPOINT = "localhost"
    # DB_USER = "postgres"
    # DB_PASSWORD = ""

    db_url = "postgresql://{user}:{password}@{endpoint}:{port}/{db}".format(endpoint=DB_ENDPOINT, db=DB_NAME,
                                                                            user=DB_USER,
                                                                            password=DB_PASSWORD, port=DB_PORT)
    gtdb = GtfsDb(db_url, spatial=True, batch_size=3000)

    feed_ids = tapi.get_california_feed_ids()

    for fid in feed_ids:
        logging.info("Loading {0}".format(fid))
        try:
            url = tapi.get_feed_zip_url(fid)
        except:
            print "Problem getting url for feed {0}".format(fid)
            continue

        try:
            gtdb.load(url, fid)
        except Exception, e:
            print "Problem loading for {0}".format(fid)
            print traceback.format_exc()
            continue
