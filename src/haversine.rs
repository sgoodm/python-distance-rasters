/// Calculate haversine distance between two points.
///
/// Points are in (longitude, latitude) format.
/// Returns haversine distance between given points p1 and p2.
pub fn haversine(p1: (f64, f64), p2: (f64, f64)) -> f64 {
    let (lon1, lat1) = p1;
    let (lon2, lat2) = p2;

    // Mean radius of the Earth in km
    let radius: f64 = 6371.0;

    let delta_lat = (lat2 - lat1).to_radians();
    let delta_lon = (lon2 - lon1).to_radians();

    let a = (delta_lat / 2.0).sin().powi(2)
        + lat1.to_radians().cos() * lat2.to_radians().cos() * (delta_lon / 2.0).sin().powi(2);

    let c = 2.0 * a.sqrt().atan2((1.0 - a).sqrt());

    radius * c
}

/// Convert 2D array indices to geographic coordinates.
///
/// Takes row and column indices along with affine parameters
/// and returns (longitude, latitude) of the pixel centroid.
pub fn index_to_coords(r: f64, c: f64, pixel_size: f64, xmin: f64, ymax: f64) -> (f64, f64) {
    let lon = xmin + pixel_size * (0.5 + c);
    let lat = ymax - pixel_size * (0.5 + r);
    (lon, lat)
}
