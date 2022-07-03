import imp
import os

import pandas as pd
import streamlit as st
from PIL import Image
from streamlit_cropper import st_cropper

from osreview import (
    delete_all_txt_files,
    extract_review_files,
    os_config_files_review,
    paddleocr2text,
    save_osfile,
)

# print_processor = TrOCRProcessor.from_pretrained('microsoft/trocr-base-printed')
# print_model = VisionEncoderDecoderModel.from_pretrained('microsoft/trocr-base-printed')

picfilelist = [
    "PASSWD-perm",
    "PASSWD-file",
    "SHADOW-perm",
    "SHADOW-file",
    "LOGIN.DEFS-file",
    "CRON.ALLOW-perm",
    "CRON.ALLOW-file",
    "CRON.DENY-perm",
    "CRON.DENY-file",
    "var-spool-cron",
    "keydirs",
    "worldwritable",
    "os-version",
    "INETD.CONF-file",
    "HOSTS.EQUIV-file",
    "netrc",
    "rhosts",
    "xinetd",
    "netstat",
    "SYSLOG.CONF-file",
    "loginlogs",
    "GROUP-perm",
    "GROUP-file",
]

uploadfolder = "output/"

# def show_image(url):
#   img = Image.open(url).convert("RGB")
#   #display(img)
#   inverted_image = ImageOps.invert(img)
#   return inverted_image


# def ocr_print_image(src_img):
# #   src_img = show_image(img_path)
#   pixel_values = print_processor(images=src_img, return_tensors="pt").pixel_values
#   generated_ids = print_model.generate(pixel_values)
#   return print_processor.batch_decode(generated_ids, skip_special_tokens=True)[0]


# def ocr2text(img):
#     # img = Image.open(img_path)
#     # add config
#     config = r'--oem 3 --psm 4 -l eng+chi_sim'
#     text = pytesseract.image_to_string(img, config=config)
#     return text


def main():

    # choose input method of manual or upload file or camera
    input_method = st.sidebar.selectbox("选择输入方式", ["脚本结果", "手动输入", "图片识别"])

    if input_method == "脚本结果":
        # upload method
        script_method = st.sidebar.radio("选择脚本结果", ["上传文件", "输入文本"])
        if script_method == "上传文件":
            # upload file
            uploaded_file = st.file_uploader("上传文件")

            # choose file using dropdown
            file_name = st.sidebar.selectbox(
                "选择文件类型",
                ("output", "module", "keydirs", "worldwritable", "userfiles", "logs"),
            )

            if uploaded_file is not None:
                # save button
                filesave = st.sidebar.button("文件保存")
                if filesave:
                    # read file
                    file_text = uploaded_file.read().decode("utf-8")
                    save_osfile(file_name, file_text)
                    st.success("文件保存成功")
            else:
                st.error("请选择文件")
        elif script_method == "输入文本":
            output_text = st.text_area("主输出文件 包括：SHADOW/PASSWD/GROUP等")
            module_text = st.text_area("模块输出文件 包括：LOGIN.DEFS/CROND等")
            keydirs_text = st.text_area("主要目录文件 包括：/bin/dev/etc/usr/var等")
            worldwritable_text = st.text_area("全局可写目录 包括：rw等")
            userfiles_text = st.text_area("用户文件 包括：/rhosts/netrc/profile等")
            logs_text = st.text_area("日志文件 包括：/var/log/messages/secure等")
            # save button
            filesave = st.sidebar.button("文件保存")
            if filesave:
                # save file
                output_name = "output"
                module_name = "module"
                keydirs_name = "keydirs"
                worldwritable_name = "worldwritable"
                userfiles_name = "userfiles"
                logs_name = "logs"
                save_osfile(output_name, output_text)
                save_osfile(module_name, module_text)
                save_osfile(keydirs_name, keydirs_text)
                save_osfile(worldwritable_name, worldwritable_text)
                save_osfile(userfiles_name, userfiles_text)
                save_osfile(logs_name, logs_text)
                st.sidebar.success("文件保存成功")

    elif input_method == "手动输入":
        save_text = st.text_area("文本内容")

        # choose file using dropdown
        file_name = st.sidebar.selectbox("选择文件类型", picfilelist)

        # save button
        filesave = st.sidebar.button("文件保存")
        if filesave:
            # save file
            save_osfile(file_name, save_text)
            st.success("文件保存成功: " + file_name)

    elif input_method == "图片识别":
        # crop image parameter
        realtime_update = st.sidebar.checkbox(label="是否实时更新", value=True)
        box_color = st.sidebar.color_picker(label="选框颜色", value="#0000FF")
        # aspect_choice = st.sidebar.radio(label="Aspect Ratio", options=["1:1", "16:9", "4:3", "2:3", "Free"])
        # aspect_dict = {
        #     "1:1": (1, 1),
        #     "16:9": (16, 9),
        #     "4:3": (4, 3),
        #     "2:3": (2, 3),
        #     "Free": None
        # }
        # aspect_ratio = aspect_dict[aspect_choice]
        aspect_ratio = None

        # choose upload file or camera
        upload_method = st.sidebar.radio("选择输入方式", ["文件上传", "摄像头"])

        if upload_method == "文件上传":
            # upload file
            img_file = st.file_uploader("上传图片", type=["png", "jpg", "jpeg"])
        elif upload_method == "摄像头":
            img_file = st.camera_input("请拍摄照片")

        if img_file is None:
            st.error("请选择文件进行识别")
            return
        else:
            # crop image
            img = Image.open(img_file)
            if not realtime_update:
                st.write("双击保存裁剪图片")
            # Get a cropped image from the frontend
            cropped_img = st_cropper(
                img,
                realtime_update=realtime_update,
                box_color=box_color,
                aspect_ratio=aspect_ratio,
            )

            # Manipulate cropped image at will
            st.write("预览图片")
            # _ = cropped_img.thumbnail((150,150))
            st.image(cropped_img, use_column_width=True)

        # ocr button
        ocr_button = st.sidebar.button("图片识别")
        if ocr_button:
            # save cropped_img as temp file
            temp_img = os.path.join(uploadfolder, "temp.png")
            cropped_img.save(temp_img)

            # read file and convert to text
            file_text = paddleocr2text(temp_img)
            st.sidebar.success("图片识别成功")
        else:
            st.error("请点击图片识别")
            file_text = ""

        save_text = st.text_area("文本内容", file_text)

        # choose file using dropdown
        file_name = st.sidebar.selectbox("选择文件类型", picfilelist)

        # save button
        filesave = st.sidebar.button("文件保存")
        if filesave:
            # save file
            save_osfile(file_name, save_text)
            st.success("文件保存成功: " + file_name)

    # # config file extraction button
    # config_extract = st.sidebar.button('配置文件解析')
    # if config_extract:

    config_review = st.sidebar.button("配置文件检查")
    if config_review:
        namels, permoutputls, fileoutputls = extract_review_files()
        st.sidebar.success("提取配置信息成功")
        st.subheader("系统配置信息")
        # print extraction result
        for name, permoutput, fileoutput in zip(namels, permoutputls, fileoutputls):
            st.warning(name)
            st.write(permoutput)
            # display raw text
            st.text(fileoutput)

        # get full result
        resls = []
        with st.spinner("检查配置中..."):
            # get playbook list from 1 to 15
            for i in range(1, 16):
                # get playbook name
                playbook_name = "test" + str(i) + ".yaml"
                # get playbook content
                taskls, outputls, stats = os_config_files_review(playbook_name)
                # st.write(taskls)
                # st.write(outputls)
                # st.write(stats)
                testname = "test" + str(i)
                # convert taskls and outputls to dataframe
                resdf = pd.DataFrame(
                    {"name": testname, "task": taskls, "output": outputls}
                )
                # convert stats to dataframe
                statdf = pd.DataFrame(stats)
                st.subheader("检查结果" + str(i))
                st.table(resdf)
                resls.append(resdf)
                # display raw text
                # for task,output in zip(taskls,outputls):
                #     st.info(task)
                #     st.markdown(output, unsafe_allow_html=True)
                # st.subheader('检查统计'+str(i))
                # st.table(statdf)
                # print success message
                st.sidebar.success("检查完成" + str(i))
        # combine all dataframe
        alldf = pd.concat(resls)
        # download csv file
        st.subheader("检查结果")
        st.download_button(
            data=alldf.to_csv(index=False), label="下载检查结果", file_name="osreview.csv"
        )

        # delete all txt files
        delete_all_txt_files()


if __name__ == "__main__":
    main()
