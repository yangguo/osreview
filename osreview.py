import os, io, re
import ansible_runner

uploadfolder = 'output/'
playbookpath = 'playbook/'


def save_osfile(file_name, file_text):

    file_bytes = bytes(file_text, encoding="utf8")
    file_io = io.BytesIO(file_bytes)
    file_io.name = file_name + '.txt'

    with open(os.path.join(uploadfolder, file_io.name), "wb") as f:
        f.write(file_io.getbuffer())
    # return st.success("上传文件:{} 成功。".format(file_io.name))


# read file text string from local
def read_file_text(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


# save file text string to local
def save_file_text(file_path, text):
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(text)


# extract text by regex and return two groups
def extract_text_by_regex_two_groups(text, regex):
    match = re.search(regex, text, re.MULTILINE)
    # print(match)
    if match:
        return match.group(1), match.group(2)
    else:
        return 'None', 'None'


# extract review files
def extract_review_files():
    outputtxt = read_file_text(uploadfolder + 'output.txt')
    # print(fulltxt)

    osmotxt = read_file_text(uploadfolder + 'module.txt')

    filels = [
        'SHADOW', 'PASSWD', 'GROUP', 'PROFILE', 'HOSTS']

    osmols = ['LOGIN.DEFS', 'AUTHCONFIG']

    cronls=['CRON.ALLOW','CRON.DENY']

    namels=[]
    permoutputls = []
    fileoutputls = []
    # extract file text
    for filename in filels:
        # print(filename)
        regex = r'\[FILE\]: ' + filename + '\n(.+)\n^[=]{52}\n([\S\s]+?)[=]{52}'

        # extract text
        text, text2 = extract_text_by_regex_two_groups(outputtxt, regex)

        # print(text)
        # print(text2)
        # save text
        group1_file_path = uploadfolder + filename + '-perm.txt'
        group2_file_path = uploadfolder + filename + '-file.txt'
        save_file_text(group1_file_path, text)
        save_file_text(group2_file_path, text2)
        namels.append(filename)
        permoutputls.append(text)
        fileoutputls.append(text2)

    for osmodulename in osmols:
        # print(osmodulename)
        regex = r'\[FILE\]: ' + osmodulename + '\n(.+)\n^[=]{52}\n([\S\s]+?)[=]{52}'
        # extract text
        text, text2 = extract_text_by_regex_two_groups(osmotxt, regex)

        # print(text)
        # print(text2)
        # save text
        group1_file_path = uploadfolder + osmodulename + '-perm.txt'
        group2_file_path = uploadfolder + osmodulename + '-file.txt'
        save_file_text(group1_file_path, text)
        save_file_text(group2_file_path, text2)
        namels.append(osmodulename)
        permoutputls.append(text)
        fileoutputls.append(text2)

    for cronname in cronls:
        # print(cronname)
        regex = r'\[FILE\]: ' + cronname + '.*\n?(.*)\n[=]{52}\n?(.*)\n[=]{52}'
        # extract text
        text, text2 = extract_text_by_regex_two_groups(outputtxt, regex)

        # print(text)
        # print(text2)
        # save text
        group1_file_path = uploadfolder + cronname + '-perm.txt'
        group2_file_path = uploadfolder + cronname + '-file.txt'
        save_file_text(group1_file_path, text)
        save_file_text(group2_file_path, text2)
        namels.append(cronname)
        permoutputls.append(text)
        fileoutputls.append(text2)

    return namels, permoutputls, fileoutputls

# os config files review
def os_config_files_review(playbook):
    # run()
    taskls = []
    outputls = []
    r = ansible_runner.run(private_data_dir=playbookpath, playbook=playbook)
    # print("{}: {}".format(r.status, r.rc))
    # successful: 0
    for each_host_event in r.events:
        # print(each_host_event['event'])
        # print(each_host_event)
        # if each_host_event['event'] == 'playbook_on_task_start':
        if each_host_event['event'] == 'runner_on_ok':
            print(each_host_event['event_data']['task'])
            print(each_host_event['event_data']['res'])
            if each_host_event['event_data'][
                    'task'] != 'Gathering Facts' and each_host_event[
                        'event_data']['task'] != 'include_vars' :
                # print(each_host_event['event_data']['task'])
                taskls.append(each_host_event['event_data']['task'])
                if each_host_event[
                        'event_data']['task'] != 'debug':
                    # print(each_host_event['event_data']['res']['stdout_lines'])
                    outputstr = 'pass: ' + ' '.join(
                        each_host_event['event_data']['res']['stdout_lines'])
                    outputls.append(outputstr)
                else:
                    # print(each_host_event['event_data']['res']['msg'])
                    outputstr = 'debug: ' + each_host_event['event_data'][
                        'res']['msg']
                    outputls.append(outputstr)

        if each_host_event['event'] == 'runner_on_failed':
            # print(each_host_event['event_data']['task'])
            # print(each_host_event['event_data']['res']['stdout_lines'])
            taskls.append(each_host_event['event_data']['task'])
            outputstr = 'failed: ' + ' '.join(
                each_host_event['event_data']['res']['stdout_lines'])
            outputls.append(outputstr)
        # print(each_host_event['event_data'])
    # print("Final status:")
    # print(r.stats)
    return taskls, outputls, r.stats
