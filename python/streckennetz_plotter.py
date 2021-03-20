import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import osmnx as ox
import networkx as nx
import shapely
import datetime
from shapely.geometry import Point, LineString, Polygon
import numpy as np
import geopy.distance
import itertools
import pandas as pd
import geopandas as gpd
from helpers.StationPhillip import StationPhillip
import matplotlib.pyplot as plt
import pickle
from concurrent.futures import ProcessPoolExecutor
from database.engine import engine
import matplotlib.pyplot as plt
import pytz
from helpers.BetriebsstellenBill import BetriebsstellenBill
from database.cached_table_fetch import cached_table_fetch

def wkb_reverse_hexer(wbk_hex):
    return shapely.wkb.loads(wbk_hex, hex=True)

plt.style.use('dark_background')

stations = StationPhillip()
station_gdf = stations.get_geopandas()

betriebsstellen = BetriebsstellenBill()
betriebsstellen_gdf = betriebsstellen.get_geopandas()

obstacles = pd.read_csv('cache/obstacles2.csv')
obstacles['from_time'] = pd.to_datetime(obstacles['from_time'])
obstacles['to_time'] = pd.to_datetime(obstacles['to_time'])

start = datetime.datetime(2021, 2, 20)
end = datetime.datetime(2021, 3, 29)
obstacles = obstacles.loc[(obstacles['from_time'] > start.replace(tzinfo=pytz.timezone("Europe/Berlin"))) & (obstacles['to_time'] < end.replace(tzinfo=pytz.timezone("Europe/Berlin")))]

streckennetz = cached_table_fetch('full_streckennetz', prefer_cache=True).set_index(['u', 'v', 'key'])
streckennetz['geometry'] = streckennetz['geometry'].apply(wkb_reverse_hexer)

nodes = cached_table_fetch('full_streckennetz_nodes', prefer_cache=True)
nodes['geometry'] = nodes['geometry'].apply(wkb_reverse_hexer)

# streckennetz = pd.read_sql_table('full_streckennetz', con=engine).set_index(['u', 'v', 'key'])
# streckennetz_nodes = pd.read_sql_table('full_streckennetz_nodes', con=engine)

# streckennetz['geometry'] = streckennetz['geometry'].apply(wkb_reverse_hexer)
# streckennetz.to_pickle('cache/full_streckennetz.pkl')

# streckennetz_nodes['geometry'] = streckennetz_nodes['geometry'].apply(wkb_reverse_hexer)
# streckennetz_nodes.to_pickle('cache/full_streckennetz_nodes.pkl')
# print('saved cache')

# streckennetz = pd.read_pickle('cache/full_streckennetz.pkl')
streckennetz = gpd.GeoDataFrame(streckennetz, geometry='geometry')

nodes = gpd.GeoDataFrame(nodes, geometry='geometry')
station_nodes = nodes.loc[~nodes['type'].isna()]
# streckennetz_graph = ox.graph_from_gdfs(streckennetz_nodes, streckennetz)

# streckennetz = streckennetz.cx[12.943267:13.822174, 52.354634:52.643063]

# strecke = streckennetz.plot(color='black')
# station_gdf = station_gdf.loc[[ 'Niederschlag', 'Kretscham-Rothensehma'], :]
# station_gdf.plot(ax=strecke, marker='o', color='red', markersize=5)

rows = []
station_obsacles = []
for i, obstacle in obstacles.iterrows():
    if obstacle['dir'] != 3:
        rows.append((obstacle['from_edge'], obstacle['to_edge'], 0))
    else:
        station_obsacles.append(obstacle['from_edge'])

strecke = streckennetz.loc[~streckennetz.index.isin(rows)].plot(color='lightgrey', linewidth=0.2)
# station_nodes.plot(color='green', ax=strecke)
obstacle_edges = streckennetz.loc[streckennetz.index.isin(rows)]
# obstacle_edges.plot(color='red', ax=strecke)
betriebsstellen_gdf = betriebsstellen_gdf.loc[betriebsstellen_gdf.index.isin(station_obsacles)]
# betriebsstellen_gdf.plot(ax=strecke, color='red', markersize=10, zorder=2)
# for name, row in station_gdf.iterrows():
#     if name in ['Kaisersesch']:
#         strecke.annotate(text=name, xy=row['geometry'].coords[0])
# plt.show()
strecke.set_aspect('equal', 'datalim')
plt.show()


# # Test functionality
# path = ox.shortest_path(streckennetz_graph, 'Niederschlag', 'Kretscham-Rothensehma', weight='length')
# print(nx.shortest_path_length(streckennetz_graph, 'Niederschlag', 'Kretscham-Rothensehma', weight='length'))
# ox.plot_graph_route(streckennetz_graph, path)

# streckennetz.to_sql('full_streckennetz', if_exists='replace', method='multi', con=engine)