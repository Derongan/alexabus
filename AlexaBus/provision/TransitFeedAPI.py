import requests


class TransitFeedAPI(object):
    def __init__(self, key, timeout=1):
        self.key = key
        self.timeout = timeout

    def get_locations(self):
        return requests.get("https://api.transitfeeds.com/v1/getLocations", params={"key": self.key},
                            timeout=self.timeout).json()

    def get_feed_ids(self, location_id, descendants=0, type="gtfs", page=1):
        return requests.get("https://api.transitfeeds.com/v1/getFeeds", params={
            "key": self.key, "location": location_id, "descendants": descendants, "page": page,
            "limit": 100, "type": type
        }).json()

    def get_all_feed_ids(self):
        first = self.get_feed_ids(0, 0, page=0)['results']
        print first.keys()
        num_pages = first['numPages']

        res = [feed['id'] for feed in first['feeds']]

        for i in range(1, num_pages):
            nxt = self.get_feed_ids(0, 0, page=i)['results']['feeds']

            res += [feed['id'] for feed in nxt]

        return res

    def get_feed_zip_url(self, feed_id):
        return requests.get("https://api.transitfeeds.com/v1/getLatestFeedVersion", params={
            "key": self.key, "feed": feed_id
        }, allow_redirects=False).url


if __name__ == "__main__":
    from config import TRANSIT_FEED_API_KEY
    x = TransitFeedAPI(TRANSIT_FEED_API_KEY)
    print x.get_all_feed_ids()
