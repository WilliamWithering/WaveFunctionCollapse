from PIL import Image
from numpy import asarray
import const
import pygame as pg


class Patterns:
    def __init__(self, input, N, rotate):
        """
            This function counts the different patterns found in input
            and returns an array of sub-images and frequencies
        """

        img = Image.open(input).convert('RGB')
        w, h = img.size

        self.N = N 			   # Patterns size
        self.patterns = []     # List of images
        self.appearance = []   # List of number of appearance of a pattern
        self.total = 0         # Number of NxN patterns analyzed

        for i in range(h-N+1):
            for j in range(w-N+1):
                pattern = img.crop((j,i,j+N,i+N))

                #For each pattern rotation, we check wether it's alerady in the pattern list
                if(rotate):
                    to_check = [pattern,
                          pattern.transpose(Image.ROTATE_90),
                          pattern.transpose(Image.ROTATE_180),
                          pattern.transpose(Image.ROTATE_270),
                          pattern.transpose(Image.FLIP_LEFT_RIGHT),
                          pattern.transpose(Image.FLIP_TOP_BOTTOM),
                          pattern.transpose(Image.TRANSPOSE)]
                else :
                    to_check = [pattern]

                for p in to_check:
                    self.total += 1

                    if not(p in self.patterns):
                        self.patterns.append(p)
                        self.appearance.append(1)
                    else:
                        k = self.patterns.index(p)
                        self.appearance[k] += 1


        print("{} patterns found ! ".format(len(self.patterns)))
        self.frequencies = [x/self.total for x in self.appearance]


    def print(self):
        """
            A development function to visualize found patterns
        """
        for i in range(len(self.patterns)):
            print("Pattern : {}, frequency : {}/{}".format(i, self.appearance[i],self.total))
        print(sum(self.appearance))

    def display_patterns(self, window):
        """
            Displays the list of all patterns
            Could be done better, just a debug tool on a specific example
        """

        for i in range(15):
            for j in range(15):
                if(i+j*15 < len(self.patterns)):
                    str = self.patterns[i+j*15].tobytes("raw","RGB")
                    surf = pg.image.fromstring(str, (self.N,self.N), "RGB")

                    sizes = tuple(const.zoom * x for x in surf.get_size())
                    surf = pg.transform.scale(surf,sizes)

                    window.blit(surf,(i*self.N*const.zoom,j*self.N*const.zoom))

        for i in range(15):
            for j in range(15):
                if(i+15*j < len(self.patterns)):
                    pg.draw.line(window, (255,0,0),
                                        ((i+1)*self.N*const.zoom,j*self.N*const.zoom),
                                        ((i+1)*self.N*const.zoom,(j+1)*self.N*const.zoom))
                    pg.draw.line(window, (255,0,0),
                                        (i*self.N*const.zoom,(j+1)*self.N*const.zoom),
                                        ((i+1)*self.N*const.zoom,(j+1)*self.N*const.zoom))

        pg.display.flip()
