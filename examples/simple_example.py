
import fiona
import distancerasters as dr


# path to example vector data
shp_path = "linestrings.geojson"

# name used for output rasters
out_name = "linestrings"

# resolution at which vector data will be rasterized
pixel_size = 0.01

# geotiff path for rasterized vector data
rasterized_features_path = f"{out_name}_binary.tif"

# load vector data
shp = fiona.open(shp_path, "r")

# rasterized vector data
rv_array, affine = dr.rasterize(shp, pixel_size=pixel_size, bounds=shp.bounds, output=rasterized_features_path)

# option to manually export rasterized vector data
# dr.export_raster(rv_array, affine, rasterized_features_path)

# examine rasterization results
print (rv_array)
print (rv_array.shape)
print (affine)


# geotiff path for distance raster
distance_raster_path = "f{out_name}_distance.tif"

# function to define which cells from rasterized input to calculate distance to
#   this would be modified if using a non-binary rasterization, for example
def raster_conditional(rarray):
    return (rarray == 1)

# generate distance array
dr.build_distance_array(rv_array, affine=affine,
                     output=distance_raster_path,
                     conditional=raster_conditional)


