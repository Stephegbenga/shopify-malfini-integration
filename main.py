from flask import Flask, request
import phonenumbers
from decouple import config
from updatevariant import *
import requests

from flask_restful import Resource, Api
import json

user_name = config('user_name')
password = config('password')
shopkey = config('shopkey')

app = Flask(__name__)
api = Api(app)


def accesstoken():
    url = "https://api.malfini.com/api/v4/api-auth/login"

    payload = json.dumps({
        "username": user_name,
        "password": password
    })
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    return response


def checkifaddressexist(load):
    url = "https://api.malfini.com/api/v4/address"
    payload = {}
    headers = {
        'Authorization': f'Bearer {token}'
    }
    response = requests.request("GET", url, headers=headers, data=payload).json()
    exists = {"name": load['name'],"street":load['street'],"zipCode":load['zipCode'],"countryCode":load['countryCode'],"phone":load['phone'],"email":load['email']} in response
    return exists

def gettheaddressid(load):
    url = "https://api.malfini.com/api/v4/address"
    payload = {}
    headers = {
        'Authorization': f'Bearer {token}'
    }
    responses = requests.request("GET", url, headers=headers, data=payload).json()
    for response in responses:
        if response['name'] == load['name'] and response['street'] == load['street'] and response['countryCode'] == load['countryCode'] and response['phone'] == load['phone'] and response['email'] == load['email'] and response['zipCode'] == load['zipCode']:
            return response['id']




# This creates an address of that user on Malfini
def createaddress(name, street, countrycode, zipcode, city, phoneno, email):
    datatoken = accesstoken().json()
    token = datatoken['access_token']
    print(token)
    url = "https://api.malfini.com/api/v4/address"
    phonenumberprefix = phonenumbers.parse("100993393939", countrycode).country_code
    phonenumber = f'+{phonenumberprefix}-{phoneno}'
    load = {
        "name": name,
        "recipient": name,
        "street": street, #"test_street"
        "countryCode": countrycode,#"DE"
        "zipCode": f"{zipcode}", #"65929",
        "city": city, #"test city 2",
        "phone": phonenumber, #"+1-8722717528",
        "email": email, #"testing01@xample.com",
        "invoiceDeliveryId": 2,
        "isValid": True
    }
    checkaddress = checkifaddressexist(load)
    if checkaddress == True:
        address_id = gettheaddressid(load)
        return address_id
    payload = json.dumps(load)
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    print(payload)
    response = requests.request("POST", url, headers=headers, data=payload).json()
    print(response)
    return response['id']

@app.route('/')
def homepage():
    return "hello baseshirt"


@app.route('/ordercreate', methods=['POST'])
def ordercreation():
    data = request.get_json()
    print(data)
    products = []
    addressid = createaddress(data['shipping_address']['name'], data['shipping_address']['address1'], data['shipping_address']['country_code'], data['shipping_address']['zip'], data['shipping_address']['city'], data['shipping_address']['phone'], data['email'])
    print(addressid)
    lineitems = data['line_items']
    for lineitem in lineitems:
        quantity = lineitem['quantity']
        sku = lineitem['sku']
        qusku = {"productSizeCode":sku, "count":quantity}
        products.append(qusku)

    token = accesstoken().json()['access_token']
    print(token)
    url = "https://api.malfini.com/api/v4/order"
    payload = json.dumps({
        "invoiceDeliveryTypeId": 3,
        "addressId": int(addressid),
        "deliveryId": 75,
        "paymentId": 9,
        "customOrderId": f"{data['id']}",
        "products": products
    })
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.json())
    return "Success"

api.add_resource(update, '/update')



if __name__ == '__main__':
    app.run()
