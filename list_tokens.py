import requests
 
headers = {
    'X-Auth-Email': 'helloshebasarah@gmail.com',
    'X-Auth-Key': '2ed5a5383794be1a1ec92ccf6aaffae2c476b',
    'Content-Type': 'application/json'
    
    
}
#List all access tokens you created.
resp = requests.request(
     'GET',
     'https://api.cloudflare.com/client/v4/user/tokens',
     headers=headers   
 )

print(resp.status_code)
 
 
print(resp.json())