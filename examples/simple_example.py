
import fiona
import distancerasters as dr


# load vector data (crs = epsg:4326)
shp = fiona.open("examples/linestrings.geojson", "r")

# resolution (in units matching projection) at which vector data will be rasterized
pixel_size = 0.01


# rasterize vector data and output to geotiff
rv_array, affine = dr.rasterize(shp, pixel_size=pixel_size, bounds=shp.bounds, output="examples/linestrings_rasterized_binary.tif")

# option to manually export rasterized vector data
# dr.export_raster(rv_array, affine, "linestrings_rasterized_binary.tif")

# function to define which cells from rasterized input to calculate distance to
#   this would be modified if using a non-binary rasterization, for example
def raster_conditional(rarray):
    return (rarray == 1)

# generate distance array and output to geotiff
dist_array = dr.DistanceRaster(rv_array, affine=affine,
                               output_path="examples/linestrings_distance_raster.tif",
                               conditional=raster_conditional)

# Output:
#
# Tree build time: 0.033019065856933594 seconds
# Building distance array...
# Total run time: 2.88 seconds