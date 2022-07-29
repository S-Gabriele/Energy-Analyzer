from ast import Str
from functools import partial
import pandas as pd
import json
from pyspark import SparkContext
from pyspark.sql import SparkSession
from pyspark.sql.dataframe import DataFrame
from pyspark.sql.types import *
from pyspark.sql.types import StructType,StructField, StringType
from elasticsearch import Elasticsearch
from datetime import datetime
from time import sleep
from pyspark.sql.functions import from_json
import pyspark.sql.types as tp
from pyspark.sql import types as st

from pyspark.ml import PipelineModel



APP_NAME = 'prize_prediction-streaming'
APP_BATCH_INTERVAL = 1


kafkaServer="kafkaserver:9092"
topic = "dati_energetici"
def process_row(row):
        
    
    elastic_host="https://elasticsearch01:9200"
    elastic_index="energy_prize_es"

    es = Elasticsearch(
    elastic_host,
    ca_certs="/app/certs/ca/ca.crt",
    basic_auth=("elastic", "energyanalyzer"), 
    )

    dati=row.asDict()
    dati["total_co2"]=dati["co2intensity"]*dati["totalProduction"]
    resp = es.index(index = elastic_index, document=dati)

    print(resp)

    '''
    for idx, row in enumerate(batch_df.collect()):
        row_dict = row.asDict()
        id = f'{batch_id}-{idx}'
        resp = es.index(index=elastic_index, id=id, document=row_dict)
        print(resp)


    batch_df.show()
    '''


spark = SparkSession.builder.appName(APP_NAME).getOrCreate()
spark.sparkContext.setLogLevel("ERROR")

model = PipelineModel.load("model")


# Define Training Set Structure
#Camabaire tutto un String
energyKafka = tp.StructType([
    
        tp.StructField('countryCode',               dataType= tp.StringType()),
        tp.StructField('totalProduction',           dataType= tp.DoubleType()),
        tp.StructField('maxProduction',             dataType= tp.DoubleType()),
        tp.StructField('price',                     dataType= tp.DoubleType()),
        tp.StructField('production_biomass',        dataType= tp.DoubleType()),
        tp.StructField('production_coal',           dataType= tp.DoubleType()),
        tp.StructField('production_gas',            dataType= tp.DoubleType()),
        tp.StructField('production_hydro',          dataType= tp.DoubleType()),
        tp.StructField('production_nuclear',        dataType= tp.DoubleType()),
        tp.StructField('production_oil',            dataType= tp.DoubleType()),
        tp.StructField('production_solar',          dataType= tp.DoubleType()),
        tp.StructField('production_unknown',        dataType= tp.DoubleType()),
        tp.StructField('production_wind',           dataType= tp.DoubleType()),
        tp.StructField('production_geothermal',     dataType= tp.DoubleType()),
        tp.StructField('co2intensity',              dataType= tp.DoubleType()),
        tp.StructField('stateDatetime',             dataType= tp.StringType())   
        
])




# Streaming Query
df = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", kafkaServer) \
    .option("subscribe", topic) \
    .load()




df = df.selectExpr("CAST(timestamp AS STRING)","CAST(value AS STRING)")\
        .select(from_json("value", energyKafka).alias("data"))\
        .select("data.*")\
        .na.fill(0)


results = model.transform(df)

results = results.drop("features", "scaled_features")


results = results.writeStream \
    .foreach(process_row).start()
    

results.awaitTermination()
