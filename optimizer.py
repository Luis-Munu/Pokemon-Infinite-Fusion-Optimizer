from copy import deepcopy
from itertools import combinations

from numpy import array, nan, unravel_index

from config import profiles, settings
from scoring import calc_fusion_stats, determine_fusion_types, rate_fusion
from utils import write_msg


def generate_pokemon_pairs(dataset):
    pokemon = dataset[[
        "Name", "Total", "Type 1", "Type 2", "HP", "Attack", "Defense", "Special Attack", "Special Defense", "Speed"
    ]]
    pokemon = pokemon[
        pokemon["Total"] < settings["Maximum base stats"]] if settings["Filter Pokemon by max stats"] else pokemon

    name_type_cols = ["Name", "Type 1", "Type 2"]
    stats_cols = ["HP", "Attack", "Defense", "Special Attack", "Special Defense", "Speed"]
    return array(list(combinations(pokemon[name_type_cols + stats_cols].values, 2)))


def calc_best_scores(profile, pairs):
    fusion_stats = calc_fusion_stats(pairs[:, :, 3:])
    fusion_types = determine_fusion_types(pairs[:, 0, 1:3], pairs[:, 1, 1:3])

    fusion_scores = rate_fusion(fusion_stats.reshape(-1, 6), [
        profile['HP'], profile['Attack'], profile['Defense'], profile['Special Attack'], profile['Special Defense'],
        profile['Speed']
    ], fusion_types.reshape(-1, 2), profile['Offensive Typing'], profile['Defensive Typing'])

    fusion_scores = array(fusion_scores).reshape(-1, 2)
    if len(fusion_scores) == 0:
        return None
    max_index = unravel_index(fusion_scores.argmax(), fusion_scores.shape)
    return (pairs[max_index[0], 0, 0], pairs[max_index[0], 1, 0], fusion_scores[max_index],
            fusion_stats[max_index[0], max_index[1]], fusion_types[max_index[0], max_index[1]])


def enforce_pokemon_pair(pairs, pokemon):
    if settings["Force Pokemon in Fusion"] and pokemon:
        pairs = pairs[(pairs[:, 0, 0] == pokemon) | (pairs[:, 1, 0] == pokemon)]
    return pairs


def find_best_fusion(profile, dataset, force_pokemon=None):
    pairs = generate_pokemon_pairs(dataset)
    pairs = enforce_pokemon_pair(pairs, force_pokemon)
    return [calc_best_scores(profile, pairs)]


def optimize_boost(profile):
    if profile["Attack"] >= profile["Special Attack"]:
        settings["physical_boost"] = (profile["Attack"] - profile["Special Attack"]) / 10 + 1
        settings["special_boost"] = 1
    else:
        settings["special_boost"] = (profile["Special Attack"] - profile["Attack"]) / 10 + 1
        settings["physical_boost"] = 1


def iterate_profiles(pokemon_set, partner=None):
    local_result = ""
    stat_names = ["HP", "Attack", "Defense", "Special Attack", "Special Defense", "Speed"]
    profiles_cp = deepcopy(profiles)

    for profile in profiles_cp:
        optimize_boost(profile)
        results = find_best_fusion(profile, pokemon_set, partner)
        if results[0]:
            results = list(reversed(find_best_fusion(profile, pokemon_set, partner)[-5:]))
            local_result += f"Results for {profile['description']}: \n"
            profile.pop("description")
            for result in results:
                lc = f"{result[1]} + {result[0]}: {round(result[2], 2)}\n" + f"Stats: {', '.join(f'{name}: {stat}' for name, stat in zip(stat_names, result[3]))}\n" + f"Types: {', '.join(x.title() for x in result[4])}\n\n"
                local_result += lc
        else:
            local_result += "No Pokemon found that match your criteria. Please check your filters."
            break

    return local_result


def main_loop(pokemon_set):
    # check if pokemon set is not empty
    if pokemon_set.empty:
        write_msg("No Pokemon found that match your criteria. Please check your filters.")
        return
    res = ""
    partners = settings["Forced Pokemon"] if settings["Force Pokemon in Fusion"] else [None]
    for partner in partners:
        res += f"Results for {'all Pokemon' if not partner else partner}:\n"
        res += iterate_profiles(pokemon_set, partner)
    write_msg(res)