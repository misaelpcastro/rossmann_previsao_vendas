import os
import requests
import json
import pandas as pd
from flask import Flask, request, Response

# constants
TOKEN = '1928498229:AAGQcODpO3P8S04v3-2GFY7dgas9HlDDqNs'

## info sobre o bot
#https://api.telegram.org/bot1928498229:AAGQcODpO3P8S04v3-2GFY7dgas9HlDDqNs/getMe
#
## get updates
#https://api.telegram.org/bot1928498229:AAGQcODpO3P8S04v3-2GFY7dgas9HlDDqNs/getUpdates
#
## Webhook
#https://api.telegram.org/bot1928498229:AAGQcODpO3P8S04v3-2GFY7dgas9HlDDqNs/setWebhook?url=https://3b24d73a32b8a9.localhost.run
#
## Webhook
#https://api.telegram.org/bot1928498229:AAGQcODpO3P8S04v3-2GFY7dgas9HlDDqNs/setWebhook?url=https://rossmann-telegram-bot-mpc.herokuapp.com/
#
## send message
#https://api.telegram.org/bot1928498229:AAGQcODpO3P8S04v3-2GFY7dgas9HlDDqNs/sendMessage?chat_id=198305981&text=Olha vc de novo...


def send_message(chat_id, text):
	url = 'https://api.telegram.org/bot{}/'.format(TOKEN)
	url = url + 'sendMessage?chat_id={}'.format(chat_id)
	
	r = requests.post(url, json={'text':text})
	print('Status Code{}'.format(r.status_code))
	
	return None

def load_dataset(store_id):
	# Carregando Dados de Teste
	df10 = pd.read_csv('test.csv')
	df_store = pd.read_csv('store.csv')

	# Merge dos Dados de Teste e Store
	df_test = pd.merge(df10, df_store, how='left', on='Store')

	# Escolhendo uma loja para fazer a predição
	df_test = df_test[df_test['Store'] == store_id]

	if not df_test.empty:
		# Removendo os dias que a loja está fechada
		df_test = df_test[df_test['Open'] != 0]
		df_test = df_test[~df_test['Open'].isnull()]
		df_test = df_test.drop('Id', axis=1)
		
		# Convertendo Dataframe em Json
		data = json.dumps(df_test.to_dict(orient='records'))
	
	else:
		data = 'error'
	
	return data
	
def predict(data):
	# Chamada da API
	url = 'https://previsao-rossmann.herokuapp.com/rossmann/predict'
	header = {'Content-type': 'application/json'}
	data = data
	
	r = requests.post(url, data=data, headers=header)
	print('Status Code {}'.format(r.status_code))
	
	d1 = pd.DataFrame(r.json(), columns=r.json()[0].keys())
	
	return d1

def parse_message(message):
	chat_id = message['message']['chat']['id']
	store_id = message['message']['text']
	
	store_id = store_id.replace('/', '')
	
	try:
		store_id = int(store_id)
		
	except ValueError:
		store_id = 'error'
	
	return chat_id, store_id

# Inicialização da API
app = Flask(__name__)

@app.route('/', methods=['GET','POST'])
def index():
	if request.method == 'POST':
		message = request.get_json()
		
		chat_id, store_id = parse_message(message)
		
		if store_id != 'error':
			# carregando dados
			data = load_dataset(store_id)
			
			if data != 'error':
				# predição
				d1 = predict(data)
				
				# calculo
				d2 = d1[['store','prediction']].groupby('store').sum().reset_index()
				
				# envia a mensagem
				msg = 'Loja número {} vai vender R${:,.2f} nas próximas 6 semanas.'.format(d2['store'].values[0], d2['prediction'].values[0])
				
				send_message(chat_id, msg)
				return Response('Ok', status=200)
				
			else:
				send_message(chat_id, 'Store not available.')
				return Response('Ok', status=200)
		
		else:
			send_message(chat_id, 'Store ID is wrong.')
			return Response('Ok', status=200)
		
	else:
		return '<h1>Rossmann Telegram BOT</h1>'

if __name__ == '__main__':
	port = int(os.environ.get('PORT', 5000))
	app.run(host='0.0.0.0', port=port)