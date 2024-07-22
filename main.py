# -*- coding: utf-8 -*-
import pandas as pd
import os

import value_count as vc

import streamlit as st

from PIL import Image

st.title('故障代码检索')

script_dir = os.getcwd()
# st.write('当前工作目录是:', script_dir)

excel_file = os.path.join(script_dir, 'error_code_index.xlsx')

option = st.selectbox('请选择故障位置',('器械臂','持镜臂','控制台'))

option_mode = st.selectbox('请选择输入方式',('查看检索方式','全段输入','分段输入'))


# 使用pandas读取Excel文件
try:
    df_mode = pd.read_excel(excel_file,'mode')
    df_type = pd.read_excel(excel_file,'type')
#arm select
    if(option == '器械臂'):
        df_position1 = pd.read_excel(excel_file,'position_arm')
    elif(option == '持镜臂'):
        df_position1 = pd.read_excel(excel_file,'position_scope')
    else:
        df_position1 = pd.read_excel(excel_file,'position_console')
#position/code read
    df_position2 = pd.read_excel(excel_file,'position2')
    df_position2_name = pd.read_excel(excel_file,'position2_name')
    df_code1 = pd.read_excel(excel_file,'code1')
    df_code2 = pd.read_excel(excel_file,'code2')
    df_code3 = pd.read_excel(excel_file,'code3')
#read excel error
except Exception as e:
    st.write('Error!',e)


X_test = ' '
error_count = 0
errorinput_flag = False 

if(option_mode == '查看检索方式'):
    st.write('全段输入：将故障代码直接粘贴至输入框中，注意以英文分号 ";" 结尾')
    st.write('分段输入：依次输入故障模式、故障类型、故障位置、故障码') 
    st.write('其中，故障代码的组成如下所示')
    image1 = Image.open('errorcode1.png')
    st.image(image1, 
         width = 600
         )
    image2 = Image.open('errorcode2.png')
    st.image(image2,
         width = 600
         )    
elif(option_mode == '全段输入'):
    X_test = st.text_input("请在下方粘贴故障代码，如：12-21 8:39/2/1/12/1;",value =' ')
else:
    error_mode = st.number_input(label = '请输入故障模式',value=0,step=1)
    error_type = st.number_input(label = '请输入故障类型',value=0,step=1)
    error_position = st.number_input(label = '请输入故障位置',value=0,step=1)
    error_code = st.number_input(label = '请输入故障码',value=0,step=1)
    if any(x<0 for x in (error_mode,error_type,error_position,error_code)):
        error_count = 0
    else:
        error_count = sum((error_mode,error_type,error_position,error_code))


if(option_mode == '全段输入' and X_test != ' '):
    error_code_segerate = list(X_test) #转换为列表

    search_item1 = '/' #分隔索引
    search_item2 = ';'

    item_index = [index for index, element in enumerate(error_code_segerate) if (element == search_item1) or (element == search_item2)]
    
    try:
        #故障信息提取
        error_mode     = error_code_segerate[item_index[0]+1:item_index[1]]  #故障模式
        error_type     = error_code_segerate[item_index[1]+1:item_index[2]] #故障类型
        error_position = error_code_segerate[item_index[2]+1:item_index[3]] #故障位置
        error_code     = error_code_segerate[item_index[3]+1:item_index[4]] #故障代码


        #类型转换，得到各部分对应十进制值
        mode_decimal_value     = vc.char_to_decimal(error_mode, 10)
        type_decimal_value     = vc.char_to_decimal(error_type, 10)
        position_decimal_value = vc.char_to_decimal(error_position, 10)
        code_decimal_value     = vc.char_to_decimal(error_code, 10)
        
        errorinput_flag = True
        
    except Exception:
        st.write('您的输入格式有误!') 
        
elif(option_mode == '分段输入' and error_count > 0): 
    mode_decimal_value = int(error_mode)
    type_decimal_value = int(error_type)
    position_decimal_value = int(error_position)
    code_decimal_value = int(error_code)
    
    errorinput_flag = True
    
else:
    errorinput_flag = False

#检索输出
if(errorinput_flag == True):
    try:
    #当前模式检索输出
        mode_indexes = df_mode['value'].isin([mode_decimal_value])
        if mode_indexes.any() == True:
            matched_mode = df_mode.loc[mode_indexes, 'significance']
            mode_out = ''.join(matched_mode.apply(str))
            st.write('当前模式为:',mode_out)
        else:
            st.write('当前模式不存在，请检查故障代码或联系管理人员')


    #当前故障类型输出
        type_indexes = df_type['type'].isin([type_decimal_value])
        if type_indexes.any() == True:
            matched_type = df_type.loc[type_indexes, 'significance']
            type_out = ''.join(matched_type.apply(str))
            st.write('当前故障类型为:',type_out)
        else:
            st.write('当前故障类型不存在，请检查故障代码或联系管理人员')

        position_flag = type_decimal_value in df_position1.columns

        binary_position_temp = bin(position_decimal_value)[2:]
        binary_position_list = [int(digit) for digit in binary_position_temp]
        padding_position_size = 16 - len(binary_position_list)


    #故障位置输出
        if position_flag == True:
        #binary pad   
            position1_out = ''
            padded_position_list = [0] * padding_position_size + binary_position_list
            index_position_print = [index for index, value in enumerate(reversed(padded_position_list)) if value == 1]
            position_out = df_position1.iloc[index_position_print]
            #打印输出
            for item in position_out[type_decimal_value]:
                position1_out = position1_out + item + ' '
            if position1_out.strip() == '':
                st.write(' ')
            elif 'x' not in position1_out:
                st.write('故障位置：',position1_out)
            else:
                st.write('故障位置有误!')
        elif type_decimal_value == 14:
        #binary convert
            padded_position_list = [0] * padding_position_size + binary_position_list
            bit_value    = padded_position_list[0:4]
            bit_comment  = padded_position_list[5:]
            position_dec_value   = vc.char_to_decimal(bit_value, 2)
            position_dec_comment = vc.char_to_decimal(bit_comment, 2)
        #index output

            position2_name_indexes = df_position2_name['value'].isin([position_dec_value])
            if position2_name_indexes.any() == True:
                matched_name = df_position2_name.loc[position2_name_indexes, 'significance']
                name_out = ''.join(matched_name.apply(str))
   
                position2_indexes = df_position2['0x0E'].isin([position_dec_comment])
                if position2_indexes.any() == True:
                    matched_position2 = df_position2.loc[position2_indexes,position_dec_value]
                    position2_out = ''.join(matched_position2.apply(str))
                    if position2_out != 'x':
                        st.write('故障位置:',name_out + ' — ' + position2_out)
                else:
                    st.write('故障位置有误!')
            elif position_dec_value == 0:
                st.write(' ')
            else:
                st.write('故障位置有误!')            
        else:
            st.write(' ')


    #故障代码输出
        code_flag = type_decimal_value in df_code1.columns
        if code_flag == True:
        #binary
            code1_indexes = df_code1['code'].isin([code_decimal_value])
            matched_code1 = df_code1.loc[code1_indexes,type_decimal_value]
            code1_out = ''.join(matched_code1.apply(str))
            if code1_indexes.any() == True:
                if code1_out != 'x':
                    st.write('故障码信息:',code1_out)

        elif type_decimal_value == 1:

            binary_code_temp = bin(code_decimal_value)[2:]  # 去掉前缀'0b'
            binary_code_list = [int(digit) for digit in binary_code_temp]
            padding_code_size = 16 - len(binary_code_list)
            padded_code_list = [0] * padding_code_size + binary_code_list

            code_temp_list = padded_code_list[12:16]
            code_dec_value1 = vc.char_to_decimal(code_temp_list, 2)

            code_temp_list = padded_code_list[0:12]
            code_dec_value2 = vc.char_to_decimal(code_temp_list, 2)
 
            code1_indexes = df_code2['value'].isin([code_dec_value1])
            code2_indexes = df_code2['value'].isin([code_dec_value2])
          
            if code1_indexes.any() == True and (code2_indexes.any() == True or code_dec_value2 == 0):
                matched_code1 = df_code2.loc[code1_indexes,1]
                code1_out = ''.join(matched_code1.apply(str))
                st.write('故障码信息:',code1_out)

            if code2_indexes.any() == True and (code1_indexes.any() == True or code_dec_value1 == 0):
                matched_code2 = df_code2.loc[code2_indexes,2]
                code2_out = ''.join(matched_code2.apply(str))
                st.write('故障码信息:',code2_out)

        elif type_decimal_value == 6:
            if len(binary_position_list) < 6:
                padding_code_size = 6 - len(binary_position_list)
                padded_code_list = [0] * padding_code_size + binary_position_list
                index_code_print = [index for index, value in enumerate(padded_code_list) if value == 1]
                code3_indexes_column = 5 - index_code_print[0] # 5:max len - 1,reversed

                code3_indexes = df_code3['0x06'].isin([code_decimal_value])
                if code3_indexes.any() == True:
                    matched_code3 = df_code3.loc[code3_indexes,code3_indexes_column]
                    code3_out = ''.join(matched_code3.apply(str))
                    if code3_out != 'x':
                        st.write('故障码信息:',code3_out)
                else:
                    st.write(' ')
            else:
                st.write(' ')
        else:
            st.write(' ')    

    except Exception as e:
        st.write('故障代码输入有误！',e)


