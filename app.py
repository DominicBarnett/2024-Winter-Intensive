import requests
import os
from flask import Flask, request, redirect, render_template, url_for
from bson.objectid import ObjectId
from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient

load_dotenv()

API_URL = 'https://api.currencybeacon.com/v1/convert'
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



@app.route('/', methods=('GET', 'POST'))
def index():
    context = {}

    if request.method == 'POST':
        FromCurrency = request.form['FromCurrency']
        amount = request.form['amount']
        ToCurrency = request.form['ToCurrency']
        db.StoredConversions.insert_one({'FromCurrency': FromCurrency, 'amount': amount, 'ToCurrency': ToCurrency})

        params = {
            'from': FromCurrency,
            'to': ToCurrency,
            'amount': amount,
            'api_key': API_KEY
        }
        try:
            results_json = requests.get(API_URL, params=params).json()
            if results_json.get('success', False):
                context = {
                    'amount': results_json['response']['amount'],
                    'fromCurrency': results_json['response']['from'],
                    'toCurrency': results_json['response']['to'],
                    'newAmount': results_json['response']['value']
                }
        except Exception as e:
            print(f"Error in API request: {e}")

        # Separate the redirect from the return statement
        return redirect(url_for('index'))

    all_conversions = db.StoredConversions.find()
    return render_template('index.html', conversions=all_conversions, **context)
# def index():
#     context = {}
#     if request.method=='POST':
#         FromCurrency = request.form['FromCurrency']
#         amount = request.form['amount']
#         ToCurrency = request.form['ToCurrency']
#         db.StoredConversions.insert_one({'FromCurrency': FromCurrency, 'amount': amount, 'ToCurrency': ToCurrency})

#         params = {
#             'from' : FromCurrency,
#             'to' : ToCurrency,
#             'amount': amount,
#             'api_key': API_KEY
#         }
#     #     results_json = requests.get(API_URL, params=params).json()
#     #     # print(results_json)
#     #     context = {
#     #     'amount' : results_json['response']['amount'],
#     #     'fromCurrency' : results_json['response']['from'],
#     #     'toCurrency' : results_json['response']['to'],
#     #     'newAmount' : results_json['response']['value']

#     #     }
#     #     return redirect(url_for('index')), results_json, context
#         try:
#             results_json = requests.get(API_URL, params=params).json()
#             if results_json.get('success', False):
#                 context = {
#                     'amount': results_json['response']['amount'],
#                     'fromCurrency': results_json['response']['from'],
#                     'toCurrency': results_json['response']['to'],
#                     'newAmount': results_json['response']['value']
#                 }
#         except Exception as e:
#             print(f"Error in API request: {e}")

#         return redirect(url_for('index')), context

#     all_conversions = db.StoredConversions.find() # Add this line outside the if block! 
#     return render_template('index.html', conversions=all_conversions, **context)
        

@app.route('/delete/<id>', methods=["POST"])
def delete(id):
    db.StoredConversions.delete_one({"_id": ObjectId(id)})
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)


