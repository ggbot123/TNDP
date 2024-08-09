# -*- coding:<UTF-8> -*-

# v0.01 by chalco
# Created 202407181529

import pathlib
import warnings
from shapely.geometry import Polygon
from scipy.spatial import Voronoi
import geopandas as gpd
import pandas as pd

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)
warnings.filterwarnings("ignore")


def lloyd_relaxation(polygons, boundary_polygon, iterations=1):
    for _ in range(iterations):
        new_points = []
        for polygon in polygons:
            centroid = polygon.centroid
            new_points.append((centroid.x, centroid.y))
        vor = Voronoi(new_points)
        new_polygons = []
        for region in vor.regions:
            if not -1 in region and len(region) > 0:
                new_polygon = Polygon([vor.vertices[i] for i in region])
                if new_polygon.is_valid:
                    new_polygon = new_polygon.intersection(boundary_polygon)
                    new_polygons.append(new_polygon)
        polygons = new_polygons
    return polygons


if __name__ == '__main__':
    data_folder = pathlib.Path("/Users/chalcozheng/PycharmProjects/pythonProject/IC_Smartcard")
    file_name = 'TAZ_division_expand.geojson'
    file_to_open = data_folder / file_name

    boundary_file_name = 'boundary.geojson'
    boundary_file_to_open = data_folder/boundary_file_name

    gdf = gpd.read_file(file_to_open)
    # polygons = [feature['geometry'] for feature in gdf['geometry']]
    polygons = [geom for geom in gdf.geometry]
    original_bounds = gdf.total_bounds
    original_polygons = Polygon([
        (original_bounds[0], original_bounds[1]),
        (original_bounds[0], original_bounds[3]),
        (original_bounds[2], original_bounds[3]),
        (original_bounds[2], original_bounds[1]),
        (original_bounds[0], original_bounds[1])
    ])

    boundary_gdf = gpd.read_file(boundary_file_to_open)
    boundary_polygon = boundary_gdf.unary_union

    relaxed_polygons = lloyd_relaxation(polygons, boundary_polygon, iterations=5)
    new_gdf = gpd.GeoDataFrame(geometry=relaxed_polygons, crs=gdf.crs)
    new_gdf = new_gdf.intersection(original_polygons)

    new_gdf.to_file('relaxed_division_boundary_expand.geojson', driver='Geojson')


