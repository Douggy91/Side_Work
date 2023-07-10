import requests, json

target_url = 'https://gitlab.nip.io/api/v4/projects'
gg_token = 'glpat-wu2GGuwxnBR4HfT7TxyY'
gg = requests.get(url=target_url, headers={'PRIVATE-TOKEN': gg_token} , verify=False)
pj = gg.json()
pj_list = []
statics = {}

target_date="<date>"

# 프로젝트의 id_list 추출
for i in pj:
    pj_list.append(i['id'])

def get_content(project_id, method):
    content = requests.get(url=target_url+'/'+str(project_id)+'/'+method, headers={'PRIVATE-TOKEN': gg_token} , verify=False)
    return content

def get_job_list(statics_list, statics, statics_avg):
    if len(statics_list) == 0:
        return
    proj_id = statics_list[0]
    if statics_avg < statics[proj_id]:
        jobs_content=get_content(proj_id, "jobs").json()
        get_jobs_content(jobs_content, proj_id)
    get_job_list(statics_list[1:], statics, statics_avg)

def get_jobs_content(jobs_content, proj_id):
    if len(jobs_content) == 0:
        return
    jobs_id = jobs_content[0]
    if jobs_id['finished_at'] < target_date:
        requests.delete(target_url+'/'+str(proj_id)+'/jobs/'+str(jobs_id['id'])+'/artifacts',headers={'PRIVATE-TOKEN': gg_token} , verify=False)    

def remove_artifact(project_list):
    if len(project_list) == 0:
        return
    project_id = project_list[0]
    statistics_content = get_content(project_id,'statistics').json()
    fetch_list = statistics_content['fetches']
    # statics dict에 proj_id : value로 정리
    statics[project_id] = fetch_list['total']/len(fetch_list['days'])
    # 전체 평균
    statics_avg = sum(statics.values())/len(statics)
    get_job_list(list(statics.keys()), statics, statics_avg)   
    remove_artifact(project_list[1:])


# for id in pj_list:    
#     # 프로젝트 별 statistics 추출
#     statistics_content = get_content(id,'statistics').json()
#     fetch_list = statistics_content['fetches']
#     # statics dict에 proj_id : value로 정리
#     statics[id] = fetch_list['total']/len(fetch_list['days'])
#     # 전체 평균
#     statics_avg = sum(statics.values())/len(statics)
#     # 평균 fetch를 넘는 프로젝트에 대해서 jobs 추출
#     for proj_id in statics.keys():
#         if statics_avg < statics[proj_id]:
#             jobs_content=get_content(proj_id, "jobs").json()
#             # jobs 중 특정 일자보다 이전의 jobs의 artifacts를 삭제 
#             for jobs_list in jobs_content:
#                 if jobs_list['finished_at'] < target_date:
#                     requests.delete(target_url+'/'+str(proj_id)+'/jobs/'+str(jobs_list['id'])+'/artifacts',headers={'PRIVATE-TOKEN': gg_token} , verify=False)

## 이후에 gitlab서버에서 rake gitlab:cleanup:orphan_job_artifact_files DRY_RUN=false 수행



remove_artifact(pj_list)