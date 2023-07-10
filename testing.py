import re                                              
import subprocess 

input_lines = input()

all_ok = True                                 
                                                                                   
for each_line in input_lines:                                                      
    if each_line:                                                                  
        #print "Content: " + each_line                                             
        (base, commit, ref) = each_line.strip().split()                            
        valid_commit_msg = False                                                   
                                                                                                               
        if ref[:9] == "refs/tags": # Skip tags                                                                 
            all_ok = True                                                                                      
            continue                                                                                           
                                                                                                               
        new_br_push = re.match(r'[^1-9]+', base) #handles new branches being pushed                            
        if new_br_push:                
            all_ok = True              
            continue                                                                                           
                                                                                                  
        revs = base + "..." + commit                                                                           
        proc = subprocess.Popen(['git', 'rev-list','--oneline','--first-parent', revs], stdout=subprocess.PIPE)
        lines = proc.stdout.readlines()                                                           
        if lines:                                                                                                        
            for line in lines:                                                                                           
                item = str(line)                                                                                         
                idx = item.index(' ')                                                                                    
                rev = item.split()[0]                                                                                    
                rest = item.split()[1:]                                                                                  
                print("Debug in pre-receive ... Item: %s, Check these messages: %s" % (rev, rest))                                                                                   
                match_any = re.search(r'(add|modify|remove|update|repair|refactor|test)+', rest[0], re.I|re.MULTILINE)   
                if match_any is not None:                                                                                
                    valid_commit_msg = True     
                                                                                                                         
        #print "\n", valid_commit_msg, new_branch_push, branch_deleted, "\n"                                             
                                                 
        if valid_commit_msg:                               
            all_ok = True                                                   
            continue                                                        
        else:
            all_ok = False                                                                                               
            break                                                                                                                                                                 
if all_ok: #or new_branch_push or branch_deleted:
    exit(0)                                                                                                              
else:                                                                                                                    
    print("""
[From the GitLab master]            
Commit Message must contain one of these word in FirstLine:
[add, modify, remove, update, repair, refactor, test]                     
Please write detail Content what you do in SecondLind 
          """)                  
    exit(1)                