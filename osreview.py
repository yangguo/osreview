import imp
import os, io, re
import ansible_runner
import streamlit as st

uploadfolder = 'output/'
playbookpath = 'playbook/'


def save_osfile(file_name, file_text):

    file_bytes = bytes(file_text, encoding="utf8")
    file_io = io.BytesIO(file_bytes)
    file_io.name = file_name + '.txt'
    # save file to upload folder if file not exists and not empty
    if (not os.path.exists(uploadfolder + file_io.name)) and file_text != '':
        with open(uploadfolder + file_io.name, 'wb') as f:
            f.write(file_bytes)
    # if not os.path.exists(uploadfolder + file_io.name):
    #     with open(os.path.join(uploadfolder, file_io.name), "wb") as f:
    #         f.write(file_io.getbuffer())


# read file text string from local
def read_file_text(file_path):
    # if file exists
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        return text
    else:
        return ''


# save file text string to local
def save_file_text(file_path, text):
    # save file to upload folder if file not exists
    if not os.path.exists(file_path):
        with open(file_path, 'w') as f:
            f.write(text)


# extract text by regex 
def extract_text_by_regex(text, regex):
    match = re.search(regex, text, re.MULTILINE)
    # print(match)
    if match:
        return match.group(1)
    else:
        return ''

# extract text by regex and return two groups
def extract_text_by_regex_two_groups(text, regex):
    match = re.search(regex, text, re.MULTILINE)
    # print(match)
    if match:
        return match.group(1), match.group(2)
    else:
        return '', ''

# extract all match by regex and return three group lists
def extract_text_by_regex_two_groups_all(text, regex):
    match = re.findall(regex, text, re.MULTILINE)
    # convert match to list
    group1ls = []
    group2ls = []
    group3ls = []
    for m in match:
        group1ls.append(m[0])
        group2ls.append(m[1])
        group3ls.append(m[2])
    return group1ls, group2ls, group3ls

# extract all match by regex and return list
def extract_text_by_regex_all(text, regex):
    match = re.findall(regex, text, re.MULTILINE)
    # convert match to list
    matchls = []
    for m in match:
        matchls.append(m)
    return matchls

# extract review files
def extract_review_files():
    outputtxt = read_file_text(uploadfolder + 'output.txt')
    osmotxt = read_file_text(uploadfolder + 'module.txt')
    keydirstxt = read_file_text(uploadfolder + 'keydirs.txt')
    worldwritabletxt = read_file_text(uploadfolder + 'worldwritable.txt')
    userfilestxt = read_file_text(uploadfolder + 'userfiles.txt')
    logstxt = read_file_text(uploadfolder + 'logs.txt')

    filels = [
        'SHADOW', 'PASSWD', 'GROUP', 'PROFILE', 'HOSTS']

    osmols = ['LOGIN.DEFS', 'AUTHCONFIG']

    cronls=['CRON.ALLOW','CRON.DENY','INETD.CONF','HOSTS.EQUIV','SYSLOG.CONF']

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

    # get var/spool/cron/
    regex=r'\[FILE\]: (.*)\n(.*/var/spool/cron.*)\n[=]{52}\n([\S\s]+?)[=]{52}'
    # extract text
    g1,g2,g3 = extract_text_by_regex_two_groups_all(outputtxt, regex)
    # combine text
    text = ''
    for i in range(len(g1)):
        text += g1[i] + '\n' + g2[i] + '\n' + g3[i] + '\n'
    filepath=uploadfolder + 'var-spool-cron.txt'
    save_file_text(filepath, text)
    namels.append('var-spool-cron')
    permoutputls.append('')
    fileoutputls.append(text)

    # get key directories
    regex=r'/:\n.*\n([\s\S]+?)[=]{52}'
    # extract text
    text = extract_text_by_regex(keydirstxt, regex)
    filepath=uploadfolder + 'keydirs.txt'
    save_file_text(filepath, text)
    namels.append('keydirs')
    permoutputls.append('')
    fileoutputls.append(text)

    # get world writable
    filepath=uploadfolder + 'worldwritable.txt'
    save_file_text(filepath, worldwritabletxt)
    namels.append('worldwritable')
    permoutputls.append('')
    fileoutputls.append(worldwritabletxt)

    # get os version
    regex=r"/bin/uname -a\n[=]{52}\n([\s\S]+?)[=]{52}"
    # extract text
    text = extract_text_by_regex(outputtxt, regex)
    filepath=uploadfolder + 'os-version.txt'
    save_file_text(filepath, text)
    namels.append('os-version')
    permoutputls.append('')
    fileoutputls.append(text)

    # get netrc
    regex=r"(.*.netrc .*)"
    # extract text
    textls = extract_text_by_regex_all(userfilestxt, regex)
    text = ''
    for t in textls:
        text += t + '\n'
    filepath=uploadfolder + 'netrc.txt'
    save_file_text(filepath, text)
    namels.append('netrc')
    permoutputls.append('')
    fileoutputls.append(text)

    # get rhosts
    regex=r"(.*.rhosts .*)"
    # extract text
    textls = extract_text_by_regex_all(userfilestxt, regex)
    text = ''
    for t in textls:
        text += t + '\n'
    filepath=uploadfolder + 'rhosts.txt'
    save_file_text(filepath, text)
    namels.append('rhosts')
    permoutputls.append('')
    fileoutputls.append(text)

    # get /etc/xinetd.d
    regex=r"\[FILE\]: (.*)\n(.*/etc/xinetd.d.*)\n[=]{52}\n([\S\s]+?)[=]{52}"
    # extract text
    g1,g2,g3 = extract_text_by_regex_two_groups_all(osmotxt, regex)
    # combine text
    text = ''
    for i in range(len(g1)):
        text += g1[i] + '\n' + g2[i] + '\n' + g3[i] + '\n'
    filepath=uploadfolder + 'xinetd.txt'
    save_file_text(filepath, text)
    namels.append('xinetd')
    permoutputls.append('')
    fileoutputls.append(text)

    # get netstat
    regex=r"CHECK_BEGIN: DO_NETSTAT_A\n[=]{52}\n\n([\s\S]+?)[=]{52}"
    # extract text
    text = extract_text_by_regex(outputtxt, regex)
    filepath=uploadfolder + 'netstat.txt'
    save_file_text(filepath, text)
    namels.append('netstat')
    permoutputls.append('')
    fileoutputls.append(text)

    # ge ten lines of login logs
    regex=r'Using: \/usr\/bin\/last.*\n[=]{52}\nLOGS_BEGIN: DO_LAST.*\n.*\n(.*\n.*\n.*\n.*\n.*\n.*\n.*\n.*\n.*\n.*)'
    # extract text
    text = extract_text_by_regex(logstxt, regex)
    filepath=uploadfolder + 'loginlogs.txt'
    save_file_text(filepath, text)
    namels.append('login_logs')
    permoutputls.append('')
    fileoutputls.append(text)

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

# delete all txt files in upload folder
def delete_all_txt_files():
    # delete all txt files
    for f in os.listdir(uploadfolder):
        if f.endswith('.txt'):
            os.remove(os.path.join(uploadfolder, f))
