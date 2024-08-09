import json
import os
import pyautogui

def ValidateConfig(path):
    Count=0
    try:
        with open(path, "r") as f:
            config = json.loads(f.read())
    except json.JSONDecodeError as err:
        print(f"Invalid Json file: {err}")
        return False
    except OSError as err:
        print(f"Can't read file {path}: {err}")
        return False

    TaskType=['command','timeout','match','detect']
    TaskId=[]
    DuplicateId=[]
    for i,task in enumerate(config):
        if type(task)!=dict:
            continue
        if 'id' in task.keys():
            if type(task['id'])!=str:
                continue
            if task['id'] in TaskId:
                if not task['id'] in DuplicateId:
                    DuplicateId.append(id)
                continue
            TaskId.append(task['id'])

    print(f"\n\nLoaded task ids {TaskId}\n\n")

    for i,task in enumerate(config):
        print("="*10+f"Task {i:5d}"+"="*10)
        if type(task)!=dict:
            print(f"task shoud be a dict, not {task} with type {type(task)}")
            Count+=1
            continue
        
        if not 'id' in task.keys():
            print(f'missing key value "id"')
            Count+=1
        else:
            if type(task['id'])!=str:
                print(f"value of key id shoud be a str, not {task['id']} with type {type(task['id'])}")
                Count+=1
            if task['id'] in DuplicateId:
                print(f"Duplicate Id {task['id']}")
                Count+=1

        if not 'start' in task.keys():
            print(f'missing key value "start"')
            Count+=1
        else:
            if type(task['start'])!=bool:
                print(f"value of key start shoud be a bool, not {task['start']} with type {type(task['start'])}")
                Count+=1

        if not 'nextTasks' in task.keys():
            print(f'missing key value "nextTasks"')
            Count+=1
        else:
            if type(task['nextTasks'])!=list:
                print(f"value of key nextTasks shoud be a list, not {task['nextTasks']} with type {type(task['nextTasks'])}")
                Count+=1
            else:
                for j,nextTask in enumerate(task['nextTasks']):
                    if type(nextTask)!=dict:
                        print(f"nextTasks[{j}]: value in array nextTasks shoud be a dict, not {nextTask} with type {type(nextTask)}")
                        Count+=1
                    else:
                        if not 'operate' in nextTask.keys():
                            print(f'nextTasks[{j}]: missing key value "operate"')
                            Count+=1
                            if not nextTask['operate'] in ['start','stop']:
                                print(f"nextTasks[{j}]: Unknown operate {nextTask['operate']}")
                                Count+=1
                        
                        if not 'id' in nextTask.keys():
                            print(f'nextTasks[{j}]: missing key value "id"')
                            Count+=1
                            if not nextTask['id'] in TaskId:
                                print(f"nextTasks[{j}]: Unknown Id {nextTask['id']}")
                                Count+=1

        if not 'type' in task.keys():
            print(f'missing key value "type"')
            Count+=1
            continue
        if not task['type'] in TaskType:
            print(f"Unknown Task type {task['type']}")
            Count+=1
            continue

        if task['type']=='command':
            if not 'command' in task.keys():
                print('missing key value "command"')
                Count+=1
            else:
                if type(task['command'])!=list:
                    print(f"value of key command shoud be a list, not {task['command']} with type {type(task['command'])}")
                    Count+=1
                else:
                    for j,command in enumerate(task['command']):
                        if type(command)!=str:
                            print(f"command[{j}]: value in array command shoud be a str, not {command} with type {type(command)}")
                            Count+=1

        if task['type']=='keypress':
            if not 'keys' in task.keys():
                print('missing key value "keys"')
                Count+=1
            else:
                if type(task['keys'])!=list:
                    print(f"value of key keys shoud be a list, not {task['keys']} with type {type(task['keys'])}")
                    Count+=1
                else:
                    for j,keyset in enumerate(task['keys']):
                        if type(keyset)!=list:
                            print(f"keys[{j}]: value in array keys shoud be a list, not {keyset} with type {type(keyset)}")
                            Count+=1
                        else:
                            for k,key in enumerate(keyset):
                                if not key in pyautogui.KEYBOARD_KEYS:
                                    print(f"keys[{j}][{k}]: unknown key {key}")
                                    Count+=1
        
        if task['type']=='match':
            f1,f2,f3,f4=False,False,False,False

            if not 'bodyPart' in task.keys():
                print('missing key value "bodyPart"')
                Count+=1
            else:
                if type(task['bodyPart'])!=list:
                    print(f"value of key bodyPart shoud be a list, not {task['bodyPart']} with type {type(task['bodyPart'])}")
                    Count+=1
                else:
                    f1=True
                    for j,parts in enumerate(task['bodyPart']):
                        if type(parts)!=list:
                            print(f"bodyPart[{j}]: value in array bodyPart shoud be a list, not {parts} with type {type(parts)}")    
                            Count+=1
                        else:
                            for part in parts:
                                if not part in ["face","leftHand","rightHand","body"]:
                                    print(f"bodypart[{j}]: Unknown part {part}")
                                    Count+=1
                    
            if not 'poseFile' in task.keys():
                print('missing key value "poseFile"')
                Count+=1
            else:
                if type(task['poseFile'])!=list:
                    print(f"value of key poseFile shoud be a list, not {task['poseFile']} with type {type(task['poseFile'])}")
                    Count+=1
                else:
                    f2=True
                    for j,file in enumerate(task['poseFile']):
                        if type(file)!=str:
                            print(f"poseFile[{j}]: value in array poseFile shoud be a str, not {file} with type {type(file)}")
                            Count+=1
                        try:
                            with open(file, "r") as f:
                                points=json.loads(f.read())
                        except json.JSONDecodeError as err:
                            print(f"Invalid Json file {file}: {err}")
                            Count+=1
                        except OSError as err:
                            print(f"Can't read file {file}: {err}")
                            Count+=1
                        # TODO check points

            if not 'sensetive' in task.keys():
                print('missing key value "sensetive"')
                Count+=1
            else:
                if type(task['sensetive'])!=list:
                    print(f"value of key sensetive shoud be a list, not {task['sensetive']} with type {type(task['sensetive'])}")
                    Count+=1
                else:
                    f3=True
                    for j,num in enumerate(task['sensetive']):
                        if type(num)!=float and type(num)!=int:
                            print(f"sensetive[{j}]: value in array sensetive shoud be a float or int, not {num} with type {type(num)}")
                            Count+=1
            
            if not 'frames' in task.keys():
                print('missing key value "frames"')
                Count+=1
            else:
                if type(task['frames'])!=list:
                    print(f"value of key frames shoud be a list, not {task['frames']} with type {type(task['frames'])}")
                    Count+=1
                else:
                    f4=True
                    for j,num in enumerate(task['frames']):
                        if type(num)!=int:
                            print(f"frames[{j}]: value in array frames shoud be a int, not {num} with type {type(num)}")
                            Count+=1
            
            if f1 and f2 and f3 and f4:
                if not(len(task['poseFile'])==len(task['bodyPart']) and len(task['poseFile'])==len(task['sensetive'])and len(task['poseFile'])==len(task['frames'])):
                    print("len of poseFile, bodyPart, sensetive, frames unmatch")
                    Count+=1
        
        if task['type']=='detect':
            if not 'bodyPart' in task.keys():
                print('missing key value "bodyPart"')
                Count+=1
            else:
                if type(task['bodyPart'])!=list:
                    print(f"value of key bodyPart shoud be a list, not {task['bodyPart']} with type {type(task['bodyPart'])}")
                    Count+=1
                for j,part in enumerate(task['bodyPart']):
                    if not part in ["face","leftHand","rightHand","body"]:
                        print(f"bodyPart[{j}]: Unknown part {part}")
                        Count+=1
                    
            if not 'frames' in task.keys():
                print('missing key value "frames"')
                Count+=1
            else:
                if type(task['frames'])!=list:
                    print(f"value of key frames shoud be a list, not {task['frames']} with type {type(task['frames'])}")
                    Count+=1
                for j,num in enumerate(task['frames']):
                    if type(num)!=int:
                        print(f"frames[{j}]: value in array frames shoud be a int, not {num} with type {type(num)}")
                        Count+=1
        
        if task['type']=='timeout':
            if not 'timeout' in task.keys():
                print('missing key value "timeout"')
                Count+=1
            else:
                if type(task['timeout'])!=int:
                    print(f"value of key timeout shoud be a int, not {task['timeout']} with type {type(task['timeout'])}")
                    Count+=1
    print("="*30)
    print(f"Total: {Count} Errors")
    return Count==0

if __name__ == "__main__":
    data_dir = r".\data"
    if not os.path.exists(data_dir):
        print("folder not found")
        exit(0)
    if not os.path.exists(os.path.join(data_dir, "config.json")):
        print("file not found")
        exit(0)
    ValidateConfig(os.path.join(data_dir, "config.json"))

