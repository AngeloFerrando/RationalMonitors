import random
import rational_multi_monitors
import os
import subprocess

Timeout = 300 # seconds

# Function to list all files in a folder and read each file
def list_and_read_traces(folder_path):
    # Check if the path is a directory
    if not os.path.isdir(folder_path):
        print(f"Error: {folder_path} is not a valid directory.")
        return
    
    # List all files in the directory
    files = os.listdir(folder_path)
    
    traces = []

    # Iterate through each file
    for file_name in files:
        # Construct the full path to the file
        file_path = os.path.join(folder_path, file_name)
        
        # Check if it's a file (not a directory)
        if os.path.isfile(file_path):
            try:
                # Open the file and read its contents
                with open(file_path, 'r') as file:
                    contents = file.read()
                    traces.append(contents)
            except Exception as e:
                print(f"Error reading {file_name}: {e}")
                print("-----------------------------")
    return traces

traces = list_and_read_traces('./traces/')
results = {}
with open('res.txt', 'w') as file:
    file.write('')
with open('tmp-res.txt', 'w') as tmp_res:
    results[f'metric0'] = {}
    results[f'metric1'] = {}
    with open('props.txt', 'r') as file:
        lines = file.readlines()
        for i in range(0, len(lines), 2):
            print(f'{float(i) / len(lines) * 100}%')
            line_0 = lines[i].split('$ ')
            line_1 = lines[i+1].split('$ ')
            # line_2 = lines[i+2].split('$ ')
            # line_3 = lines[i+3].split('$ ')
            for trace in traces:
                with open('tmp.txt', 'w') as file_t:
                    file_t.write(trace)
                try:
                    alphabet = set()
                    alphabet.update(set(line_0[1].replace('[', '').replace(']', '').split(',')))
                    alphabet.update(set(line_1[1].replace('[', '').replace(']', '').split(',')))
                    # alphabet.update(set(line_2[1].replace('[', '').replace(']', '').split(',')))
                    # alphabet.update(set(line_3[1].replace('[', '').replace(']', '').split(',')))
                    alphabet = set([a.replace(' ', '') for a in alphabet])
                    
                    alphabet_copy = alphabet.copy()
                    visibilites_l = []
                    visibilites_l.append(set(random.sample(list(alphabet_copy), int(len(alphabet_copy)/2))))
                    alphabet_copy.difference_update(visibilites_l[0])
                    visibilites_l[0] = '['+','.join(visibilites_l[0])+']'
                    visibilites_l.append(alphabet_copy)
                    visibilites_l[1] = '['+','.join(visibilites_l[1])+']'
                    visibility = ','.join(visibilites_l)

                    with open('tmp.txt', 'w') as file_t:
                        file_t.write(trace)

                    # Run the code
                    # print(' '.join(['python3', './main.py', line_0[0]+','+line_1[0], '['+','.join(alphabet)+']', visibility, '16', '10', 'tmp.txt' ]))
                    run_process = subprocess.run(['python3', './main.py', line_0[0]+','+line_1[0], '['+','.join(alphabet)+']', visibility, '16', '10', 'tmp.txt' ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=Timeout)
                    # print('code: ' + str(run_process.returncode))
                    res = run_process.stdout.decode()
                    # print(res)
                    verdict1 = res[res.index(':')+1:res.index('\n')].replace(' ', '')
                    verdict2 = res[res.index(':', res.index(':')+1)+1:res.index('\n', res.index('\n')+1)].replace(' ', '')
                    if verdict1 == 'Undefined' or verdict2 == 'Undefined':
                        verdict = 'Undefined'
                    else:
                        verdict = 'Defined'
                    # verdict = '('+verdict1+', '+verdict2+')'
                        # verdict = rational_monitor.main(['', line[0], line[1], line[2], line[3], line[4], '100000', 'tmp.txt', f'metric_{i}'])
                    if verdict not in results[f'metric0']:
                        results[f'metric0'][verdict] = 0
                    results[f'metric0'][verdict] += 1

                    run_process = subprocess.run(['python3', './main.py', line_0[0]+','+line_1[0], '['+','.join(alphabet)+']', visibility, '0', '10', 'tmp.txt' ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=Timeout)
                    # print('code: ' + str(run_process.returncode))
                    res = run_process.stdout.decode()
                    # print(res)
                    verdict1 = res[res.index(':')+1:res.index('\n')].replace(' ', '')
                    verdict2 = res[res.index(':', res.index(':')+1)+1:res.index('\n', res.index('\n')+1)].replace(' ', '')
                    if verdict1 == 'Undefined' or verdict2 == 'Undefined':
                        verdict = 'Undefined'
                    else:
                        verdict = 'Defined'
                    # verdict = '('+verdict1+', '+verdict2+')'
                        # verdict = rational_monitor.main(['', line[0], line[1], line[2], line[3], line[4], '100000', 'tmp.txt', f'metric_{i}'])
                    if verdict not in results[f'metric1']:
                        results[f'metric1'][verdict] = 0
                    results[f'metric1'][verdict] += 1
                except subprocess.TimeoutExpired:
                    break
                except Exception as e:
                    break
            tmp_res.write(str(results) + '\n')
    with open('res.txt', 'a') as file:
        file.write(f'metric0' + str(results[f'metric0']))
        file.write(f'metric1' + str(results[f'metric1']))
        file.write('\n')
print(results)