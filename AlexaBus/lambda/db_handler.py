import psycopg2


class GtfsDb(object):
    def __init__(self, url, db, user=None, password=None, port=None):
        self.url = url
        print url, db, user, password, port
        self.conn = psycopg2.connect(host=url, dbname=db, user=user, password=password, port=port)

    def get_closest_stops(self, latlng, num):
        with self.conn.cursor() as cur:
            cur.execute(GtfsDb.GET_CLOSEST_STOP, {'lat': latlng[0], 'lon': latlng[1], 'num': num})

            return cur.fetchall()

    def get_bus_times_at_stop(self, stop_pid, feed_pid):
        with self.conn.cursor() as cur:
            cur.execute(GtfsDb.GET_BUS_TIMES_AT_STOPS, {'stop_pid': stop_pid, 'feed_pid': feed_pid})
            return cur.fetchall()


with open("SQL/get_closest_stops.sql") as f:
    GtfsDb.GET_CLOSEST_STOP = f.read()

with open("SQL/get_bus_times_at_stop.sql") as f:
    GtfsDb.GET_BUS_TIMES_AT_STOPS = f.read()

if __name__ == "__main__":
    db = GtfsDb("localhost", "alexabus")

    latlng = (38.547188, -121.788848)

    # print (db.get_bus_times_at_stop(stop_id))
    closest_stop = db.get_closest_stops(latlng, 1)[0]

    print closest_stop

    closest_id = closest_stop[-2]
    gtf_id = closest_stop[-1]

    print closest_id, gtf_id
    print "The closest stop is {0} which is {1} meters away.".format(closest_stop[0], int(round(closest_stop[1], -1)))

    next_busses = db.get_bus_times_at_stop(closest_id, gtf_id)

    print next_busses

    print "There are {0} bus lines still running to this stop right now.".format(len(next_busses))
    for line in next_busses:
        print line
        print "The next {0} line bus that I know about will arive at around {1}".format(line[0],
                                                                                        line[1].strftime("%-I:%M %p"))
