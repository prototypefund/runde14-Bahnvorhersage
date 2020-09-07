from sklearn.ensemble import ExtraTreesClassifier
from sklearn.metrics import multilabel_confusion_matrix
import numpy as np
import pandas as pd
from joblib import dump, load
import sys
import os
#import logging

basepath = os.path.dirname(os.path.realpath(__file__))

def train_and_test(X, y, X_test, y_test, name):
    clf = ExtraTreesClassifier(n_estimators=70, max_depth=12,
                                 random_state=0, n_jobs = None, criterion = 'entropy')
    clf.fit(X, y)
    
    #save the trained model
    dump(clf, basepath + '/ml_models/' + name + '_extra.joblib')

    #make and print some acc statistics
    test_pred = clf.predict(X_test)
    acc = test_pred[test_pred == y_test]
    print('Feature importances', clf.feature_importances_)
    print('acc_' + name + ':', len(acc)/ len(test_pred))

    #print confusion matrix
    c_m = multilabel_confusion_matrix(y_test, test_pred).ravel()
    dadx = [' ad0', ' ad5', 'ad10', 'ad15', ' dd0', ' dd5', 'dd10', 'dd15']
    print('\ttn, \tfp, \tfn, \ttp, \tacc1, \t\t\tacc2')
    for i in range(8):
        print(dadx[i], c_m[4*i+0], c_m[4*i+1], c_m[4*i+2], c_m[4*i+3], c_m[4*i+3]/(c_m[4*i+3]+c_m[4*i+1]), c_m[4*i+0]/(c_m[4*i+0]+c_m[4*i+2]), sep='\t')


def np_sets(dataset):
    # make the balance of delayed trains in the dataset better
    set1 = dataset[dataset['adelay10'] == True]
    buffer1 = dataset[dataset['adelay10'] == False]
    buffer1 = buffer1.sample(n=len(set1))
    set1 = pd.concat([set1, buffer1], ignore_index=True, sort=False)
    set1 = set1.sample(n=len(set1)).reset_index(drop=True)
    dataset = set1
    del set1

    #only train on these features
    dataset = dataset[['adelay0', 'adelay5', 'adelay10', 'adelay15', 'ddelay0', 'ddelay5', 'ddelay10', 'ddelay15',
                    'month',
                    'dayofweek',
                    'hour',
                    'track_length_since_start',
                    'time_since_first_station',
                    'station_number',
                    'lat',
                    'lon',
                    'track_length',
                    'stay_time',
                    'time_since_last_station',
                    'start_lat',
                    'start_lon',
                    'destination_lat',
                    'destination_lon',
                    'total_lenth',
                    'total_time',
                    'delta_lon',
                    'delta_lat']]
                    # 'relative_humidity', 'dew_point_c', 'air_pressure_hpa', 'temperature_c', 'trainno', 'weather_condition', 'type', 'bhf', 'wind_speed_kmh',

    #classes
    columns = ['adelay0', 'adelay5', 'adelay10', 'adelay15', 'ddelay0', 'ddelay5', 'ddelay10', 'ddelay15']

    #split into train and test set / labels
    train_set1 = dataset.sample(frac=0.8,random_state=0)
    test_set1 = dataset.drop(train_set1.index)

    train_labels = train_set1[columns].copy()
    train_set1.drop(columns, axis=1, inplace=True)

    test_labels = test_set1[columns].copy()
    test_set1.drop(columns, axis=1, inplace=True)

    train_set1 = train_set1.to_numpy()
    train_labels = train_labels.to_numpy()

    test_set1 = test_set1.to_numpy()
    test_labels = test_labels.to_numpy()

    return train_set1, train_labels, test_set1, test_labels

def handle_non_numerical_data(df):
    columns = df.columns.values

    for column in columns:
        text_digit_vals = {}
        def convert_to_int(val):
            return text_digit_vals[val]

        if df[column].dtype != np.int64 and df[column].dtype != np.float64:
            unique_elements = df[column].unique()
            x = 0
            for unique in unique_elements:
                if unique not in text_digit_vals:
                    text_digit_vals[unique] = x
                    x+=1

            df.loc[:,column] = df[column].apply(convert_to_int)
    return df

def train():
    print('creating models...', end=' ')

    path =  'data/combinedData/na_droped_trains2.csv'
    
    dataset = pd.read_csv(path, index_col=False, compression='zip') #C:/Users/McToel/Desktop/regression.csv combinedData/na_droped_trains.csv C:/Users/Serverkonto/Desktop/regression.csv
    dataset = dataset.sample(frac=1.0,random_state=0)

    date = dataset['date'].astype('datetime64[D]')
    dataset['month'] = date.dt.month
    dataset['dayofweek'] = date.dt.dayofweek
    dataset['hour'] = dataset['zeit']
    del date
    dataset = dataset[['adelay',
                    'ddelay',
                    'month',
                    'dayofweek',
                    'hour',
                    'track_length_since_start',
                    'time_since_first_station',
                    'station_number',
                    'lat',
                    'lon',
                    'track_length',
                    'stay_time',
                    'time_since_last_station',
                    'start_lat',
                    'start_lon',
                    'destination_lat',
                    'destination_lon',
                    'total_lenth',
                    'total_time',
                    'delta_lon',
                    'delta_lat']]

    #dataset[['bhf', 'weather_condition', 'trainno', 'type']] = handle_non_numerical_data(dataset[['bhf', 'weather_condition', 'trainno', 'type']])

    # one_hot = pd.get_dummies(dataset['type'])
    # dataset = dataset.drop('type',axis = 1)
    # dataset = dataset.join(one_hot)

    dataset['adelay0'] = dataset['adelay'] <= 5
    dataset['adelay5'] = (dataset['adelay'] > 5) #& (dataset['adelay'] <= 10)
    dataset['adelay10'] = (dataset['adelay'] > 10) #& (dataset['adelay'] <= 15)
    dataset['adelay15'] = dataset['adelay'] > 15

    dataset['ddelay0'] = dataset['ddelay'] <= 5
    dataset['ddelay5'] = (dataset['ddelay'] > 5) #& (dataset['ddelay'] <= 10)
    dataset['ddelay10'] = (dataset['ddelay'] > 10) #& (dataset['ddelay'] <= 15)
    dataset['ddelay15'] = dataset['ddelay'] > 15

    d_set, d_lab, test_set, test_lab = np_sets(dataset)
    del dataset
    train_and_test(d_set, d_lab, test_set, test_lab, 'multiclass')




class predictor:
    def __init__(self):
        try:
            self.multiclass_rf = load(basepath + '/ml_models/multiclass_extra.joblib')
        except FileNotFoundError:
            if input("Models not present! Create Models? y/[n]") == "y":
                train()
                self.__init__()
            else:
                sys.exit('Please create Models')

    def predict(self, features_df):
        #this is to make sure that we olny pass the right features in the right order into the predictor.
        features_df = features_df[[ 'month',
                                    'dayofweek',
                                    'hour',
                                    'track_length_since_start',
                                    'time_since_first_station',
                                    'station_number',
                                    'lat',
                                    'lon',
                                    'track_length',
                                    'stay_time',
                                    'time_since_last_station',
                                    'start_lat',
                                    'start_lon',
                                    'destination_lat',
                                    'destination_lon',
                                    'total_lenth',
                                    'total_time',
                                    'delta_lon',
                                    'delta_lat']]
        
        #convert df to 2d numpy array
        features = features_df.to_numpy()
        features = features.reshape(1, -1)
        del features_df

        #make a probability prediction for one train
        delays = np.array(self.multiclass_rf.predict_proba(features))[:, 0,1] # , check_input=False

        #return delay probabilitys in a dict
        return {'adelay0': delays[0],
                'adelay5': delays[1],
                'adelay10': delays[2],
                'adelay15': delays[3],
                'ddelay0': delays[4],
                'ddelay5': delays[5],
                'ddelay10': delays[6],
                'ddelay15': delays[7] }

    def predict_con(self, features1, features2, transfertime):
        if (features1 == False):
            # if we have no data in our database to predict the delay of the train,
            # we set the yearly average delay for regio trains as delay probability.
            # Values from https://www.deutschebahn.com/de/konzern/konzernprofil/zahlen_fakten/puenktlichkeitswerte-1187696
            pred1 = {'adelay0': 0.95, 'adelay5': 1 - 0.95, 'adelay10': 1 - 0.97, 'adelay15': 1 - 0.99}
        else:
            features1 = pd.DataFrame(features1,index=[0])
            pred1 = self.predict(features1)

        if (features2 == False):
            # if we have no data in our database to predict the delay of the train,
            # we set the yearly average delay for regio trains as delay probability.
            # Values from https://www.deutschebahn.com/de/konzern/konzernprofil/zahlen_fakten/puenktlichkeitswerte-1187696
            pred2 = {'ddelay0': 0.95, 'ddelay5': 1 - 0.95, 'ddelay10': 1 - 0.97, 'ddelay15': 1 - 0.99}
        else:
            features2 = pd.DataFrame(features2,index=[0])
            pred2 = self.predict(features2)

        con_score = 0
        if (transfertime > 17):
            con_score = 1 #if the transfer time is higher than our highest lable, we can only predict the connection as working

        elif (transfertime > 12):
            p1 = pred1['adelay15'] * (1 - pred2['ddelay5'])
            con_score = 1 - (p1)

        elif (transfertime > 7):
            #if the arrival train has 10 min delay, and the departure one does not have 5 min delay
            p1 = (pred1['adelay10'] - pred1['adelay15']) * (1 - pred2['ddelay5'])

            #if the arrival train has 15 min delay, and the departure one does not have 10 min delay
            p2 = pred1['adelay15'] * (1 - pred2['ddelay10'])
            con_score = 1 - (p1+p2)

        else:
            p1 = (pred1['adelay5'] - pred1['adelay10']) * (1 - pred2['ddelay5'])
            p2 = (pred1['adelay10'] - pred1['adelay15']) * (1 - pred2['ddelay10'])
            p3 = pred1['adelay15'] * (1 - pred2['ddelay15'])
            con_score = 1 - (p1+p2+p3)
        
        return con_score, pred1['adelay5'], pred2['ddelay5']


#train()