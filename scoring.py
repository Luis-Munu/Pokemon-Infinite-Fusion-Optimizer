from numpy import array, nan, stack, str_, sum

from config import type_info


def calculate_multiplier(type, value, split=0):
    split_b = type_info["physical_boost"] if split == 0 else type_info["special_boost"]
    if type in type_info["boosted_types"]:
        return value * type_info["boost"] * split_b
    elif type in type_info["nerfed_types"]:
        return value * type_info["nerf"] * split_b
    return value * split_b


def get_defensive_score(type1, type2):
    types = [type1, int(type2)] if not type(type2) == str_ else [type1]
    score = 0
    for attacking_type, value in type_info["type_chart"].items():
        local_scores = [
            0 if type(value[defending_type]) == float or abs(value[defending_type]) < 2 else value[defending_type]
            for defending_type in types
        ]
        if 4 in local_scores or -4 in local_scores:
            score += 4
        elif not (sum(local_scores) == 0):
            score += -sum([
                calculate_multiplier(attacking_type, score, 0)
                if attacking_type in type_info["physical_types"] else calculate_multiplier(attacking_type, score, 1)
                for score in local_scores
            ])
    return score


def get_offensive_score(type1, type2):

    def eval_type(offensive_type):
        return sum([
            calculate_multiplier(defending_type, value) if type(value) != str_ and value != 0 else -4
            for defending_type, value in type_info["type_chart"][offensive_type].items()
        ])

    return eval_type(type1) + eval_type(type2) if type(type2) != str_ else eval_type(type1)


def determine_fusion_types(types1, types2):
    types = []
    for i in range(len(types1)):
        type1_1, type1_2 = types1[i]
        type2_1, type2_2 = types2[i]
        if type(type1_2) == float:
            type1_2 = type1_1
        if type(type2_2) == float:
            type2_2 = type2_1

        if type1_1 == type2_2:
            type2_2 = nan
        if type2_1 == type1_2:
            type1_2 = nan

        types.append([[type1_1, type2_2], [type2_1, type1_2]])
    return array(types)


def calc_fusion_stats(stats_pairs):
    stats1 = stats_pairs[:, 0, :]
    stats2 = stats_pairs[:, 1, :]

    fusion1 = array([
        stats1[:, 0] * 2 / 3 + stats2[:, 0] * 1 / 3, stats1[:, 1] * 1 / 3 + stats2[:, 1] * 2 / 3,
        stats1[:, 2] * 1 / 3 + stats2[:, 2] * 2 / 3, stats1[:, 3] * 2 / 3 + stats2[:, 3] * 1 / 3,
        stats1[:, 4] * 2 / 3 + stats2[:, 4] * 1 / 3, stats1[:, 5] * 1 / 3 + stats2[:, 5] * 2 / 3
    ]).T.astype(int)

    fusion2 = array([
        stats1[:, 0] * 1 / 3 + stats2[:, 0] * 2 / 3, stats1[:, 1] * 2 / 3 + stats2[:, 1] * 1 / 3,
        stats1[:, 2] * 2 / 3 + stats2[:, 2] * 1 / 3, stats1[:, 3] * 1 / 3 + stats2[:, 3] * 2 / 3,
        stats1[:, 4] * 1 / 3 + stats2[:, 4] * 2 / 3, stats1[:, 5] * 2 / 3 + stats2[:, 5] * 1 / 3
    ]).T.astype(int)
    return stack([fusion1, fusion2], axis=1)


def rate_pokemon(stats, multipliers, types, off_mul, def_mul):
    defensive_score = get_defensive_score(types[0], types[1]) / 20 * def_mul
    offensive_score = get_offensive_score(types[0], types[1]) / 10 * off_mul
    stat_score = (stats[0] * multipliers[0] + stats[1] * multipliers[1] + stats[2] * multipliers[2] +
                  stats[3] * multipliers[3] + stats[4] * multipliers[4] + stats[5] * multipliers[5]) / 1000 * max(
                      0, (1 - off_mul - def_mul))

    return (stat_score + defensive_score + offensive_score) * 30


def rate_fusion(stats, stat_multipliers, fusion_types, off_mul, def_mul):
    return [
        rate_pokemon(statN, stat_multipliers, fusion_typeN, off_mul, def_mul)
        for statN, fusion_typeN in zip(stats, fusion_types)
    ]