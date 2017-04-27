import requests


class TransitFeedAPI(object):
    def __init__(self, key, timeout=1):
        self.key = key
        self.timeout = timeout

    def get_locations(self):
        return requests.get("https://api.transitfeeds.com/v1/getLocations", params={"key": self.key},
                            timeout=self.timeout).json()

    def get_feed_ids(self, location_id):
        return requests.get("https://api.transitfeeds.com/v1/getFeeds", params={
            "key": self.key, "location": location_id, "descendants": 0, "page": 1,
            "limit": 0
        }).json()

    def get_feed_zip_url(self, feed_id):
        return requests.get("https://api.transitfeeds.com/v1/getLatestFeedVersion", params={
            "key": self.key, "feed": feed_id
        }, allow_redirects=False).url
