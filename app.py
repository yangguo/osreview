import streamlit as st
import pandas as pd
from osreview import save_osfile, extract_review_files,os_config_files_review

def main():

    # choose input method of manual or upload file
    input_method = st.sidebar.radio('选择输入方式', ('手动输入', '上传文件'))

    if input_method == '手动输入':
        output_text = st.text_area('主输出文件 包括：SHADOW/PASSWD/GROUP等')
        module_text = st.text_area('模块输出文件 包括：LOGIN.DEFS/CROND等')
        # save txt file as bytesio
        # if output_text != '' and module_text != '':
            # save button
        filesave = st.sidebar.button('开始配置检查')
        if filesave:
            # save file
            output_name = 'output'
            module_name = 'module'
            save_osfile(output_name, output_text)
            save_osfile(module_name, module_text)
            st.sidebar.success('文件保存成功')
        # extract button
        # extract = st.sidebar.button('提取配置信息')
        # if extract:
            namels, permoutputls, fileoutputls=extract_review_files()
            st.sidebar.success('提取配置信息成功')
            st.subheader('系统配置信息')
            # print extraction result
            for name, permoutput, fileoutput in zip(namels, permoutputls, fileoutputls):
                st.warning(name)
                st.write(permoutput)
                # display raw text
                st.text(fileoutput)

        # config_check_button = st.sidebar.button('检查配置')
        # if config_check_button:
            with st.spinner('检查配置中...'):
                # get playbook list from 1 to 15
                for i in range(1, 7):
                    # get playbook name
                    playbook_name = 'test' + str(i)+'.yaml'
                    # get playbook content
                    taskls,outputls,stats=os_config_files_review(playbook_name)
                    # st.write(taskls)
                    # st.write(outputls)
                    # st.write(stats)
                    # convert taskls and outputls to dataframe
                    resdf=pd.DataFrame({'task':taskls,'output':outputls})
                    # convert stats to dataframe
                    statdf=pd.DataFrame(stats)
                    st.subheader('检查结果'+str(i))
                    st.table(resdf)
                    st.subheader('检查统计'+str(i))
                    st.table(statdf)
                    # print success message
                    st.sidebar.success('检查完成'+str(i))
                    
        # else:
        #     st.error('请输入脚本运行输出内容')
  

if __name__ == '__main__':
    main()