import datetime
import pandas as pd
import numpy as np
import os
import random
import xml.etree.ElementTree as ET
import sqlalchemy
import collections
from config import db_database, db_password, db_server, db_username

class NoLocationError(Exception):
    pass

class BetriebsstellenBill:
    def __init__(self):
        self.engine = sqlalchemy.create_engine('postgresql://'+ db_username +':' + db_password + '@' + db_server + '/' + db_database + '?sslmode=require')
        self.betriebsstellen = pd.read_sql('SELECT * FROM betriebstellen', con=self.engine)
        self.engine.dispose()

        self.name_index_betriebsstellen = self.betriebsstellen.set_index('name')
        self.ds100_index_betriebsstellen = self.betriebsstellen.set_index('ds100')
        self.NoLocationError = NoLocationError

    def __len__(self):
        return len(self.betriebsstellen)

    def get_name(self, ds100):
        return self.ds100_index_betriebsstellen.at[ds100, 'name']
    
    def get_ds100(self, name):
        return self.name_index_betriebsstellen.at[name, 'ds100']

    def get_location(self, name=None, ds100=None):
        if name:
            return self.get_location(ds100=self.get_ds100(name=name))
        else:
            lon = self.ds100_index_betriebsstellen.at[ds100, 'lon']
            lat = self.ds100_index_betriebsstellen.at[ds100, 'lat']
            # print(type(lon), type(lat))
            if type(lon) == np.ndarray:
                lon = lon[0]
            if type(lat) == np.ndarray:
                lat = lat[0]
            # print(lon, lat)
            if not lon or not lat:
                raise self.NoLocationError
            else:
                return (lon,lat)

class StationPhillip:
    def __init__(self):
        self.engine = sqlalchemy.create_engine('postgresql://'+ db_username +':' + db_password + '@' + db_server + '/' + db_database + '?sslmode=require')
        self.station_df = pd.read_sql('SELECT * FROM stations', con=self.engine)
        # self.betriebsstellen = pd.read_sql('SELECT * FROM betriebstellen', con=self.engine)
        self.engine.dispose()

        self.station_df['eva'] = self.station_df['eva'].astype(int)
        self.name_index_stations = self.station_df.set_index('name')
        self.eva_index_stations = self.station_df.set_index('eva')
        self.ds100_index_stations = self.station_df.set_index('ds100')
        self.sta_list = self.station_df['name'].tolist()

    def __len__(self):
        return len(self.station_df)

    def __iter__(self):
        self.n = 0
        return self
    
    def __next__(self):
        if self.n < self.__len__():
            self.n += 1
            return self.sta_list[self.n -1]
        else:
            raise StopIteration

    def get_eva(self, name=None, ds100=None):
        if name:
            return self.name_index_stations.at[name, 'eva']
        elif ds100:
            return self.ds100_index_stations.at[ds100, 'eva']
        else:
            return None

    def get_name(self, eva=None, ds100=None):
        if eva:
            return self.eva_index_stations.at[eva, 'name']
        elif ds100:
            return self.ds100_index_stations.at[ds100, 'name']
        else:
            return None
    
    def get_ds100(self, name=None, eva=None):
        if name:
            return self.name_index_stations.at[name, 'ds100']
        elif eva:
            return self.eva_index_stations.at[eva, 'ds100']
        else:
            return None

    def get_location(self, name=None, eva=None, ds100=None):
        if name or ds100:
            return self.get_location(eva=self.get_eva(name=name, ds100=ds100))
        else:
            return (self.eva_index_stations.at[eva, 'lon'],
                    self.eva_index_stations.at[eva, 'lat'])

    def random_iter(self):
        random_sta_list = self.station_df['name'].tolist()
        # randomize list order in order to be harder to track when doing requests
        # random.shuffle(random_sta_list)
        for sta in random_sta_list:
            yield sta


class FileLisa:
    def __init__(self):
        self.BASEPATH = 'rtd/'

    def clean_station_name(self, station):
        return station.strip().replace('/', 'slash')

    def concat_xmls(self, xml1, xml2):
        # iter the elements to concat
        for xml_child in xml2:
            # append elements to xml
            xml1.append(xml_child)
        return xml1

    def save_xml(self, xml, directory, file_name):
        # try:
        # check if there is an xml to save
        if xml != 'None' or xml != None or not xml:
            #create dir if not present
            if not os.path.exists(directory):
                os.makedirs(directory)
            # save xml to file
            with open(directory + file_name, 'w') as fd:
                print(xml, file=fd)
        # except Exception as ex:
        #     print(directory, file_name)
        #     print(ex)

    def open_xml(self, dir_name):
        # try to open and parse the file
        try:
            tree = ET.parse(dir_name)
            xroot = tree.getroot()
            if xroot != 'None' or xroot != None or not xroot:
                return xroot
            else:
                return None
        except FileNotFoundError:
            # print('file_not_found')
            return None
        except ET.ParseError: #if the file is emty or corrupt
            # print('parse_error')
            return None

    def save_plan_xml(self, xml, station, date):
        directory = self.BASEPATH + self.clean_station_name(station) + '/'
        file_name = str(date) + '_' + 'plan.xml'
        if xml != 'None' or xml != None or not xml:
            old_xml = self.open_xml(directory + file_name)
            if old_xml == None:
                self.save_xml(xml, directory, file_name)
            else:
                try:
                    tree = ET.ElementTree()
                    root = ET.fromstring(xml)
                    old_xml = self.concat_xmls(old_xml, root)
                    tree._setroot(old_xml)
                    tree.write(directory + file_name)
                except ET.ParseError: # if the xml looks like <timetable\> or sth like that
                    pass
                except TypeError: # one object has NoneType
                    pass
                # except Exception as e:
                #     print(e)

    def save_real_xml(self, xml, station, date):
        directory = self.BASEPATH + self.clean_station_name(station) + '/'
        file_name = str(date) + '_' + 'changes.xml'
        if xml != 'None' or xml != None or not xml:
            old_xml = self.open_xml(directory + file_name)
            if old_xml == None:
                self.save_xml(xml, directory, file_name)
            else:
                try:
                    tree = ET.ElementTree()
                    root = ET.fromstring(xml)
                    old_xml = self.concat_xmls(old_xml, root)
                    tree._setroot(old_xml)
                    tree.write(directory + file_name)
                except ET.ParseError: # if the xml looks like <timetable\> or sth like that
                    pass
                except TypeError: # one object has NoneType
                    pass
                # except Exception as e:
                #     print(e)

    def open_plan_xml(self, station, date):
        directory = self.BASEPATH + self.clean_station_name(station) + '/'
        file_name = str(date) + '_' + 'plan.xml'
        xml = self.open_xml(directory + file_name)
        return xml

    def open_real_xml(self, station, date):
        directory = self.BASEPATH + self.clean_station_name(station) + '/'
        file_name = str(date) + '_' + 'changes.xml'
        xml = self.open_xml(directory + file_name)
        return xml

    def delete_plan(self, station, date):
        directory = self.BASEPATH + self.clean_station_name(station) + '/'
        file_name = str(date) + '_' + 'plan.xml'
        self.delete(directory + file_name)

    def delete_real(self, station, date):
        directory = self.BASEPATH + self.clean_station_name(station) + '/'
        file_name = str(date) + '_' + 'real.xml'
        self.delete(directory + file_name)

    def delete(self, path):
        if os.path.isfile(path):
            os.remove(path)

if __name__ == '__main__':
    stations = StationPhillip()
    print('lol')