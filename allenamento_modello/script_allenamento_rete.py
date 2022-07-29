

#N.B. il seguente codice è un tentativo quasi riuscito di far funzionare un modello di reteneurale basata su deeplearning basato su keras
#in maniera distribuita su spark, è quesi riuscito perche dopo esser riusciti a creare un modello che si allena e da in output una 
#qualche predizione (sulla produzione di energia su funte nucleare nella successiva fascia oraria), non si è riusciti a integrarlo 
#nella pipeline definitiva perchè la libreria usate per incapsulare il modello di keras (elephas) è un progetto non definitivo
#e non supporta il salvataggio del modello.


from os import sync
import shutil
import pyspark.sql.functions as funcs

from pyspark.ml.feature import VectorAssembler
from pyspark.ml.feature import StandardScaler
from pyspark.ml.regression import LinearRegression
from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.ml import Pipeline

from pyspark import SparkFiles
from pyspark.sql import SparkSession

from keras.models import Sequential
from keras.layers import Dense

from keras import optimizers, regularizers

from elephas.ml_model import ElephasEstimator
import tensorflow  as tf
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
    "price",
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

feature_rilevanti2 = [
    "totalProduction",
    "maxProduction",
    "price",
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

print("set creato")

dataset = spark.createDataFrame(dati)
print(dataset.count())
dataset=dataset.na.fill(0)
prova=dataset.collect()

model=Sequential()

model.add(Dense(50,input_shape=(len(feature_rilevanti2),),activation="relu"))
model.add(Dense(100,activation="relu"))
model.add(Dense(1))

model.compile(loss="mean_squared_error",optimizer="adam",metrics=["acc"])

optimizer_conf=optimizers.Adam(lr=0.01)
opt_conf=optimizers.serialize(optimizer_conf)

estimator=ElephasEstimator()

estimator.setFeaturesCol("features2")
estimator.setLabelCol("nucleare_giorno_dopo")
estimator.set_keras_model_config(model.to_json())
estimator.set_num_workers(1)
estimator.set_epochs(2)
estimator.set_batch_size(1)
estimator.set_verbosity(1)
estimator.set_optimizer_config(opt_conf)
estimator.set_mode("synchronous")
estimator.set_loss("mean_squared_error")
estimator.set_metrics(["acc"])
estimator.set_nb_classes(50000)
estimator.setOutputCol("predizioni_nucleare")

#asb = VectorAssembler(inputCols=feature_rilevanti, outputCol='features')
asb2 = VectorAssembler(inputCols=feature_rilevanti2, outputCol='features2')
#scl = StandardScaler(inputCol='features', outputCol='scaled_features', withMean=True, withStd=True)
#lr = LinearRegression(predictionCol="predizioni",labelCol='price_giorno_dopo', featuresCol='scaled_features', maxIter=100, regParam=.1)

#pipeline = Pipeline(stages=[asb,asb2, scl, lr, estimator])


pipeline = Pipeline(stages=[asb2, estimator])

(training_data, test_data) = dataset.randomSplit([ 0.6, 0.4 ])


pipeline_model = pipeline.fit(training_data)
predictions = pipeline_model.transform(test_data)

evaluator1=RegressionEvaluator(predictionCol="predizioni_nucleare",labelCol="nucleare_giorno_dopo")

test=predictions.collect()
for x in test:
    print(str(x["predizioni_nucleare"])+":::"+str(x["nucleare_giorno_dopo"]))

# model.save('model.h5')
# with open('model.h5', 'rb') as f:
# 	f_content = f.read()
# tf.gfile.FastGFile(HDFS_prefix + 'model1.h5', 'wb').write(f_content)

print("finito")