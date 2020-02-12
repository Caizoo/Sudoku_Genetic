from random import *
from copy import deepcopy
import time

def evolve(board): # begin search with given board

    numTimesStuck = 0
    prevBestFit = 10000

    total_best_ind = 0
    total_best_fit = 10000

    population = create_pop(board)
    fitness_population = evaluate_pop(population, board) # evaluate initial population
    generations_to_solve = 0
    t = time.time() # to time how long each search takes
    for gen in range(NUMBER_GENERATION):
        mating_pool = select_pop(population, fitness_population) # select top % of population
        offspring_population = crossover_pop(mating_pool)        # create children from this selection
        population = mutate_pop(offspring_population)            # mutate the children
        fitness_population = evaluate_pop(population, board)     # evaluate
        best_ind, best_fit = best_pop(population, fitness_population)
        if(best_fit<total_best_fit): total_best_ind,total_best_fit = best_ind,best_fit # best solution of current generation
        if (best_fit == 0): break # if solution is found, end search

        if(best_fit==prevBestFit): # if best fitness is same as last gen, add one to stuck counter
            numTimesStuck += 1
        else:
            numTimesStuck = 0
        prevBestFit = best_fit
        if(numTimesStuck>30): # if stuck in local minimum, start population over with a new initial population
            numTimesStuck = 0
            population = create_pop(board)

        print("Current best fitness:",best_fit,"Current gen:",generations_to_solve) # print out current generation's best fitness to keep track of search
        generations_to_solve += 1

    total_fitness = 0
    for i in fitness_population: # used for average fitness of last population
        total_fitness += i

    return (total_best_ind, total_best_fit, generations_to_solve, (total_fitness / POPULATION_SIZE), time.time() - t) # return perfomance results

# population-level operators

def best_pop(population, fitness_population):
    return sorted(zip(population, fitness_population), key=lambda ind_fit: ind_fit[1])[0] # return the best individual and it's fitness from the population


def create_pop(board):
    return [create_ind(board) for _ in range(POPULATION_SIZE)] # create POPULATION_SIZE number of individuals to initalise the search


def evaluate_pop(population, board):
    return [fitness_ind(matrix_addition(individual, board)) for individual in population] # evaluate the fitness of each individual in population


def select_pop(population, fitness_population):
    sorted_population = sorted(zip(population, fitness_population), key=lambda ind_fit: ind_fit[1]) # sort the population by fitness
    return [individual for individual, fitness in sorted_population[:int(POPULATION_SIZE * TRUNCATION_RATE)]] # select the top %


def crossover_pop(population):
    return [crossover_ind(choice(population), choice(population)) for _ in range(POPULATION_SIZE)] # select two random parents from the selection and cross them to repopulate the population


def mutate_pop(population):
    return [mutate_ind(individual) for individual in population] # for each individual, run mutate function (has function to check whether to mutate or not)


# individual-level operations

def fitness_ind(board): # no need to check blocks as it's made sure a block conflict cannot happen
    rows = []
    cols = []
    for i in range(9):
        rows.append([])
        cols.append([])

    for block_count in range(9):
        for row_count in range(3):
            for cell_count in range(3):
                cell = board[block_count][row_count][cell_count] # for every cell on the board
                rows[row_count + 3 * int(block_count / 3)] = rows[row_count + 3 * int(block_count / 3)] + [cell] # add cell to correct row and column
                cols[(block_count % 3) * 3 + cell_count] = cols[(block_count % 3) * 3 + cell_count] + [cell]
    return fitness_part(rows, 1) + fitness_part(cols, 1) # evaluate number of conflicts on rows and column


def fitness_part(part, incrementValue): # evaluate either rows or columns
    part_fitness = 0
    for ind in part:
        row = list(ind) # sort the entire row or column
        row.sort()
        for i in range(len(row) - 1):
            if (row[i] == row[i + 1]): # if conflict, i.e. a number follows the same number in sorted list, add 1 to fitness
                part_fitness += incrementValue
    return part_fitness


def crossover_ind(p1, p2):
    return [choice(block) for block in zip(p1, p2)] # for each block of the child, randomly select from either parent 1 or 2


def mutate_ind(individual):
    return [mutate_block(block) for block in individual] # for each block, check for mutation


def mutate_block(block):  # completely mix up a single block
    if random() > MUTATION_RATE: return deepcopy(block) # if not mutate, return unaffected block
    new_block = deepcopy(block)

    indices_to_choose = []
    for i in range(len(new_block)):
        for j in range(len(new_block[0])):
            if (new_block[i][j] != 0):
                indices_to_choose.append((i, j)) # all the possible indices that can be changed

    ind1 = choice(indices_to_choose) # choose two
    indices_to_choose.remove(ind1)
    ind2 = choice(indices_to_choose)
    new_block[ind1[0]][ind1[1]], new_block[ind2[0]][ind2[1]] = new_block[ind2[0]][ind2[1]], new_block[ind1[0]][ind1[1]] # swap two numbers in a block

    return new_block


def create_ind(board): # create an inital
    rand_board = []
    for block in board: # for each block in the given board, fill the rest in randomly
        rand_block = randomize_block(block)
        rand_board.append(rand_block)
    return rand_board


def randomize_block(block):
    block_nums = []
    new_block = []
    for i in range(3):
        new_block.append([0, 0, 0])
    for row in block:
        for cell in row:
            block_nums.append(cell)
    choiceList = list(set([1, 2, 3, 4, 5, 6, 7, 8, 9]) - set(block_nums)) # take the set of given numbers from the set {1...9}
    for row in range(3):
        for cell in range(3):
            if (block[row][cell] == 0):
                new_cell = choice(choiceList)
                choiceList.remove(new_cell)
                new_block[row][cell] = new_cell # for each cell, take one from the new set and add to block
            else:
                new_block[row][cell] = 0 # if number is given, for the guess matrix have as a blank cell
    return list(new_block)


# matrix operations

def matrix_addition(m1, m2):
    return [block_addition(b) for b in zip(m1, m2)] # add two matrices together, i.e. a given board and a guess board


def block_addition(block):
    return [row_addition(row) for row in zip(block[0], block[1])] # add two blocks together


def row_addition(row):
    return [sum(x) for x in zip(row[0], row[1])] # add two lists together, done for each row in a block


# io operations

def read_in_file(filename):
    file = open(filename, 'r')
    strIn = file.readlines()
    for i in range(0, len(strIn) - 1):
        strIn[i] = strIn[i][:len(strIn[i]) - 1] # read in file and remove new line character
    file.close

    return strIn  # list of strings, each element is a line from the file


def create_board(file_contents):
    board = []
    for i in range(0, len(file_contents) - 1, 3 + 1):  # +1 to skip ---!---!--- line
        row_blocks = list(
            zip(file_contents[i], file_contents[i + 1], file_contents[i + 2]))  # zip first 3 lines together
        for j in range(0, len(row_blocks) - 1, 4):
            block = create_block(list(zip(row_blocks[j], row_blocks[j + 1], row_blocks[j + 2]))) # create a block from the given row
            board.append(block)
    return board


def create_block(block):
    intBlock = []
    for i in range(3):
        intRow = []
        for j in range(3):
            if (block[i][j] == '.'): # if blank, use 0
                intRow.append(0)
            else:
                intRow.append(int(block[i][j])) # else use given number
        intBlock.append(intRow)
    return intBlock


def print_board(board):
    for i in range(0, len(board) - 1, 3): # for each row of blocks
        print_row(list(zip(board[i], board[i + 1], board[i + 2]))) # print block


def print_row(row):
    for line in row:
        for i in range(3):
            print(line[i], end=' ') # print first first row of each block given, then second then third
        print()
    print()

# create given boards
board1 = create_board(read_in_file("Grid1.txt"))
board2 = create_board(read_in_file("Grid2.txt"))
board3 = create_board(read_in_file("Grid3.txt"))

POPULATION_SIZE = 1000
NUMBER_GENERATION = 2000
TRUNCATION_RATE = 0.2
MUTATION_RATE = 0.16

b1 = evolve(board1)
print("Board 1 finished") # keeping track of search
b2 = evolve(board2)
print("Board 2 finished")
b3 = evolve(board3)

print("Board 1 results ------------")
print_board(matrix_addition(b1[0],board1))
print("Best fitness:",b1[1],"Num generations:",b1[2])
print()
print("Board 2 results ------------")
print_board(matrix_addition(b2[0],board2))
print("Best fitness:",b2[1],"Num generations:",b2[2])
print()
print("Board 3 results ------------")
print_board(matrix_addition(b3[0],board3))
print("Best fitness:",b3[1],"Num generations:",b3[2])