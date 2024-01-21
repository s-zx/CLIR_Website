# -*- coding: utf-8 -*-
# @Time    : 2024/1/18 14:54
# @Author  : 沈振兴
# @FileName: test.py
# @Software: PyCharm
line = '4   landscape'
last_query = line.strip()
print(last_query)
split = last_query.split("\t")
print(split)
last_index = int(last_query.split("\t")[0])

last_index