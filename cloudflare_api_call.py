import requests
import json
 
headers = {
    'X-Auth-Email': 'helloshebasarah@gmail.com',
    'X-Auth-Key': '2ed5a5383794be1a1ec92ccf6aaffae2c476b',
    'Content-Type': 'application/json'
    
    
}
data={
   'name':'readonly-token',
   'policy':{
    "id": "f267e341f3dd4697bd3b9f71dd96247f",
    "effect": "allow",
   }
   
} 

response = requests.request(
    'PUT',
    'https://api.cloudflare.com/client/v4/user/tokens/54aad0c5b4e9d961a59c58d2fc86260a/value',
     headers=headers,
    
    
)

if response and response.status_code == 200:
    print('Request was successful')
    

    data=response.json()
    print(data)
    print(data["result"])
    

# resp = requests.request(
#      'GET',
#      'https://api.cloudflare.com/client/v4/user/tokens',
#      headers=headers   
#  )

 #print(resp.status_code)
 
 
# print(resp.json())

