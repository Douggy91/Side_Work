import requests, time, os, re

target_url = 'https://192.168.31.161/api/v4/projects'
import_url = 'http://192.168.31.169/api/v4/projects'
gg_token = 'glpat-Bu3HhpJZQsmUsKxpnzsh'
import_token = 'glpat-oZPyAS31uR8i5vo5MnaL'
gg = requests.get(url=target_url, headers={'PRIVATE-TOKEN': gg_token} , verify=False)
path ="./"+time.strftime('%Y-%m-%d')+"_export"
pj = gg.json()
pj_dict = {}

for i in pj:
    pj_dict[i['id']] = i['path_with_namespace']
    # pj_dict[i['id']] = i['name']
print(pj_dict)


def reservation_export(project_list):
    if len(project_list) == 0:
        return
    project_id = project_list[0]
    url=target_url+'/'+str(project_id)+'/export'
    msg=requests.post(target_url+'/'+str(project_id)+'/export', headers={'PRIVATE-TOKEN':gg_token}, verify=False)
    print(f"{msg} : {url}")
    time.sleep(10)
    reservation_export(project_list[1:])


def get_download_export(project_list):
    try:
        os.mkdir(path)
    except:
        print("already exist dir")
    if len(project_list) == 0:
        return
    project_id = project_list[0]
    url=target_url+'/'+str(project_id)+'/export'
    status=requests.get(url, headers={'PRIVATE-TOKEN':gg_token}, verify=False)
    time.sleep(20)
    if status.ok: 
        content=requests.get(url+'/download', headers={'PRIVATE-TOKEN':gg_token}, verify=False)
        time.sleep(20)
        result=open(path+'/'+re.sub("/","@",pj_dict[project_id])+'.tar.gz','wb').write(content.content)
        time.sleep(20)
#        open(path+'/'+str(project_id)+"@"+re.sub("/","@",pj_dict[project_id])+'_export.tar.gz','wb').write(content.content)
        print(f"""
{result}
{status}
{content}
""")
        
    get_download_export(project_list[1:])

def import_project_file(file_list):
    if len(file_list) == 0:
        return
    file_name = file_list[0]
    file_path = path+"/"+file_name
    url=import_url+'/import'
#    url=import_url+'/'+file_name.split('@')[0]+'/import'
    files = {"file": open(file_path,"rb")}
    namespace=""
    for word in file_name.split('@')[:-1]:
        namespace += (word+"/")
    data = {
        "path": (file_name.split('@')[-1]).split('.')[0],
        "namespace": namespace.rstrip("/"),
        "overwrite": "true"
        }
    result=requests.post(url, headers={'PRIVATE-TOKEN':import_token} ,data=data, files=files, verify=False)
    time.sleep(10)
    print(f"""
{file_name}
{file_path}
{url}
{files}
{data}
{result}
""")
    import_project_file(file_list[1:])

#reservation_export(list(pj_dict.keys()))
#get_download_export(list(pj_dict.keys()))
import_project_file(os.listdir(path))
