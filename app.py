import streamlit as st
import pandas as pd
import pytesseract
from PIL import Image,ImageOps
import numpy as np
import os
from osreview import save_osfile, extract_review_files, os_config_files_review, delete_all_txt_files

from transformers import OPENAI_GPT_PRETRAINED_CONFIG_ARCHIVE_MAP, TrOCRProcessor, VisionEncoderDecoderModel
import cv2

def img2contour(img):
    # img = cv2.imread(img_path)
 
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, img = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    img = cv2.bitwise_not(img)

    cnts, hierarchy = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # sort the cnts bigger width first
    # cnts = sorted(cnts, key=cv2.contourArea, reverse=True)
    cnts=sorted(cnts,key=lambda c: cv2.boundingRect(c)[2], reverse=True)

    return cnts



## install PyTesseract
# os.system('sudo apt-get install tesseract-ocr')

# print_processor = TrOCRProcessor.from_pretrained('microsoft/trocr-base-printed')
# print_model = VisionEncoderDecoderModel.from_pretrained('microsoft/trocr-base-printed')

picfilelist = [
    'PASSWD-perm',
    'PASSWD-file',
    'SHADOW-perm',
    'SHADOW-file',
    'LOGIN.DEFS-file',
    'CRON.ALLOW-perm',
    'CRON.ALLOW-file',
    'CRON.DENY-perm',
    'CRON.DENY-file',
    'var-spool-cron',
    'keydirs',
    'worldwritable',
    'os-version',
    'INETD.CONF-file',
    'HOSTS.EQUIV-file',
    'netrc',
    'rhosts',
    'xinetd',
    'netstat',
    'SYSLOG.CONF-file',
    'loginlogs',
    'GROUP-perm',
    'GROUP-file',
]

def show_image(url):
  img = Image.open(url).convert("RGB")
  #display(img)
  inverted_image = ImageOps.invert(img)
  return inverted_image 
  

# def ocr_print_image(src_img):
# #   src_img = show_image(img_path)
#   pixel_values = print_processor(images=src_img, return_tensors="pt").pixel_values
#   generated_ids = print_model.generate(pixel_values)
#   return print_processor.batch_decode(generated_ids, skip_special_tokens=True)[0]


def ocr2text(img_path):
    img = Image.open(img_path)
    # add config
    config = r'--oem 3 --psm 4 -l eng+chi_sim'
    text = pytesseract.image_to_string(img, config=config)
    return text


def main():

    # choose input method of manual or upload file or camera
    input_method = st.sidebar.selectbox('选择输入方式',
                                        ['手动输入', '文件上传', '图片识别', '摄像头'])

    if input_method == '手动输入':
        output_text = st.text_area('主输出文件 包括：SHADOW/PASSWD/GROUP等')
        module_text = st.text_area('模块输出文件 包括：LOGIN.DEFS/CROND等')
        keydirs_text = st.text_area('主要目录文件 包括：/bin/dev/etc/usr/var等')
        worldwritable_text = st.text_area('全局可写目录 包括：rw等')
        userfiles_text = st.text_area('用户文件 包括：/rhosts/netrc/profile等')
        logs_text = st.text_area('日志文件 包括：/var/log/messages/secure等')
        # save button
        filesave = st.sidebar.button('文件保存')
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

    elif input_method == '文件上传':
        # upload file
        uploaded_file = st.file_uploader("上传文件")

        # choose file using dropdown
        file_name = st.sidebar.selectbox(
            '选择文件类型', ('output', 'module', 'keydirs', 'worldwritable',
                       'userfiles', 'logs'))

        if uploaded_file is not None:
            # save button
            filesave = st.sidebar.button('文件保存')
            if filesave:
                # read file
                file_text = uploaded_file.read().decode("utf-8")
                save_osfile(file_name, file_text)
                st.success('文件保存成功')
        else:
            st.error('请选择文件')

    elif input_method == '图片识别':
        # upload file
        uploaded_file = st.file_uploader("上传图片")
        if uploaded_file is not None:
            # display image
            st.image(uploaded_file, use_column_width=True)
            # read file and convert to text
            file_text = ocr2text(uploaded_file)
            # inverted_image=show_image(uploaded_file)
            # st.image(inverted_image)
            # bytes_data = uploaded_file.getvalue()
            # cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
            # st.image(cv2_img)
            # inverte the image
            # inverted_image = cv2.bitwise_not(cv2_img)
            # st.image(inverted_image)
            # st.image(~cv2_img)
            # Creating a copy of image
            # im2 = inverted_image.copy()
            # contours=img2contour(im2)
            
            # get the 2 big lines
            # lines = [cv2.boundingRect(contours[0]), cv2.boundingRect(contours[1])]
            # higher line first
            # lines.sort(key=lambda c: c[1])
            # croping the img
            # crop_img = im2[lines[0][1]:lines[1][1]]
            # st.image(crop_img)


            # txtls=[]
            # show contours
            # for i,cnt in enumerate(contours):

            #     # get the 2 big lines
            #     lines = [cv2.boundingRect(contours[i]), cv2.boundingRect(contours[i+1])]
            #     # higher line first
            #     lines.sort(key=lambda c: c[1])
            #     # croping the img
            #     crop_img = im2[lines[0][1]:lines[1][1]]
            #     st.image(crop_img)
              
            #     # st.image(cropped)
            #     # txt=ocr_print_image(cropped)
            #     txt=str(crop_img)
            #     # st.text(txt)
            #     txtls.append(txt)

            # file_text= ocr_print_image(uploaded_file)
            # file_text = '\n'.join(txtls)
        else:
            st.error('请选择文件进行识别或手工输入')
            file_text = ''

        save_text = st.text_area('文件内容', file_text)

        # choose file using dropdown
        file_name = st.sidebar.selectbox('选择文件类型', picfilelist)

        # save button
        filesave = st.sidebar.button('文件保存')
        if filesave:
            # save file
            save_osfile(file_name, save_text)
            st.success('文件保存成功: ' + file_name)

    elif input_method == '摄像头':
        # open camera and take picture
        picture = st.camera_input("请拍摄照片")

        # choose file using dropdown
        file_name = st.sidebar.selectbox('选择文件类型', picfilelist)

        if picture is not None:
            st.image(picture)
            # ocr the picture using tesseract
            ocr_text = ocr2text(picture)
            # ocr_text = ocr_print_image(picture)
            st.text(ocr_text)
            # save button
            filesave = st.sidebar.button('文件保存')
            if filesave:
                # save file
                save_osfile(file_name, ocr_text)
                st.success('文件保存成功: ' + file_name)
        else:
            st.error('请拍摄照片')

    # # config file extraction button
    # config_extract = st.sidebar.button('配置文件解析')
    # if config_extract:

    config_review = st.sidebar.button('配置文件检查')
    if config_review:
        namels, permoutputls, fileoutputls = extract_review_files()
        st.sidebar.success('提取配置信息成功')
        st.subheader('系统配置信息')
        # print extraction result
        for name, permoutput, fileoutput in zip(namels, permoutputls,
                                                fileoutputls):
            st.warning(name)
            st.write(permoutput)
            # display raw text
            st.text(fileoutput)

        # get full result
        resls = []
        with st.spinner('检查配置中...'):
            # get playbook list from 1 to 15
            for i in range(1, 16):
                # get playbook name
                playbook_name = 'test' + str(i) + '.yaml'
                # get playbook content
                taskls, outputls, stats = os_config_files_review(playbook_name)
                # st.write(taskls)
                # st.write(outputls)
                # st.write(stats)
                testname = 'test' + str(i)
                # convert taskls and outputls to dataframe
                resdf = pd.DataFrame({
                    'name': testname,
                    'task': taskls,
                    'output': outputls
                })
                # convert stats to dataframe
                statdf = pd.DataFrame(stats)
                st.subheader('检查结果' + str(i))
                st.table(resdf)
                resls.append(resdf)
                # display raw text
                # for task,output in zip(taskls,outputls):
                #     st.info(task)
                #     st.markdown(output, unsafe_allow_html=True)
                # st.subheader('检查统计'+str(i))
                # st.table(statdf)
                # print success message
                st.sidebar.success('检查完成' + str(i))
        # combine all dataframe
        alldf = pd.concat(resls)
        # download csv file
        st.subheader('检查结果')
        st.download_button(data=alldf.to_csv(index=False),
                           label='下载检查结果',
                           file_name='osreview.csv')

        # delete all txt files
        delete_all_txt_files()


if __name__ == '__main__':
    main()