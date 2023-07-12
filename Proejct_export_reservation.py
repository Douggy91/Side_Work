import requests, time

target_url = 'https://gitlab.nip.io/api/v4/projects'
gg_token = 'glpat-Bu3HhpJZQsmUsKxpnzsh'
gg = requests.get(url=target_url, headers={'PRIVATE-TOKEN': gg_token} , verify=False)
pj = gg.json()
pj_dict = {}

# 프로젝트의 id_list 추출
for i in pj:
    pj_dict[i['id']] = i['name']
print(pj_dict[2])


def reservation_export(project_list):
    if len(project_list) == 0:
        return
    project_id = project_list[0]
    url=target_url+'/'+str(project_id)+'/export'
    msg=requests.post(target_url+'/'+str(project_id)+'/export', headers={'PRIVATE-TOKEN':gg_token}, verify=False)
    print(f"{msg} : {url}")

    reservation_export(project_list[1:])


def get_download_export(project_list):
    if len(project_list) == 0:
        return
    project_id = project_list[0]
    url=target_url+'/'+str(project_id)+'/export'
    status=requests.get(url, headers={'PRIVATE-TOKEN':gg_token}, verify=False)
    print(f"{status.ok} / {url}")
    if status.ok:
        content=requests.get(url+'/download', headers={'PRIVATE-TOKEN':gg_token}, verify=False)
        open(time.strftime('%Y-%m-%d')+'-'+pj_dict[project_id]+'-export.tar.gz','wb').write(content.content)
        time.sleep(2)
        
    get_download_export(project_list[1:])

# reservation_export(pj_list)
# print(list(pj_dict.keys()))
get_download_export(list(pj_dict.keys()))