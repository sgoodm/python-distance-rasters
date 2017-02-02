



from main import build_distance_array
from utils import rasterize

# shp_path = "data/line_test/line_test.shp"
# out_name = "line_test"

# shp_path = "data/line_test/big_line.shp"
# out_name = "big_line"

shp_path = "data/ca_riv_15s/ca_riv_15s.shp"
out_name = "ca_riv_15s"

shp_path = "/home/userz/Desktop/river_shps/world_riv_15s/world_riv_15s.shp"
out_name = "world_riv_15s"

shp_path = "/home/userz/Desktop/shorelines/GSHHS_f_L1_lines.shp"
out_name = "shorelines"

# -----------------------------------------------------------------------------


rasterized_feature_output_path = "data/{0}_raster.tif".format(out_name)

pixel_size = 0.01


rv_array, affine = rasterize(path=shp_path, pixel_size=pixel_size,
                           output=rasterized_feature_output_path)

# print rv_array
print rv_array.shape
print affine


output_raster_path = "data/{0}_distance_raster.tif".format(out_name)


# -----------------------------------------------------------------------------


build_distance_array(rv_array, affine=affine, output=output_raster_path)


