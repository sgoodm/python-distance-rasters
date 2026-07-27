use kiddo::immutable::float::kdtree::ImmutableKdTree;
use kiddo::SquaredEuclidean;
use rayon::prelude::*;

use crate::haversine;

/// Calculate distances from every pixel in an (nrows x ncols) grid to the
/// nearest point in `indices`.
///
/// `indices` is a slice of (row, col) pairs (as f64) where the conditional is true.
/// `affine_params`, if provided, is (pixel_size, xmin, ymax) and triggers
/// geographic distance conversion (haversine, output in meters).
/// Without affine_params, raw Euclidean pixel distance is returned.
///
/// Returns a flat Vec<f64> of length nrows * ncols (row-major).
pub fn calculate_distances(
    indices: &[[f64; 2]],
    nrows: usize,
    ncols: usize,
    affine_params: Option<(f64, f64, f64)>,
) -> Vec<f64> {
    if indices.is_empty() {
        return vec![f64::INFINITY; nrows * ncols];
    }

    // Build a 2-D k-d tree from the input points for fast nearest-neighbor lookups.
    // Uses the immutable/bulk-load variant: it's built once from the full point
    // set and only queried afterward (never modified), and unlike the mutable
    // KdTree's one-at-a-time `add()`, its construction doesn't panic when many
    // points share the same coordinate on one axis (e.g. a raster row/column
    // that's mostly or entirely "true" — common for dense binary masks like
    // road networks) — see kiddo's fixed bucket-size limit on incremental
    // insertion (default 32) vs. this variant's count-based median partitioning.
    let tree: ImmutableKdTree<f64, u64, 2, 32> = ImmutableKdTree::new_from_slice(indices);

    // Iterate over every pixel in parallel (one thread per row via rayon).
    // For each pixel, find the closest input point and compute the distance.
    let tree_ref = &tree;
    let result: Vec<f64> = (0..nrows)
        .into_par_iter()
        .flat_map_iter(|r| {
            (0..ncols).map(move |c| {
                // Look up the nearest input point to this pixel in the k-d tree
                let query = [r as f64, c as f64];
                let nearest = tree_ref.nearest_one::<SquaredEuclidean>(&query);
                let nearest_idx = nearest.item as usize;
                let nearest_point = indices[nearest_idx];
                let min_dist = nearest.distance.sqrt();

                // If affine params are provided, convert pixel distance to
                // geographic distance (meters) using the haversine formula.
                // Otherwise, return raw Euclidean distance in pixel units.
                match affine_params {
                    Some((pixel_size, xmin, ymax)) => {
                        let km_dist = if (c as f64) == nearest_point[1] {
                            min_dist * pixel_size * 111.321
                        } else {
                            let p1 = haversine::index_to_coords(
                                r as f64, c as f64, pixel_size, xmin, ymax,
                            );
                            let p2 = haversine::index_to_coords(
                                nearest_point[0],
                                nearest_point[1],
                                pixel_size,
                                xmin,
                                ymax,
                            );
                            haversine::haversine(p1, p2)
                        };
                        km_dist * 1000.0 // convert km → meters
                    }
                    None => min_dist,
                }
            })
        })
        .collect();
    result
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn many_points_same_row_does_not_panic() {
        // 500 points all sharing row=10.0, spread across many columns.
        // This exceeds kiddo's default incremental-insertion bucket size
        // (32) on one axis; the mutable KdTree used to panic here.
        let indices: Vec<[f64; 2]> = (0..500).map(|c| [10.0, c as f64]).collect();
        let result = calculate_distances(&indices, 50, 500, None);
        assert_eq!(result.len(), 50 * 500);
        assert_eq!(result[10 * 500], 0.0);
    }

    #[test]
    fn many_points_same_column_does_not_panic() {
        // same scenario, transposed: many points sharing col=10.0
        let indices: Vec<[f64; 2]> = (0..500).map(|r| [r as f64, 10.0]).collect();
        let result = calculate_distances(&indices, 500, 50, None);
        assert_eq!(result.len(), 500 * 50);
        assert_eq!(result[10 * 50 + 10], 0.0);
    }
}
