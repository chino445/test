# -*- coding: utf-8 -*-
"""
Created on Thu Jul 18 10:45:55 2024

@author: 15273
"""

def char_to_decimal(convert_list,binary):
    int_list = [int(digit) for digit in convert_list]
    decimal_value = 0
    for i, digit in enumerate(int_list):
        # 计算当前位的权重（10的幂）
        power = len(int_list) - 1 - i
        # 累加到最终的数值
        decimal_value += digit * (binary ** power) #类型转换，得到故障类型
    return decimal_value