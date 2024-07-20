# -*- coding: utf-8 -*-
import pandas as pd
import os

import value_count as vc

import streamlit as st

st.title('故障代码检索')

script_dir = os.getcwd()
# st.write('当前工作目录是:', script_dir)

excel_file = os.path.join(script_dir, 'error_code_index.xlsx')


option = st.selectbox('请选择故障',('器械臂','持镜臂','控制台'))

X_test = st.text_input("请输入故障代码",'12-21 8:39/1/1/12/1;')


st.subheader('检索结果：')

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
    df_code1 = pd.read_excel(excel_file,'code1')
    df_code2 = pd.read_excel(excel_file,'code2')
    df_code3 = pd.read_excel(excel_file,'code3')
#read excel error
except Exception as e:
    st.write('Error!',e)


error_code_segerate = list(X_test) #转换为列表

search_item1 = '/' #分隔索引
search_item2 = ';'

item_index = [index for index, element in enumerate(error_code_segerate) if (element == search_item1) or (element == search_item2)]

try:

#故障信息提取
    error_mode     = error_code_segerate[item_index[0]+1]  #故障模式
    error_type     = error_code_segerate[item_index[1]+1:item_index[2]] #故障类型
    error_position = error_code_segerate[item_index[2]+1:item_index[3]] #故障位置
    error_code     = error_code_segerate[item_index[3]+1:item_index[4]] #故障代码


#类型转换，得到各部分对应十进制值
    mode_decimal_value     = int(error_mode)
    type_decimal_value     = vc.char_to_decimal(error_type, 10)
    position_decimal_value = vc.char_to_decimal(error_position, 10)
    code_decimal_value     = vc.char_to_decimal(error_code, 10)


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
        if 'x' not in position1_out:
            st.write('故障位置：',position1_out)
        else:
            st.write('故障位置码有误!')
    elif type_decimal_value == 14:
    #binary convert
        padded_position_list = [0] * padding_position_size + binary_position_list
        bit_value    = padded_position_list[0:4]
        bit_comment  = padded_position_list[5:]
        position_dec_value   = vc.char_to_decimal(bit_value, 2)
        position_dec_comment = vc.char_to_decimal(bit_comment, 2)
    #index output
        position2_indexes = df_position2['0x0E'].isin([position_dec_comment])
        if position2_indexes.any() == True and position_dec_value != 0:
            matched_position2 = df_position2.loc[position2_indexes,position_dec_value]
            position2_out = ''.join(matched_position2.apply(str))
            if position2_out != 'x':
                st.write('故障位置:',position2_out)
        else:
            
            st.write('故障位置编码有误')
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

        code1_indexes = df_code2['value'].isin([code_dec_value1])
        if code1_indexes.any() == True:
            matched_code1 = df_code2.loc[code1_indexes,1]
            code1_out = ''.join(matched_code1.apply(str))
            st.write('故障码信息:',code1_out)

        code_temp_list = padded_code_list[0:12]
        code_dec_value2 = vc.char_to_decimal(code_temp_list, 2)

        code2_indexes = df_code2['value'].isin([code_dec_value2])
        if code2_indexes.any() == True:
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
    st.write('故障代码或Excel文件有误！',e)


# st.error('This is an error')
