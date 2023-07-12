import requests

target_url = 'https://gitlab.nip.io/api/graphql'
gg_token = 'glpat-wu2GGuwxnBR4HfT7TxyY'
data = "{\"query\": \"query {project(fullPath: \\\"root/AC_GroupTest\\\") {jobs {nodes {id duration}}}}\"}"
header = {
    "Authorization": "Bearer ${gg_token}",
    "User-Agent" : "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Content-Type": "application/json"
    }
gg=requests.post(url=target_url, 
                 headers=header,
                 data=data , 
                 verify=False)
print(gg.json())