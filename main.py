from extraction import data_extraction
from preprocessing import preprocessing
from optimizer import main_loop

if __name__ == "__main__":
    print("Welcome to the Pokemon Team Optimizer!")
    print("Extracting data from the Pokemon API...")
    pokemon_set = data_extraction()
    print("Preprocessing data...")
    print("Data preprocessing complete!")
    pokemon_set = preprocessing(pokemon_set)
    print("Starting optimization...")
    main_loop(pokemon_set)