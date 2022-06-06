roi_center = {
    "runway": (850, 170), 
    "rpmleft": (652, 438),
    "asi": (695, 490), 
    "alt": (820, 490),
    "nrst": (840, 550),
    "rpmright": (1050, 438),
 }

label = {"runway": [(0,0), (1280, 350), "r"],
         "rpmleft": [(633, 411), (672, 451), "r"],
         "asi": [(674, 432), (705, 525), "r"],
         "alt": [(797, 428), (852, 523), "r"],
#          "hsi": [(742, 556), 45, "c"],
#          "nrst": [(792, 534), (876, 554), "r"],
#          "RPM_RIGHT": [(1054, 440), 30, "c"]
}

encode_table = {
    "rpmleft": "R",
#     "nrst": "Q",
#     "RPM_RIGHT": "R",
    "asi": "S",
#     "hsi": "D",
    "alt": "A",
    "runway": "X",
    "unknown": "Z"
}