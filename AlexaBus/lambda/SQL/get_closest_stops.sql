SELECT   stop_name,
         st_distance_sphere(geom, st_makepoint(%(lon)s, %(lat)s)),
         pid,
         gtfsfeed_id
FROM     stop
WHERE    st_distance_sphere(geom, st_makepoint(%(lon)s, %(lat)s)) < 500
ORDER BY st_distance_sphere(geom, st_makepoint(%(lon)s, %(lat)s)) limit %(num)s