SELECT   name,
         st_distance_sphere(geom, st_makepoint(%s, %s)),
         id
FROM     stop
WHERE    st_distance_sphere(geom, st_makepoint(%s, %s)) < 500
ORDER BY st_distance_sphere(geom, st_makepoint(%s, %s)) limit %s