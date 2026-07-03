# Geography and Location Falsehoods

## Core Rules

- Carry coordinate reference systems, units, precision, and source metadata with geospatial values.
- Treat place names, borders, weather, and map projections as contextual, political, historical, and time-varying.
- Use geospatial libraries and authoritative datasets for projection, distance, containment, and reverse-geocoding work.
- Model uncertainty explicitly: location data can be approximate, stale, disputed, or valid only at a specific scale.
- Do not discard datum, projection, axis order, altitude reference, timestamp, or precision when storing coordinates.
- Choose algorithms based on scale. Short-distance calculations, global routing, map display, geofencing, and legal boundary checks need different assumptions.
- Keep human place labels separate from coordinates. A name is a search/display artifact, not a stable geometry.
- Document whether a location means centroid, entrance, parcel, postal route, administrative area, sensor position, or user-reported point.

## Falsehoods To Avoid

- A place does not have one stable name, spelling, boundary, parent region, language, or coordinate.
- Latitude and longitude alone do not define enough context; datum, projection, axis order, altitude, and precision matter.
- Maps are not neutral truth: projections distort area, shape, distance, and direction, and datasets choose simplifications.
- Weather is not one value per city; it varies with exact location, elevation, time, sensor, forecast model, and microclimate.
- The shortest route, nearest object, and containing region can change depending on whether calculations are planar, spherical, ellipsoidal, network-based, or jurisdictional.
- Administrative hierarchies are not uniform. Countries can have states, provinces, counties, prefectures, territories, autonomous regions, disputed areas, exclaves, and overseas dependencies.
- Geocoding is not deterministic truth. Providers disagree, return different precision levels, and change results when data improves.
- A boundary can be fuzzy, contested, seasonal, historical, private, or intentionally generalized for privacy or licensing.

## Edge Cases

- Coordinate systems can swap axis order, use incompatible datums, or silently mix projected and geographic coordinates.
- Political boundaries, country names, and administrative regions can change or be disputed while systems keep stale assumptions.
- Weather APIs can report different conditions for the same named place because their stations and models differ.
- GPS coordinates can be spoofed, rounded, snapped to roads, cached from a prior session, or unavailable indoors.
- Antimeridian crossings, polar regions, and bounding boxes that wrap around longitude `180` break simple min/max checks.
- Elevation can be relative to sea level, an ellipsoid, a local datum, floor number, pressure altitude, or terrain model.
- Map tiles, vector data, and search indexes may update on different schedules, so a visible map and an API result can disagree.


## Recommended Libraries

- Projections and datums: PROJ (and bindings such as `pyproj`) with explicit EPSG codes carried alongside the data.
- Geometry and containment: GEOS/JTS-based libraries (Shapely, JSTS, NetTopologySuite), Turf.js, or PostGIS for storage and queries.
- Geodesics: GeographicLib for accurate ellipsoidal distance and bearing when haversine approximations are not enough.
- Spatial indexing and tiling: S2 or H3 cells and R-tree indexes, with antimeridian and polar cases handled explicitly.
- Data: versioned authoritative boundary datasets (national agencies, OSM extracts, Natural Earth), because boundaries and names change.

## Sources

Citation keys resolve in [source-index.md](source-index.md).

- Geography and place names: [G1]
- Maps and projections: [G2]
- Weather: [G3]
- Coordinate systems and datums: [G4]
