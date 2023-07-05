import requests
from flask import Flask
from flask import request, jsonify
from flask_mongoengine import MongoEngine

app = Flask(__name__)
app.config['MONGODB_SETTINGS'] = {
    'db': 'Lab14',
    'host': '127.0.0.1',
    'port': 27017
}

db = MongoEngine()
db.init_app(app)

class Context(db.Document):
    lugar = db.StringField()
    email = db.StringField(unique=True)
    # _id = 
    def to_json(self):
        return {"lugar": self.lugar,
                "email": self.email}



def obtener_coordenadas(nombre_lugar):
    url = f"https://nominatim.openstreetmap.org/search?q={nombre_lugar}&format=json"
    response = requests.get(url)

    data = response.json()    
    if data:
        latitud = data[0]['lat']
        longitud = data[0]['lon']        
        return latitud, longitud
    else:
        return None, None


def obtener_climas(latitud, longitud, days):
    url_diario = f"https://api.open-meteo.com/v1/forecast?latitude={latitud}&longitude={longitud}&forecast_days={days}&daily=temperature_2m_max&timezone=PST"
    response_diario = requests.get(url_diario)
    data_diario = response_diario.json()
    climas = data_diario['daily']['temperature_2m_max']
    return climas


@app.route('/')
def get_clima():
    nombre_lugar = request.args.get('lugar')
    dias = request.args.get('dias')
    context_id = request.args.get('context_id')
    email = request.args.get('email')

    if (context_id and dias and not nombre_lugar and email):
        current_context = Context.objects(id=context_id).first()
        nombre_lugar = current_context.lugar
        
    elif (context_id and dias and nombre_lugar and email):
        current_context = Context.objects.get(id=context_id)
        current_context.lugar = nombre_lugar
        current_context.save()

    elif (not context_id and dias and nombre_lugar and email):
        new_context = Context(lugar=nombre_lugar,email=email)
        new_context.save()
    
    
    latitud, longitud = obtener_coordenadas(nombre_lugar)
    if latitud and longitud:
        climas = obtener_climas(latitud, longitud,dias)
        current_context = Context.objects.get(email=email)
        return jsonify({"climas":climas,"context_id":str(current_context.id)})
    else:
        return jsonify({"error":"error"})

if __name__ == "__main__":
    app.run(debug=True, port=6100)