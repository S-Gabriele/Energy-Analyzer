# <p style="text-align:center">  Energy Analyzer </p>

### A data processing stream for energy production and Co2 intensity

![img](./book/images/pipeline.png?raw=true "Pipeline")
<br>
This project provides a simulated real-time visualization of the energy production of the main countries of the Euro-Asian continent and their CO2 emissions, the technologies used are the following:
* <a href="https://www.docker.com/">Docker</a> to create and manage containers
* <a href="https://app.electricitymaps.com/map">Electricity Map</a> as real time data source 
* <a href="	https://www.elastic.co/logstash/">Logstash</a> for data ingestion
* <a href="https://zookeeper.apache.org/">ZooKeeper</a> + <a href="https://kafka.apache.org/">Kafka</a> for data stream processing
* <a href="	https://spark.apache.org/">Spark</a> to process data
* <a href="	https://www.elastic.co/elasticsearch/">Elastic Search</a> for data indexing
* <a href="https://www.elastic.co/kibana/">Kibana</a> for data visualization
<br>

### Run the project
```shell
$ git clone https://github.com/
$ cd 
$ docker-compose up 
```

### Credentials for Kibana and Elasticsearch
Elasticsearch:
>- user: elastic
>- password: energyanalyzer

Kibana:
>- user: kibana_system
>- password: energyanalyzer

### Import the dashboard into Kibana
Once the Dashboard has been built, it can be saved together with all the inserted objects (views and maps) in an ndjson type file. To do this, click on the menu on the left and go to Management> Stack Management, in the drop-down on the left click on Kibana> Saved Objects, find your Dashboard and export it, making sure to include the objects inside it. <br>
![img](./book/images/export.png?raw=true "Export")

To reload the saved Dashboard re-enter the Saved Objects section and click on import.

![img](./book/images/import.png?raw=true "Export")



### Exit status 78 of elasticsearch01 using WSL
The elasticsearch01 container could come out with exit status 78, going to see the errors you will probably see the message <br>
>- "Elasticsearch: Max virtual memory areas vm.max_map_count [65530] is too low, increase to at least [262144]". <br>
The error message states that the memory granted to the WSL is too low <br>

If this is the case, it should be sufficient to run these two commands using a prompt before compose up: <br>
```shell
$ wsl -d docker-desktop
$ sysctl -w vm.max_map_count=262144
```

## Useful links 

|Service                 | Link                   | Note                                              |
|------------------------|------------------------|---------------------------------------------------|
|KafkaUI                 |http://localhost:8080   | To check the status of topics and their messages  |
|Cluster Elastic Search  |https://localhost:9200/ | To view the ES index                              |
|Kibana                  |http://localhost:5601/  | To access the dashboard                           |

<br>
<h3> Authors </h3>
- <a href="https://github.com/S-Gabriele/">Gabriele Sanguedolce</a>
- <a href="https://github.com/ciccio2305/">Francesco Cristoforo Conti</a>









