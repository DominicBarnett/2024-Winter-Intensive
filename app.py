import requests
import os
from flask import Flask, request, redirect, render_template, url_for
from bson.objectid import ObjectId
from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient

load_dotenv()
API_URL = 'https://api.currencybeacon.com/v1/convert'
CURRENCY_API_URL = 'https://api.currencybeacon.com/v1/currencies'
API_KEY = os.getenv('API_KEY')
app = Flask(__name__)
uri = 'mongodb+srv://dombarnett03:3SYrz9JsbamU6txd@cluster0.zvgijzx.mongodb.net/?retryWrites=true&w=majority'
client = MongoClient(uri)
db = client.CurrencyConversions

try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")

except Exception as e:
    print(e)

# for entry in currency_results_json['response']:
#         name = entry['name']
#         short_code = entry['short_code']
#         currency_dict[name] = short_code

# print(currency_dict)
    
def get_currency_dict():
    '''Creates API call to generate all available currency's to use'''
    currency_dict = {}
    currency_params = {
        'type' : 'fiat',
        'api_key' : API_KEY
    }
    currency_results_json = requests.get(CURRENCY_API_URL, params=currency_params).json()
    for entry in currency_results_json['response']:
        name = entry['name']
        short_code = entry['short_code']
        currency_dict[name] = short_code
    return currency_dict

def egg_price_conversion():
    ToCurrency = request.form['ToCurrency']
    print(ToCurrency)
    Eggs = 2.78

    params = {
            'from' : 'USD',
            'to' : ToCurrency,
            'amount': Eggs,
            'api_key': API_KEY
        }
    
    egg_conversion_json = requests.get(API_URL, params=params).json()
    Eggs = round(egg_conversion_json['response']['value'], 2)
    print(Eggs)

    return Eggs

@app.route('/', methods=('GET', 'POST'))
def index():
    context = {}
    if request.method=='POST':
        
        FromCurrency = request.form['FromCurrency']
        amount = request.form['amount']
        ToCurrency = request.form['ToCurrency']
        if ToCurrency != 'USD':
            Eggs = egg_price_conversion()
        else:
            Eggs = 2.78
        
        params = {
            'from' : FromCurrency,
            'to' : ToCurrency,
            'amount': amount,
            'api_key': API_KEY
        }
        results_json = requests.get(API_URL, params=params).json()
                # print(results_json)
        context = {
                'amount' : results_json['response']['amount'],
                'fromCurrency' : results_json['response']['from'],
                'toCurrency' : results_json['response']['to'],
                'newAmount' : round(results_json['response']['value'], 2),
                'QuantityOfEggs' : round(round(results_json['response']['value'], 2)/Eggs)
                }
        newAmount = round(results_json['response']['value'], 2)
        db.StoredConversions.insert_one({'FromCurrency': FromCurrency, 'amount': amount, 'ToCurrency': ToCurrency, 'NewAmount': newAmount})

    all_conversions = db.StoredConversions.find() 
    return render_template('index.html',currency_dict=get_currency_dict(), conversions=all_conversions, **context)


@app.route('/delete/<id>', methods=["POST"])
def delete(id):
    db.StoredConversions.delete_one({"_id": ObjectId(id)})
    return redirect(url_for('index'))




if __name__ == '__main__':
    app.run(debug=True)


