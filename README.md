# Pokemon Infinite Fusion Optimizer

A fusion optimizer created for the game Pokemon Infinite Fusion

Program created to simplify the process of finding the best fusion for a role, it lets you weight the stats, filter by name, current progress in the playthrough, total base stat, find the best partner for a pokemon and even adjust the importance of the typing, both offensively and defensively.

### Parameters

- **Profiles** - You can create multiple profiles to search for fusions that fulfill a specific role, from physical sweeper to bulky special wall. Profiles are composed of a list of weights that determine the scoring system for the fusion you wish to find, the first list of 6 numbers represent the weight of the Pokemon base stats (HP, Attack, Defense, Special Attack, Special Defense and Speed) and the last two numbers represent the weight of the offensive and defensive typing respectively. The higher the number, the more important that stat is for the fusion you are looking for.

- **Filters** - You can filter the results by name, current progress in the playthrough and total base stat. The name filter is case sensitive and will filter out any pokemon that contains the string you typed, the progress filter will only show fusions that are currently available in the game and the base stat filter will only show fusions that have a total base stat equal or lower than the number you typed.

- **Partner** - You can find the best partner for a pokemon, the program will find the best fusion for the pokemon you typed.

- **Type boosts** - You can give more weight to specific types, rewarding crucial resistances or STABS such as fighting or ground while nerfing others such as bug. You can also balance the importance of physical and special types when searching for a fusion. The latter will be automatically balanced towards the stats you gave more weight to if you don't change the value.

### Usage for normal users

Download the latest release from the [releases page](https://github.com/Valkam-Git/Pokemon-Infinite-Fusion-Optimizer/releases) and extract the contents of the zip file to a folder of your choice.

Run the `Pokemon Infinite Fusion Optimizer.exe` file to generate results in the results folder.

The user can edit the `settings.json` file to change the parameters of the program, the `profiles.csv` file to create new profiles and the `type_info.json` file to change the type boosts.

### Usage for developers

The project has been written in Python 3.10.7 and uses the following libraries:

- Pandas
- Numpy
- BeautifulSoup4

To install them, run the following command:

```bash
pip install -r requirements.txt
```

### TODO

- Dump the game data directly from the game files using a post-game item.
- Take abilities and moves into account.
- Create a team planner tool based on pokemon roles.
- Make a GUI.
