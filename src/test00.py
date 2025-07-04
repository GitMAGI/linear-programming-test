from pulp import *

def main():
    print(f'Started')

    solvers = listSolvers(onlyAvailable=True)
    print(solvers)

    print(f'Completed')

if __name__ == "__main__":
    main()