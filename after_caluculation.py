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


def make_ub_value_list(ub_data, characters):
    physical_debuff_list = [0] * BATTLE_LENGTH
    magical_debuff_list = [0] * BATTLE_LENGTH
    debuff_value = []

    for i in characters:
        s1_value = np.array(db.s1_table[i]) * db.value_table[i][cd.S1][VALUE]
        s2_value = np.array(db.s2_table[i]) * db.value_table[i][cd.S2][VALUE]

        s1_int_value = s1_value.astype(int)
        s2_int_value = s2_value.astype(int)

        s1_type = db.value_table[i][cd.S1][VALUE_TYPE]
        s2_type = db.value_table[i][cd.S2][VALUE_TYPE]

        if s1_type == cd.PHYSICAL:
            physical_debuff_list += s1_int_value
        elif s1_type == cd.MAGICAL:
            magical_debuff_list += s1_int_value
        elif s1_type == cd.PHYSICAL_AND_MAGICAL:
            physical_debuff_list += s1_int_value
            magical_debuff_list += s1_int_value

        if s2_type == cd.PHYSICAL:
            physical_debuff_list += s2_int_value
        elif s2_type == cd.MAGICAL:
            magical_debuff_list += s2_int_value
        elif s2_type == cd.PHYSICAL_AND_MAGICAL:
            physical_debuff_list += s2_int_value
            magical_debuff_list += s2_int_value

    ub_count = range(len(ub_data))

    for i in ub_count:
        ub_time = ub_data[i][UB_TIMING_NUM]
        ub_start_time = BATTLE_LENGTH - ub_data[i][UB_TIMING_NUM]
        characters_num = ub_data[i][CHARACTER_NUM]
        ub_base_value = db.value_table[characters_num][cd.UB][VALUE]

        if ub_start_time < (BATTLE_LENGTH - 18):
            ub_value = np.array(db.ub_table[characters_num]) * ub_base_value
            ub_value = np.append([0] * ub_start_time, ub_value)
            ub_value = np.append(ub_value, [0] * (BATTLE_LENGTH - (ub_start_time + 18)))
        else:
            ub_value = np.array(db.ub_table[characters_num]) * ub_base_value
            ub_value = ub_value[:ub_time]
            ub_value = np.append([0] * ub_start_time, ub_value)

        ub_int_value = ub_value.astype(int)
        ub_value_type = cd.ub_type_table[characters_num]

        if 0 < ub_time <= 90:
            if ub_value_type is cd.PHYSICAL:
                debuff_value.append(str(int(physical_debuff_list[ub_start_time])))
            elif ub_value_type is cd.MAGICAL:
                debuff_value.append(str(int(magical_debuff_list[ub_start_time])))

            ub_type = db.value_table[characters_num][cd.UB][VALUE_TYPE]

            if ub_type == cd.PHYSICAL:
                physical_debuff_list = physical_debuff_list + ub_int_value
            elif ub_type == cd.MAGICAL:
                magical_debuff_list = magical_debuff_list + ub_int_value
            elif ub_type == cd.PHYSICAL_AND_MAGICAL:
                physical_debuff_list = physical_debuff_list + ub_int_value
                magical_debuff_list = magical_debuff_list + ub_int_value
        else:
            debuff_value.append("???")

    return debuff_value
