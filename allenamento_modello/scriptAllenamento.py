# import findspark
# findspark.init()
# findspark.find()

import shutil
import pyspark.sql.functions as funcs

from pyspark.ml.feature import VectorAssembler
from pyspark.ml.feature import StandardScaler
from pyspark.ml.regression import LinearRegression
from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.ml import Pipeline

from pyspark import SparkFiles
from pyspark.sql import SparkSession

import json


APP_NAME = 'training_price_prediction_model'
APP_DATASET_PATH = './data/dataset_Log2.csv'
APP_DATASET_FILE = 'dataset_Log2.csv'

nazioni= ['ES', 'PT', 'FR', 'IT-NO', 'IT-CNO', 'IT-CSO', 'IT-SO', 'IT-SAR', 'IT-SIC', 'CH','AT', 'SI', 
'HR', 'ME','GR', 'BE', 'NL', 'DE', 'GB', 'IE', 'IS', 'DK-DK1', 'NO-NO4', 'SE', 'FI', 'RU-1', 'PL', 
'EE','LV', 'LT', 'CZ', 'SK', 'HU', 'RS', 'BG', 'RO', 'TR', 'GE']

feature_rilevanti = [
    "totalProduction",
    "maxProduction",
    #"price",
    'production_biomass',    
    'production_coal', 
    'production_gas',   
    'production_geothermal',      
    'production_hydro',
    "production_nuclear",  
    'production_oil',    
    'production_solar',
    "production_unknown",
    "production_wind"
]


spark = SparkSession.builder.appName(APP_NAME).config("spark.files.overwrite", "true").getOrCreate()
sparkContext=spark.sparkContext

dati=[]
for naz in nazioni:
    for i in range(1,10):
        for d in range(0,24):        
            stringe='data/2022-07-0'+str(i)+'/2022-07-0'+str(i)+'-'+naz+'.json'
            f = open(stringe)
            data = json.load(f)
            f.close()
            
            #dati.append(data["data"][d])
            if(data["data"][d]["stateDatetime"]=="NULL"):
                print(stringe)
            dati.insert(len(dati), {
                    "stateDatetime":data["data"][d]["stateDatetime"],
                    "countryCode":data["data"][d]["countryCode"],
                    "totalProduction":data["data"][d]["totalProduction"],
                    "maxProduction":data["data"][d]["maxProduction"],
                    "price":data["data"][d]["price"]["value"],
                    
                    "production_biomass":data["data"][d]["production"]["biomass"],
                    "production_coal":data["data"][d]["production"]["coal"],
                    "production_gas":data["data"][d]["production"]["gas"],
                    "production_geothermal":data["data"][d]["production"]["geothermal"],
                    "production_hydro":data["data"][d]["production"]["hydro"],
                    "production_nuclear":data["data"][d]["production"]["nuclear"],
                    "production_oil":data["data"][d]["production"]["oil"],
                    "production_solar":data["data"][d]["production"]["solar"],
                    "production_unknown":data["data"][d]["production"]["unknown"],
                    "production_wind":data["data"][d]["production"]["wind"]
                }
                )



for i in range(len(dati)-1):
    if(dati[i+1]["countryCode"]!=dati[i]["countryCode"]):
        continue

    dati[i]["price_giorno_dopo"]=dati[i+1]["price"]
    dati[i]["nucleare_giorno_dopo"]=dati[i+1]["production_nuclear"]

for x in dati:
    if("nucleare_giorno_dopo" not in x):
        dati.remove(x)



dataset = spark.createDataFrame(dati)

dataset=dataset.na.fill(0)
prova=dataset.collect()

asb = VectorAssembler(inputCols=feature_rilevanti, outputCol='features')
scl = StandardScaler(inputCol='features', outputCol='scaled_features', withMean=True, withStd=True)
lr = LinearRegression(labelCol='price_giorno_dopo', featuresCol='scaled_features', maxIter=100, regParam=.1)
pipeline = Pipeline(stages=[asb, scl, lr])

(training_data, test_data) = dataset.randomSplit([ 0.8, 0.2 ])


pipeline_model = pipeline.fit(training_data)
predictions = pipeline_model.transform(test_data)



pipeline_model.write().overwrite().save("model")