#!/home/prilog/.pyenv/versions/3.6.9/bin/python
# -*- coding: utf-8 -*-
import characters as cd
import debuff as db
import numpy as np

# UB情報格納位置
UB_TIMING_NUM = 0
CHARACTER_NUM = 1

# 戦闘時間
BATTLE_LENGTH = 90

# valueリスト格納位置
VALUE = 0
VALUE_TYPE = 1

ub_data = [[76, 62], [64, 105], [61, 14], [58, 24], [52, 62], [51, 8], [47, 62], [43, 14], [41, 105], [32, 24], [27, 8], [27, 105], [24, 62], [14, 105], [1, 62], [1, 8], [1, 24]]
characters = [62, 105, 14, 24, 8]


#def make_ub_value_list(ub_data, characters):
physical_debuff_list = [0] * BATTLE_LENGTH
magical_debuff_list = [0] * BATTLE_LENGTH

for i in characters:
    s1_value = (np.array(db.s1_table[i]) * db.value_table[i][cd.S1][VALUE])
    s2_value = (np.array(db.s2_table[i]) * db.value_table[i][cd.S2][VALUE])

    s1_type = db.value_table[i][cd.S1][VALUE_TYPE]
    s2_type = db.value_table[i][cd.S2][VALUE_TYPE]
    
    if s1_type == cd.PHYSICAL:
        physical_debuff_list += s1_value
    elif s1_type == cd.MAGICAL:
        magical_debuff_list += s1_value
    elif s1_type == cd.PHYSICAL_AND_MAGICAL:
        physical_debuff_list += s1_value
        magical_debuff_list += s1_value

    if s2_type == cd.PHYSICAL:
        physical_debuff_list += s2_value
    elif s2_type == cd.MAGICAL:
        magical_debuff_list += s2_value
    elif s2_type == cd.PHYSICAL_AND_MAGICAL:
        physical_debuff_list += s2_value
        magical_debuff_list += s2_value


debuff_list = [physical_debuff_list, magical_debuff_list]

debuff_value = []
for i in range(len(ub_data)):
    ub_value_type = cd.ub_type_table[ub_data[i][CHARACTER_NUM]]
    ub_timing = BATTLE_LENGTH - ub_data[i][UB_TIMING_NUM]

    debuff_value.append(debuff_list[ub_value_type][ub_timing])
    print(debuff_list[ub_value_type][ub_timing])

print(debuff_value)
