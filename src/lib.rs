mod distance;
mod haversine;

use numpy::{PyArray2, PyReadonlyArray2};
use pyo3::prelude::*;

/// Calculate distances from every pixel to the nearest feature pixel.
///
/// Args:
///     indices: numpy array of shape (N, 2) with (row, col) pairs where condition is true
///     nrows: number of rows in the raster
///     ncols: number of columns in the raster
///     affine_params: optional tuple of (pixel_size, xmin, ymax) for geographic distance
///
/// Returns:
///     numpy array of shape (nrows, ncols) with distances
#[pyfunction]
fn calculate_distances<'py>(
    py: Python<'py>,
    indices: PyReadonlyArray2<'py, f64>,
    nrows: usize,
    ncols: usize,
    affine_params: Option<(f64, f64, f64)>,
) -> Bound<'py, PyArray2<f64>> {
    let indices_array = indices.as_array();

    // Convert numpy array to Vec of [f64; 2]
    let points: Vec<[f64; 2]> = indices_array
        .rows()
        .into_iter()
        .map(|row| [row[0], row[1]])
        .collect();

    let result = py.detach(|| distance::calculate_distances(&points, nrows, ncols, affine_params));

    PyArray2::from_vec2(
        py,
        &result
            .chunks(ncols)
            .map(|c: &[f64]| c.to_vec())
            .collect::<Vec<_>>(),
    )
    .expect("Failed to create output array")
}

#[pymodule]
fn _distancerasters(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(calculate_distances, m)?)?;
    Ok(())
}
