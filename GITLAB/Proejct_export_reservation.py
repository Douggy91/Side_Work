import requests, time, os

target_url = 'https://gitlab.nip.io/api/v4/projects'
export_url = 'https://gitlab.nip.io/api/v4/projects'
gg_token = 'glpat-Bu3HhpJZQsmUsKxpnzsh'
export_token = 'glpat-Bu3HhpJZQsmUsKxpnzsh'
gg = requests.get(url=target_url, headers={'PRIVATE-TOKEN': gg_token} , verify=False)
path = `./time.strftime('%Y-%m-%d')_export`
pj = gg.json()
pj_dict = {}

# 프로젝트의 id_list 추출
for i in pj:
    pj_dict[i['id']] = i['path_with_namespace']
    # pj_dict[i['id']] = i['name']
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
    try:
        os.mkdir(path)
    if len(project_list) == 0:
        return
    project_id = project_list[0]
    url=target_url+'/'+str(project_id)+'/export'
    status=requests.get(url, headers={'PRIVATE-TOKEN':gg_token}, verify=False)
    print(f"{status.ok} / {url}")
    if status.ok:
        content=requests.get(url+'/download', headers={'PRIVATE-TOKEN':gg_token}, verify=False)
        open(path+'/'+pj_dict[project_id]+'_export.tar.gz','wb').write(content.content)
        # open(time.strftime('%Y-%m-%d')+'_'+pj_dict[project_id]+'_export.tar.gz','wb').write(content.content)
        time.sleep(2)
        
    get_download_export(project_list[1:])

def import_project_file(file_list):
    if len(file_list) == 0:
        return
    file_name = file_list[0]
    url=export_url+'/import'
    files = {"file": open(file_name,"rb")}
    namespace=""
    for word in file_name.split('/')[:-1]:
        namespace += (word+"/")
    data = {
        "path": file_name.split('/')[-1],
        "namespace": namespace.rstrip("/")
        }
    requests.post(url, headers={'PRIVATE-TOKEN':export_token}, verify=False ,data=data, file=file)
    time.sleep(2)
    import_project_file(file_list[1:])
# reservation_export(pj_list)
# print(list(pj_dict.keys()))
get_download_export(list(pj_dict.keys()))
import_project_file(os.listdir(path))