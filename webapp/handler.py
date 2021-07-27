import os
import pickle
import pandas as pd
from flask             import Flask, request, Response
from rossmann.Rossmann import Rossmann

# Carregando o modelo
model = pickle.load(open('modelo/modelo_rossmann.pkl', 'rb'))

# Inicializa a API
app = Flask(__name__)

@app.route('/rossmann/predict', methods=['POST'])
def rossmann_predict():
    test_json = request.get_json()
    
    if test_json: # Tem dado?
        if isinstance(test_json, dict): # único exemplo
            test_raw = pd.DataFrame(test_json, index=[0])
        else: # multiplos examples
            test_raw = pd.DataFrame(test_json, columns=test_json[0].keys())
            
        # Instancia a Classe Rossmann
        pipeline = Rossmann()
        
        # Limpeza dos Dados
        df1 = pipeline.data_cleaning(test_raw)
        
        # Criação de Novos Atributos
        df2 = pipeline.feature_engineering(df1)
        
        # Preparação dos Dados
        df3 = pipeline.data_preparation(df2)
        
        # Predição
        df_response = pipeline.get_prediction(model, test_raw, df3)
        
        return df_response
        
    else:
        return Response('{}', status=200, mimetype='application/json')

if __name__ == '__main__':
	port = int(os.environ.get('PORT', 5000))
	app.run(host='0.0.0.0', port=port)