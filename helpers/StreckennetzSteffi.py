import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pandas as pd
import networkx as nx
import functools
import geopy.distance
from helpers.StationPhillip import StationPhillip
from database.cached_table_fetch import cached_table_fetch
import logging

logger = logging.getLogger("webserver." + __name__)

class StreckennetzSteffi(StationPhillip):
    def __init__(self, **kwargs):
        super().__init__()

        streckennetz_df = cached_table_fetch('minimal_streckennetz', **kwargs)

        self.streckennetz = nx.from_pandas_edgelist(streckennetz_df, source='u', target='v', edge_attr=True)

        logger.info("Done")

    def route_length(self, waypoints) -> float:
        """
        Calculate approximate length of a route, e.g. the sum of the distances between the waypoints.

        Parameters
        ----------
        waypoints: list
            List of station names that describe the route.

        Returns
        -------
        float:
            Length of route.

        """
        length = 0
        for i in range(len(waypoints) - 1):
            try:
                length += self.distance(waypoints[i], waypoints[i + 1])
            except KeyError:
                pass
        return length
    
    def eva_route_length(self, waypoints) -> float:
        """
        Calculate approximate length of a route, e.g. the sum of the distances between the waypoints.

        Parameters
        ----------
        waypoints: list
            List of station evas that describe the route.

        Returns
        -------
        float:
            Length of route.

        """
        length = 0
        for i in range(len(waypoints) - 1):
            try:
                length += self.distance(self.get_name(eva=waypoints[i]),
                                        self.get_name(eva=waypoints[i + 1]))
            except KeyError:
                pass
        return length

    @functools.lru_cache(maxsize=8000)
    def distance(self, u: str, v: str) -> float:
        """
        Calculate approx distance between two stations. Uses the Streckennetz if u and v are part of it,
        otherwise it usese geopy.distance.distance.

        Parameters
        ----------
        u: str
            Station name
        v: str
            Station name

        Returns
        -------
        float:
            Distance in meters between u and v.
        """
        if u in self.streckennetz and v in self.streckennetz:
            try:
                return nx.shortest_path_length(self.streckennetz, u, v, weight='length')
            except nx.exception.NetworkXNoPath:
                try:
                    u_coords = self.get_location(name=u)
                    v_coords = self.get_location(name=v)
                    return geopy.distance.distance(u_coords, v_coords).meters
                except KeyError:
                    return 0
        else:
            try:
                u_coords = self.get_location(name=u)
                v_coords = self.get_location(name=v)
                return geopy.distance.distance(u_coords, v_coords).meters
            except KeyError:
                return 0


if __name__ == "__main__":
    import helpers.fancy_print_tcp
    streckennetz_steffi = StreckennetzSteffi()
    print(streckennetz_steffi.route_length(['Tübingen Hbf', 'Stuttgart Hbf', 'Paris Est']))
