from extraction import data_extraction
from preprocessing import preprocessing
from optimizer import main_loop

if __name__ == "__main__":
    pokemon_set = data_extraction()
    pokemon_set = preprocessing(pokemon_set)
    main_loop(pokemon_set)