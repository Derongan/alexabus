SELECT min(arrival_time), route.pid, route.route_short_name
FROM   stop_time,
       trip,
       route,
       calendar,
       agency,
       (select * FROM calendar, to_char(current_date, 'fmday') as day) as calenday
WHERE  stop_pid = %(stop_pid)s
       AND stop_time.gtfsfeed_id = %(feed_pid)s
       AND trip.gtfsfeed_id = %(feed_pid)s
       AND route.gtfsfeed_id = %(feed_pid)s
       AND stop_time.trip_pid = trip.pid
       AND trip.route_pid = route.pid
       AND trip.service_pid = calendar.pid
       AND agency.gtfsfeed_id = %(feed_pid)s
       AND route.agency_id = agency.agency_id
       AND ((calendar.monday=TRUE AND day='monday') OR
                   (calendar.tuesday=TRUE AND day='tuesday') OR
                   (calendar.wednesday=TRUE AND day='wednesday') OR
                   (calendar.thursday=TRUE AND day='thursday') OR
                   (calendar.friday=TRUE AND day='friday') OR
                   (calendar.saturday=TRUE AND day='saturday') OR
                   (calendar.sunday=TRUE AND day='sunday'))
       AND (current_timestamp AT TIME ZONE agency.agency_timezone)::TIME < arrival_time


GROUP BY route.pid