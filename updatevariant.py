from flask import Flask
from flask_restful import Resource, Api
import requests
from decouple import config
import urllib.request
import json
from time import sleep
import time
import threading

start_time = time.time()



user_name = config('user_name')
password = config('password')
shopkey = config('shopkey')
# get token
def token():
    url = "https://api.malfini.com/api/v4/api-auth/login"

    payload = json.dumps({
        "username": f"{user_name}",
        "password": f"{password}"
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload).json()
    # print(response)
    token = response['access_token']
    return token


tokenn = token()
url = "https://api.malfini.com/api/v4/product/availabilities"
payload={}
headers = {
  'Authorization': f'Bearer {tokenn}'
}
responsesformalfiniquantity = requests.request("GET", url, headers=headers, data=payload).json()



def getavailabilities(productSizeCode):
    for response in responsesformalfiniquantity:
        if response['productSizeCode'] == productSizeCode:
            # print(f"The product sizecode is {response['productSizeCode']}")
            return response['quantity']

def setinventoryquantity(inventory_item_id, location_id, quantity, variantsku):
    try:
        url = "https://richtiger-kevin.myshopify.com/admin/api/2022-01/inventory_levels/set.json"

        payload = json.dumps({
            "location_id": location_id,
            "inventory_item_id": inventory_item_id,
            "available": quantity
        })
        headers = {
            'X-Shopify-Access-Token': f'{shopkey}',
            'Content-Type': 'application/json'
        }
        response = requests.request("POST", url, headers=headers, data=payload).json()
        # print(f"variantsku: {variantsku} Inventoryid: {inventory_item_id} Locationid:{location_id} Quantity: {quantity} {response}\n\n")
        return response
    except:
        sleep(10)
        url = "https://richtiger-kevin.myshopify.com/admin/api/2022-01/inventory_levels/set.json"

        payload = json.dumps({
            "location_id": location_id,
            "inventory_item_id": inventory_item_id,
            "available": quantity
        })
        headers = {
            'X-Shopify-Access-Token': f'{shopkey}',
            'Content-Type': 'application/json'
        }
        response = requests.request("POST", url, headers=headers, data=payload).json()
        # print(response)
        return response



def getinventorydata(inventory_item_id):
    try:
        url = f"https://richtiger-kevin.myshopify.com/admin/api/2022-01/inventory_levels.json?inventory_item_ids={inventory_item_id}"

        payload = {}
        headers = {
            'X-Shopify-Access-Token': f'{shopkey}'
        }
        response = requests.request("GET", url, headers=headers, data=payload).json()
        # print(response)
        # print(f"This is the location id {response['inventory_levels'][0]['location_id']}")
        return response['inventory_levels'][0]['location_id']
    except:
        sleep(10)
        url = f"https://richtiger-kevin.myshopify.com/admin/api/2022-01/inventory_levels.json?inventory_item_ids={inventory_item_id}"

        payload = {}
        headers = {
            'X-Shopify-Access-Token': f'{shopkey}'
        }
        response = requests.request("GET", url, headers=headers, data=payload).json()
        # print(response)
        # print(f"This is the location id {response['inventory_levels'][0]['location_id']}")
        return response['inventory_levels'][0]['location_id']


# Variant Price from malfini
tokenn = token()
url = "https://api.malfini.com/api/v4/product/prices"
payload = {}
headers = {
    'Authorization': f'Bearer {tokenn}'
}
malfinipricelist = requests.request("GET", url, headers=headers, data=payload).json()


def malfiniprice(sku):
    for prices in malfinipricelist:
        try:
            prices['limit']
        except:
            prices['limit'] = 1
        if prices['productSizeCode'].strip() == sku.strip() and prices['limit'] == 1:
            product_price = prices['price']
            # print(f"-{sku}-{product_price}")
            return product_price
        elif prices['productSizeCode'].strip() == sku.strip() and prices['limit'] == "1":
            product_price = prices['price']
            # print(f"-{sku}-{product_price}")
            return product_price




# Update Varint Price:
def updatevariantprice(price, variantid):
    url = f"https://richtiger-kevin.myshopify.com/admin/api/2021-10/variants/{variantid}.json"

    payload = json.dumps({
        "variant": {
            "price": price
        }
    })
    headers = {
        'X-Shopify-Access-Token': f'{shopkey}',
        'Content-Type': 'application/json'
    }
    response = requests.request("PUT", url, headers=headers, data=payload).json()



# Get The Link for the Bulk Product

def getbulkproductlink():
    url = "https://richtiger-kevin.myshopify.com/admin/api/2020-04/graphql.json"
    payload = "{\"query\":\"mutation {\\r\\n  bulkOperationRunQuery(\\r\\n   query: \\\"\\\"\\\"\\r\\n   {\\r\\n      inventoryItems {\\r\\n        edges {\\r\\n          node {\\r\\n            variant {\\r\\n              id\\r\\n              price\\r\\n              inventoryQuantity\\r\\n              compareAtPrice\\r\\n              availableForSale\\r\\n              barcode\\r\\n              product {\\r\\n                id\\r\\n                title\\r\\n              }\\r\\n            }\\r\\n            id\\r\\n            sku\\r\\n            tracked\\r\\n          }\\r\\n        }\\r\\n      }\\r\\n    }\\r\\n    \\\"\\\"\\\"\\r\\n  ) {\\r\\n    bulkOperation {\\r\\n      id\\r\\n      status\\r\\n    }\\r\\n    userErrors {\\r\\n      field\\r\\n      message\\r\\n    }\\r\\n  }\\r\\n}\",\"variables\":{}}"
    headers = {
        'X-Shopify-Access-Token': f'{shopkey}',
        'Content-Type': 'application/json'
    }
    bulkproductresponse = requests.request("POST", url, headers=headers, data=payload).json()
    # print(bulkproductresponse)
    pollbulkproduct()

def pollbulkproduct():
    url = "https://richtiger-kevin.myshopify.com/admin/api/2020-04/graphql.json"

    payload = "{\"query\":\"query {\\r\\n  currentBulkOperation {\\r\\n    id\\r\\n    status\\r\\n    errorCode\\r\\n    createdAt\\r\\n    completedAt\\r\\n    objectCount\\r\\n    fileSize\\r\\n    url\\r\\n    partialDataUrl\\r\\n  }\\r\\n}\",\"variables\":{}}"
    headers = {
        'X-Shopify-Access-Token': f'{shopkey}',
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload).json()
    if response['data']['currentBulkOperation']['status'] == 'COMPLETED':
        bulkproductlink = response['data']['currentBulkOperation']['url']
        # print(bulkproductlink)
        startupdating(bulkproductlink)
    else:
        print("Not yet Completed")
        sleep(2)
        pollbulkproduct()

def notempty():
    print("Bulk Product link is not empty")

def startupdating(bulkproductlink):
    with urllib.request.urlopen(bulkproductlink) as url:
        array = list(url)

    data = []
    for json_str in array:
        result = json.loads(json_str)
        data.append(result)
    # print(data)
    for variant in data:
        variantsku = variant['sku']
        inventoryid = variant['id'].split('/')[4]
        variantid = variant['variant']['id'].split('/')[4]
        variantprice = malfiniprice(variantsku)
        updatevariantprice(variantprice,variantid)
        locationid = getinventorydata(inventoryid)
        quantity = getavailabilities(variantsku)
        setinventoryquantity(inventoryid, locationid, quantity, variantsku)
    print("========== All Proces Completed Sucessfully")
    print("--- %s seconds ---" % (time.time() - start_time))


class update(Resource):
    def get(self):
        threading.Thread(target=getbulkproductlink).start()
        return "Working on it"


