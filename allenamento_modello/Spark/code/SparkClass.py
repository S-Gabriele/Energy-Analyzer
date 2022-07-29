import shutil
import pyspark.sql.functions as funcs

from pyspark import SparkFiles
from pyspark.sql import SparkSession
from pyspark.ml.feature import VectorAssembler, StandardScaler
from pyspark.ml.classification import LinearSVC
from pyspark.ml.evaluation import MulticlassClassificationEvaluator
from pyspark.ml import Pipeline
import json

APP_NAME = 'training_price_prediction_model'
APP_DATASET_PATH = './data'
APP_DATASET_FILE = 'dataset_Log2.csv'

nazioni= ['ES', 'PT', 'FR', 'IT-NO', 'IT-CNO', 'IT-CSO', 'IT-SO', 'IT-SAR', 'IT-SIC', 'CH','AT', 'SI', 
'HR', 'ME','GR', 'BE', 'NL', 'DE', 'GB', 'IE', 'IS', 'DK-DK1', 'NO-NO4', 'SE', 'FI', 'RU-1', 'PL', 
'EE','LV', 'LT', 'CZ', 'SK', 'HU', 'RS', 'BG', 'RO', 'TR', 'GE']

spark = SparkSession.builder.appName(APP_NAME).config("spark.files.overwrite", "true").getOrCreate()
sparkContext=spark.sparkContext

print(sparkContext)

lines = sparkContext.textFile('data/2022-07-01/2022-07-01-ES.json') 

lines.count()