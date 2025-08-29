# board.py
# Grafo dodecaédrico (20 salas, cada una con 3 túneles)

dodecahedron = {
    1:  {"room1": 5,  "room2": 8,  "room3": 2},
    2:  {"room1": 1,  "room2": 10, "room3": 3},
    3:  {"room1": 2,  "room2": 12, "room3": 4},
    4:  {"room1": 3,  "room2": 14, "room3": 5},
    5:  {"room1": 4,  "room2": 6,  "room3": 1},
    6:  {"room1": 15, "room2": 5,  "room3": 7},
    7:  {"room1": 6,  "room2": 17, "room3": 8},
    8:  {"room1": 7,  "room2": 1,  "room3": 9},
    9:  {"room1": 8,  "room2": 18, "room3": 10},
    10: {"room1": 9,  "room2": 2,  "room3": 11},
    11: {"room1": 10, "room2": 19, "room3": 12},
    12: {"room1": 11, "room2": 3,  "room3": 13},
    13: {"room1": 12, "room2": 20, "room3": 14},
    14: {"room1": 13, "room2": 4,  "room3": 15},
    15: {"room1": 14, "room2": 16, "room3": 6},
    16: {"room1": 17, "room2": 15, "room3": 20},
    17: {"room1": 16, "room2": 7,  "room3": 18},
    18: {"room1": 17, "room2": 9,  "room3": 19},
    19: {"room1": 18, "room2": 11, "room3": 20},
    20: {"room1": 19, "room2": 13, "room3": 16}
}

def instructions():
    print("Instructions")
    print("The dreaded Wumpus lives in a cave of 20 rooms. Each room has three tunnels leading to other rooms.")
    print("The shape is a classic dodecahedron. Like all unexplored caves, there are hazards.\n")
    print("Bottomless Pits - Two of the rooms have bottomless pits in them. If you venture there, you will")
    print("fall into the pit and lose.\n")
    print("Superbats - Two rooms have super bats. If you venture into these rooms, they will grab you and take")
    print("you to some other room at random.\n")
    print("The Wumpus - The Wumpus is a smelly beast that likes to sleep. If you enter his room, there is a")
