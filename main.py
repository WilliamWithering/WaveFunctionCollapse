# Algorithme :
#     - Read input and count NxN patterns
#         . Augment with rotations/reflections
#     - Create an array with dimensions of wanted output
#         . Each element represent the state of an NxN region (superposition with boolean coefs)
#         . False means forbidden, True means not yet forbidden
#     - Initialize all to True
#     - Repeat :
#         . Observation
#             Choose the element with minimal non-zero entropy. If all have 0 or undefined break cycle
#             Collapse according to coef and distrib of NxN
#         . Propagation
#             Propagate information gained during previous Observation
#     - Contradictive or completely observed

import pygame as pg
import classOutput
import classPatterns
import const


pg.init()
window = pg.display.set_mode(((const.W_output*(const.N-1)+1)*const.zoom,
                              (const.H_output*(const.N-1)+1)*const.zoom))
pat = classPatterns.Patterns("Forest.png",const.N)
output = classOutput.Output(const.W_output,const.H_output,pat)

output.init_entropy()

running = True
c = (0,0)

while running and c!=(-1,-1):
    output.update_display(window)

    c = output.get_min_entro_coord()
    output.collapse(c)
    output.info(c)
    output.update_entropy(c)

    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
    pg.time.wait(10)

#Keeps the window open when it's done
running = True
output.update_display(window)
while running:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
    pg.time.wait(10)
