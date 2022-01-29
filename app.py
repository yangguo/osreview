from cProfile import label
import streamlit as st
import pandas as pd
from osreview import save_osfile, extract_review_files,os_config_files_review

def main():

    # choose input method of manual or upload file
    input_method = st.sidebar.radio('选择输入方式', ('手动输入', '上传文件'))

    if input_method == '手动输入':
        output_text = st.text_area('主输出文件 包括：SHADOW/PASSWD/GROUP等')
        module_text = st.text_area('模块输出文件 包括：LOGIN.DEFS/CROND等')
        keydirs_text=st.text_area('主要目录文件 包括：/bin/dev/etc/usr/var等')
        worldwritable_text=st.text_area('全局可写目录 包括：rw等')
        userfiles_text=st.text_area('用户文件 包括：/rhosts/netrc/profile等')
        logs_text=st.text_area('日志文件 包括：/var/log/messages/secure等')
        # save button
        filesave = st.sidebar.button('开始配置检查')
        if filesave:
            # save file
            output_name = 'output'
            module_name = 'module'
            keydirs_name = 'keydirs'
            worldwritable_name = 'worldwritable'
            userfiles_name = 'userfiles'
            logs_name = 'logs'
            save_osfile(output_name, output_text)
            save_osfile(module_name, module_text)
            save_osfile(keydirs_name, keydirs_text)
            save_osfile(worldwritable_name, worldwritable_text)
            save_osfile(userfiles_name, userfiles_text)
            save_osfile(logs_name, logs_text)
            st.sidebar.success('文件保存成功')

            namels, permoutputls, fileoutputls=extract_review_files()
            st.sidebar.success('提取配置信息成功')
            st.subheader('系统配置信息')
            # print extraction result
            for name, permoutput, fileoutput in zip(namels, permoutputls, fileoutputls):
                st.warning(name)
                st.write(permoutput)
                # display raw text
                st.text(fileoutput)

            # get full result
            resls=[]
            with st.spinner('检查配置中...'):
                # get playbook list from 1 to 15
                for i in range(1, 16):
                    # get playbook name
                    playbook_name = 'test' + str(i)+'.yaml'
                    # get playbook content
                    taskls,outputls,stats=os_config_files_review(playbook_name)
                    # st.write(taskls)
                    # st.write(outputls)
                    # st.write(stats)
                    testname='test'+str(i)
                    # convert taskls and outputls to dataframe
                    resdf=pd.DataFrame({'name':testname,'task':taskls,'output':outputls})
                    # convert stats to dataframe
                    statdf=pd.DataFrame(stats)
                    st.subheader('检查结果'+str(i))
                    st.table(resdf)
                    resls.append(resdf)
                    # display raw text
                    # for task,output in zip(taskls,outputls):
                    #     st.info(task)
                    #     st.markdown(output, unsafe_allow_html=True)
                    # st.subheader('检查统计'+str(i))
                    # st.table(statdf)
                    # print success message
                    st.sidebar.success('检查完成'+str(i))
            # combine all dataframe
            alldf=pd.concat(resls)
            # download csv file
            st.subheader('检查结果')
            st.download_button(data=alldf.to_csv(index=False),label='下载检查结果',file_name='osreview.csv')
  

if __name__ == '__main__':
    main()