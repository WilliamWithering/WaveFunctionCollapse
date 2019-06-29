import numpy as np
from PIL import Image
import pygame as pg
import const
import random
from math import log

#Found on pygame.org
def rot_center(image, angle):
    """rotate an image while keeping its center and size"""
    orig_rect = image.get_rect()
    rot_image = pg.transform.rotate(image, angle)
    rot_rect = orig_rect.copy()
    rot_rect.center = rot_image.get_rect().center
    rot_image = rot_image.subsurface(rot_rect).copy()
    return rot_image


class Output:
    def __init__(self, X, Y, P):
        """
            Initializes the wave and stores sizes and Patterns
        """
        # Initializes all patterns to 1 (all allowed)
        self.wave = [[[True for _ in range(len(P.patterns))]
                            for _ in range(X)]
                            for _ in range(Y)]
        self.X = X
        self.Y = Y
        self.patterns = P
        self.N = P.N

        self.squares = [[None for _ in range(self.X)]
                              for _ in range(self.Y)]

        # Counts how many patterns of each type have been placed
        self.cur_app = [0 for _ in range(len(P.patterns))]

        # Not the real entropy for now, but will be reevaluated later
        self.entropies = [[1 for _ in range(self.X)]
                             for _ in range(self.Y)]

        # Make distinction between chosen states, and propagation
        self.chosen = [[0 for _ in range(self.X)]
                             for _ in range(self.Y)]


    def init_entropy(self):
        """
            Calculates entropy when all states are allowed, and fill self.entropies with this value
        """
        freq = np.asarray(self.patterns.appearance)
        state = np.asarray(self.wave[0][0])
        tot = sum(state * freq)
        entro = 0

        for k in range(len(self.patterns.appearance)):
            entro -= (state[k]*freq[k])/tot * log((state[k]*freq[k])/tot)

        for i in range(self.Y):
            for j in range(self.X):
                self.entropies[i][j] = entro





    def update_display(self, window):
        """
            Displays the current state of the wave

            Calculates a blending between all "not yet forbidden" patterns for each square
            Then slightly overlay those patterns
        """

        for i in range(self.Y):
            for j in range(self.X):
                add = np.zeros_like(np.asarray(self.patterns.patterns[0]), dtype="float")
                active = sum(self.wave[i][j])

                indices = [i for i, x in enumerate(self.wave[i][j]) if x == 1]
                for k in indices:
                    add += np.asarray(self.patterns.patterns[k]).astype('float') / active
                self.squares[i][j] = np.transpose(add, axes=(1,0,2)).astype('int')


        for i in range(self.Y):
            for j in range(self.X):
                surf = pg.surfarray.make_surface(self.squares[i][j])
                sizes = tuple(const.zoom * x for x in surf.get_size())
                surf = pg.transform.scale(surf,sizes)
                window.blit(surf,(j*(self.N-1)*const.zoom,i*(self.N-1)*const.zoom))
        pg.display.flip()



    def get_min_entro_coord(self):
        """
            Returns the coordinates of a non-zero minimum of entropy, or (-1,-1)
        """
        min = None
        coords = [(-1,-1)]

        for i in range(self.Y):
            for j in range(self.X):
                if(min):
                    #if new min
                    if self.entropies[i][j] < min and self.entropies[i][j] != 0:
                        min = self.entropies[i][j]
                        coords = [(i,j)]
                    #if min found again
                    if self.entropies[i][j] == min:
                        coords.append((i,j))
                elif self.entropies[i][j] != 0:
                    min = self.entropies[i][j]
                    coords = [(i,j)]

        if len(coords)>1:
            return random.choice(coords)
        else:
            return coords[0]



    def update_entropy(self,coords):
        """
            Update entropies after collapse of a point
        """
        freq = np.asarray(self.patterns.appearance)
        for i in [-1,0,1]:
            for j in [-1,0,1]:
                state = np.asarray(self.wave[(coords[0]+i)%self.Y][(coords[1]+j)%self.X])
                tot = sum(state * freq)
                entro = 0
                for k in range(len(self.patterns.appearance)):
                    if state[k]!=0:
                        entro -= (state[k]*freq[k])/tot * log((state[k]*freq[k])/tot)
                self.entropies[(coords[0]+i)%self.Y][(coords[1]+j)%self.X] = entro





    def collapse(self, coords):
        """
            Collapse into one state,

            Todo : Should be considering actual frequency and goal frequency
        """
        # print("Collapsing : {}".format(coords))
        i = coords[0]
        j = coords[1]

        indices = [i for i, x in enumerate(self.wave[i][j]) if x == 1]
        weights = [self.patterns.frequencies[i] for i in indices]
        
        # Rescaling the weights so that the sum is 1
        weights = [w * 1/sum(weights) for w in weights]

        choice = random.choices(population = indices, weights = weights,k=1)

        self.wave[i][j] = np.zeros_like(self.wave[i][j])
        self.wave[i][j][choice[0]] = 1
        self.cur_app[choice[0]]+=1
        self.chosen[i][j]=1




    def info(self, coords):
        """
            Propagates information of a recently collapsed position to others

            Still to be fixed : case were the waveFunction contains only only one "True"
            -> If this state has been chosen, then do not modify it
            -> If this state hasn't, then forbid if necessary
        """
        i = coords[0]
        j = coords[1]
        collapsed_pattern = self.patterns.patterns[np.argmax(self.wave[i][j])]

        #top left
        # Get the indices of all non-forbidden patterns
        indices = [i for i, x in enumerate(self.wave[(i-1)%self.Y][(j-1)%self.X]) if x == 1]
        #If there are more than one indices (means not collapsed yet)
        if len(indices)>1 or self.chosen[i][j]==0:
            for k in indices:
                if(self.patterns.patterns[k].getpixel((self.N-1,self.N-1)) != collapsed_pattern.getpixel((0,0))):
                    self.wave[(i-1)%self.Y][(j-1)%self.X][k] = False

        #top right
        indices = [i for i, x in enumerate(self.wave[(i-1)%self.Y][(j+1)%self.X]) if x == 1]
        if len(indices)>1 or self.chosen[i][j]==0:
            for k in indices:
                if(self.patterns.patterns[k].getpixel((0,self.N-1)) != collapsed_pattern.getpixel((self.N-1,0))):
                    self.wave[(i-1)%self.Y][(j+1)%self.X][k] = False

        #bottom left
        indices = [i for i, x in enumerate(self.wave[(i+1)%self.Y][(j-1)%self.X]) if x == 1]
        if len(indices)>1 or self.chosen[i][j]==0:
            for k in indices:
                if(self.patterns.patterns[k].getpixel((self.N-1,0)) != collapsed_pattern.getpixel((0,self.N-1))):
                    self.wave[(i+1)%self.Y][(j-1)%self.X][k] = False

        #bottom right
        indices = [i for i, x in enumerate(self.wave[(i+1)%self.Y][(j+1)%self.X]) if x == 1]
        if len(indices)>1 or self.chosen[i][j]==0:
            for k in indices:
                if(self.patterns.patterns[k].getpixel((0,0)) != collapsed_pattern.getpixel((self.N-1,self.N-1))):
                    self.wave[(i+1)%self.Y][(j+1)%self.X][k] = False

        #left
        indices = [i for i, x in enumerate(self.wave[(i)%self.Y][(j-1)%self.X]) if x == 1]
        if len(indices)>1 or self.chosen[i][j]==0:
            for k in indices:
                ok = 1
                for l in range(self.N):
                    if(self.patterns.patterns[k].getpixel((self.N-1,l)) != collapsed_pattern.getpixel((0,l))):
                        ok = 0
                        break
                if ok==0 :
                    self.wave[(i)%self.Y][(j-1)%self.X][k] = False

        #top
        indices = [i for i, x in enumerate(self.wave[(i-1)%self.Y][(j)%self.X]) if x == 1]
        if len(indices)>1 or self.chosen[i][j]==0:
            for k in indices:
                ok = 1
                for l in range(self.N):
                    if(self.patterns.patterns[k].getpixel((l,self.N-1)) != collapsed_pattern.getpixel((l,0))):
                        ok = 0
                        break
                if ok==0 :
                    self.wave[(i-1)%self.Y][(j)%self.X][k] = False

        #right
        indices = [i for i, x in enumerate(self.wave[(i)%self.Y][(j+1)%self.X]) if x == 1]
        if len(indices)>1 or self.chosen[i][j]==0:
            for k in indices:
                ok = 1
                for l in range(self.N):
                    if(self.patterns.patterns[k].getpixel((0,l)) != collapsed_pattern.getpixel((self.N-1,l))):
                        ok = 0
                        break
                if ok==0 :
                    self.wave[(i)%self.Y][(j+1)%self.X][k] = False

        #bottom
        indices = [i for i, x in enumerate(self.wave[(i+1)%self.Y][(j)%self.X]) if x == 1]
        if len(indices)>1 or self.chosen[i][j]==0:
            for k in indices:
                ok = 1
                for l in range(self.N):
                    if(self.patterns.patterns[k].getpixel((l,0)) != collapsed_pattern.getpixel((l,self.N-1))):
                        ok = 0
                        break
                if ok==0 :
                    self.wave[(i+1)%self.Y][(j)%self.X][k] = False
