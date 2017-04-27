SELECT route_id,
       MIN(arrival_time)
FROM   stop_time JOIN
(agency JOIN
    (SELECT route_id, route.agency_id as agency_id, trip_id FROM (
        route  JOIN
            (
                   SELECT route_id, trip.agency_id as agency_id, trip.id as trip_id
                   FROM   trip
                   JOIN   (select * FROM calendar, to_char(current_date, 'fmday') as day) calenday --fm removes trailing spaces (format)
                   ON calenday.id = trip.service_id AND calenday.agency_id = trip.agency_id
                   WHERE  (monday=TRUE AND day='monday') OR
                   (tuesday=TRUE AND day='tuesday') OR
                   (wednesday=TRUE AND day='wednesday') OR
                   (thursday=TRUE AND day='thursday') OR
                   (friday=TRUE AND day='friday') OR
                   (saturday=TRUE AND day='saturday') OR
                   (sunday=TRUE AND day='sunday')
            ) triponday
            ON route.id = triponday.route_id AND route.agency_id = triponday.agency_id
        )
    ) C2
    ON agency.id = agency_id
) c3
ON c3.trip_id = stop_time.trip_id
WHERE  stop_id = ( %s )
AND (current_timestamp AT TIME ZONE c3.timezone)::TIME < arrival_time
AND  arrival_time IS NOT NULL
GROUP BY route_id