import numpy as np
from PIL import Image
import pygame as pg
import const
import random
from math import log

class Output:
    def __init__(self, X, Y, P):
        """
            Initializes the wave and stores sizes and Patterns
        """
        self.wave = [[[True for _ in range(len(P.patterns))]
                            for _ in range(Y)]
                            for _ in range(X)]
        self.X = X
        self.Y = Y
        self.patterns = P
        self.N = P.N

        self.squares = [[None for _ in range(self.Y)]
                              for _ in range(self.X)]
        self.cur_app = [0 for _ in range(len(self.patterns.patterns))]

        # Not the real entropy for now, but will be reevaluated later
        self.entropies = [[1 for _ in range(self.Y)]
                             for _ in range(self.X)]



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

                add = np.zeros_like(self.patterns.patterns[0].getdata(), dtype="float").reshape(self.N,self.N,-1)
                active = sum(self.wave[i][j])
                for k in range(len(self.patterns.patterns)):
                    if self.wave[i][j][k] == 1:
                        add += np.asarray(self.patterns.patterns[k]).astype('float') / active
                self.squares[i][j] = add.astype('int')

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

        #If more than 1 occurence of min :
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
            Collapse into one state, considering actual frequency and goal frequency
        """
        print("Collapsing : {}".format(coords))
        i = coords[0]
        j = coords[1]
        #Sample frequencies
        freq = np.asarray(self.patterns.frequencies)
        #Current frequencies
        curr_freq = np.asarray(self.cur_app)/(self.X * self.Y)

        d_curr_freq = freq - curr_freq
        d_curr_freq = [d_curr_freq[k] if self.wave[i][j][k]==1 else 0 for k in range(len(self.wave[i][j]))]

        max = np.argmax(d_curr_freq)
        # print(d_curr_freq)
        #print("Possibilities : {}".format(self.wave[i][j]))
        print("\nCollapsing for index {}, dfreq = {}".format(max, d_curr_freq[max]))

        self.wave[i][j] = np.zeros_like(self.wave[i][j])
        self.wave[i][j][max] = 1
        self.cur_app[max]+=1




    def info(self, coords):
        """
            Propagates information of a recently collapsed position to others
        """
        i = coords[0]
        j = coords[1]
        collapsed_pattern = self.patterns.patterns[np.argmax(self.wave[i][j])]

        #top left
        # Get the indices of all non-forbidden patterns
        indices = [i for i, x in enumerate(self.wave[(i-1)%self.Y][(j-1)%self.X]) if x == 1]
        for k in indices:
            if(self.patterns.patterns[k].getpixel((self.N-1,self.N-1)) != collapsed_pattern.getpixel((0,0))):
                self.wave[(i-1)%self.Y][(j-1)%self.X][k] = 0

        #top right
        indices = [i for i, x in enumerate(self.wave[(i-1)%self.Y][(j+1)%self.X]) if x == 1]
        for k in indices:
            if(self.patterns.patterns[k].getpixel((0,self.N-1)) != collapsed_pattern.getpixel((self.N-1,0))):
                self.wave[(i-1)%self.Y][(j+1)%self.X][k] = 0

        #bottom left
        indices = [i for i, x in enumerate(self.wave[(i+1)%self.Y][(j-1)%self.X]) if x == 1]
        for k in indices:
            if(self.patterns.patterns[k].getpixel((self.N-1,0)) != collapsed_pattern.getpixel((0,self.N-1))):
                self.wave[(i+1)%self.Y][(j-1)%self.X][k] = 0

        #bottom right
        indices = [i for i, x in enumerate(self.wave[(i+1)%self.Y][(j+1)%self.X]) if x == 1]
        for k in indices:
            if(self.patterns.patterns[k].getpixel((0,0)) != collapsed_pattern.getpixel((self.N-1,self.N-1))):
                self.wave[(i+1)%self.Y][(j+1)%self.X][k] = 0

        #left
        indices = [i for i, x in enumerate(self.wave[(i)%self.Y][(j-1)%self.X]) if x == 1]
        for k in indices:
            ok = 1
            for l in range(self.N):
                if(self.patterns.patterns[k].getpixel((self.N-1,l)) != collapsed_pattern.getpixel((0,l))):
                    ok = 0
                    break
            if ok==0 :
                self.wave[(i)%self.Y][(j-1)%self.X][k] = 0

        #top
        indices = [i for i, x in enumerate(self.wave[(i-1)%self.Y][(j)%self.X]) if x == 1]
        for k in indices:
            ok = 1
            for l in range(self.N):
                if(self.patterns.patterns[k].getpixel((l,self.N-1)) != collapsed_pattern.getpixel((l,0))):
                    ok = 0
                    break
            if ok==0 :
                self.wave[(i-1)%self.Y][(j)%self.X][k] = 0

        #right
        indices = [i for i, x in enumerate(self.wave[(i)%self.Y][(j+1)%self.X]) if x == 1]
        for k in indices:
            ok = 1
            for l in range(self.N):
                if(self.patterns.patterns[k].getpixel((0,l)) != collapsed_pattern.getpixel((self.N-1,l))):
                    ok = 0
                    break
            if ok==0 :
                self.wave[(i)%self.Y][(j+1)%self.X][k] = 0

        #bottom
        indices = [i for i, x in enumerate(self.wave[(i+1)%self.Y][(j)%self.X]) if x == 1]
        for k in indices:
            ok = 1
            for l in range(self.N):
                if(self.patterns.patterns[k].getpixel((l,0)) != collapsed_pattern.getpixel((l,self.N-1))):
                    ok = 0
                    break
            if ok==0 :
                self.wave[(i+1)%self.Y][(j)%self.X][k] = 0
