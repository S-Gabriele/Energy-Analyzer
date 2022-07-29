from flask import Flask, json
from datetime import date, datetime

tapserver = Flask(__name__)

dati=[]

nazioni= ['ES', 'PT', 'FR',  'CH','AT', 'SI', 'HR', 'ME','GR', 'BE', 'NL', 'DE', 'GB', 'IE', 'IS', 'SE',\
    'FI', 'PL', 'EE','LV', 'LT', 'CZ', 'SK', 'HU', 'RS', 'BG', 'RO', 'TR', 'GE','DK-DK1','NO-NO4','RU-1']


italia=['IT-CNO', 'IT-CSO', 'IT-SO', 'IT-SAR', 'IT-SIC']

def feature(elem):
    return elem["stateDatetime"] [5:13]

#inseriamo i dati per l'italia combinanod le informazioni per ogni regione

for i in range(0,9):
    for d in range(0,24):
        stringe='dati/2022-07-1'+str(i)+'/2022-07-1'+str(i)+'-'+'IT-NO'+'.json'
        f = open(stringe)
        data = json.load(f)
        f.close()


        nuovo_dato={
                    
                    "co2intensity":data["data"][d]["co2intensity"]*data["data"][d]["totalProduction"],
                    "stateDatetime":data["data"][d]["stateDatetime"],
                    "countryCode":'IT',

                    "totalProduction":data["data"][d]["totalProduction"],
                    "maxProduction":data["data"][d]["maxProduction"],
                    "price":(data["data"][d]["price"]["value"]/6),

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

        for naz in italia:
            stringe='dati/2022-07-1'+str(i)+'/2022-07-1'+str(i)+'-'+naz+'.json'
            f = open(stringe)
            data = json.load(f)
            f.close()
            #dati.append(data["data"][d])
            nuovo_dato["maxProduction"]+=data["data"][d]["maxProduction"]

            nuovo_dato["totalProduction"]+=data["data"][d]["totalProduction"]
            parziale=(data["data"][d]["price"]["value"])/6
            nuovo_dato["price"]+=parziale
            nuovo_dato["co2intensity"]+=data["data"][d]["co2intensity"]*data["data"][d]["totalProduction"]
            nuovo_dato["production_biomass"]+=data["data"][d]["production"]["biomass"]
            nuovo_dato["production_coal"]+=data["data"][d]["production"]["coal"]
            nuovo_dato["production_gas"]+=data["data"][d]["production"]["gas"]
            nuovo_dato["production_geothermal"]+=data["data"][d]["production"]["geothermal"]
            nuovo_dato["production_hydro"]+=data["data"][d]["production"]["hydro"]
            nuovo_dato["production_nuclear"]+=data["data"][d]["production"]["nuclear"]
            nuovo_dato["production_oil"]+=data["data"][d]["production"]["oil"]
            nuovo_dato["production_solar"]+=data["data"][d]["production"]["solar"]
            nuovo_dato["production_unknown"]+=data["data"][d]["production"]["unknown"]
            nuovo_dato["production_wind"]+=data["data"][d]["production"]["wind"]


        nuovo_dato["co2intensity"]= nuovo_dato["co2intensity"]/nuovo_dato["totalProduction"]
        dati.append(nuovo_dato)
                
#inseriamo i dati per tutte le nazioni europee

for i in range(0,9):
    for d in range(0,24):
        for naz in nazioni:
            stringe='dati/2022-07-1'+str(i)+'/2022-07-1'+str(i)+'-'+naz+'.json'
            f = open(stringe)
            data = json.load(f)
            f.close()
            
            #dati.append(data["data"][d])

            #scegliamo il tag corretto per i dati di alcune nazioni che hanno un tag diverso da quello a due lettere
            cc=data["data"][d]["countryCode"]

            if cc=='DK-DK1':
                cc="DK"
            elif cc=='NO-NO4':
                cc="NO"
            elif cc=='RU-1':
                cc="RU"

            dati.append( {
                    "stateDatetime":data["data"][d]["stateDatetime"],
                    "countryCode":cc,
                    "totalProduction":data["data"][d]["totalProduction"],
                    "maxProduction":data["data"][d]["maxProduction"],
                    "price":data["data"][d]["price"]["value"],
                    "co2intensity":data["data"][d]["co2intensity"],
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



dati.sort(reverse = True,key=feature)

@tapserver.route("/return-log")
def return_log():    
    send = dati.pop()
    print(send)
    send_json = json.dumps(send)
    return send_json

if __name__ == "__main__":
    tapserver.run(debug=True,
            host='0.0.0.0',
            port=8000)

