import pyxel 
import time
import random

class Ennemi_arbre:
    def __init__(self,h,l,taille,largeur):
        self.tab = []
        self.x = l - largeur
        self.y = h - taille
        self.h = h
        self.l = l
        self.hauteur_perso = taille
        self.largeur_perso = largeur
        self.time = 30
        self.speed = 1
        self.cap = 0
        self.time = time.time() % 60

    def creation_ennemi(self):
        if ((pyxel.frame_count % self.time) == 0):
            self.tab.append([self.x,self.y])
            if self.cap == 0:
                self.time = random.randint(60,90)
            if self.cap == 1:
                self.time = random.randint(50,80)
            if self.cap == 2:
                self.time = random.randint(30,60)
            if self.cap == 3:
                self.time = random.randint(30,50)
            if self.cap >= 4:
                self.time = random.randint(10,40)

    def mouv(self):
        if (pyxel.frame_count % 1800 == 0):
            print("40 seconde ecoulée")
            self.speed = self.speed + 0.5
            self.cap = self.cap + 1
            print(self.cap)
        for ennemi in self.tab:
            ennemi[0] -= self.speed
            if  ennemi[0]<0:
                self.tab.remove(ennemi)
        pass

    def player_collision(self,player_x,player_y):
        for ennemi in self.tab:
            if ennemi[0] <= player_x +8 and ennemi[1] <= player_y +16 and ennemi[0]+8 >= player_x and ennemi[1]+8 >= player_y:
                self.tab.remove(ennemi)
                return -1  
        return 0                 

    def draw(self):
        for ennemi in self.tab:
            pyxel.blt(ennemi[0],ennemi[1], 0, 8, 24, self.largeur_perso, self.hauteur_perso, 5)
            #pyxel.rect(ennemi[0],ennemi[1],self.largeur_perso, self.hauteur_perso, 1)
        pass



class Player:
    def __init__(self,life,h,l,taille,largeur):
        self.x = 0
        self.y = h - taille
        self.vie = life 
        self.h = h
        self.l = l
        self.hauteur_perso = taille
        self.largeur_perso = largeur

    def mouv(self):
        if pyxel.btn(pyxel.KEY_RIGHT) and self.x< self.l -self.largeur_perso:
            self.x += 2
        if pyxel.btn(pyxel.KEY_LEFT) and self.x>0:
            self.x += -2
        
        if pyxel.btn(pyxel.KEY_UP) and self.y>0 and self.y == self.h - self.hauteur_perso:
            self.y += -40

        if self.y< self.h - self.hauteur_perso:
            self.y += 1
        pass

    def update_vie(self):
        if self.vie == 2:
            pyxel.tilemap(0).pset(6,0,(0,0))
        if self.vie ==1:
            pyxel.tilemap(0).pset(5,0,(0,0))
        if self.vie == 0:
            pyxel.tilemap(0).pset(4,0,(0,0))


    def draw(self):
        pyxel.blt(self.x, self.y, 0, 0, 24, self.largeur_perso, self.hauteur_perso, 5)
        #pyxel.rect(self.x, self.y, self.largeur_perso, self.hauteur_perso, 1)


class Game:
    def __init__(self):
        h = 60
        l = 200
        taille_perso =16
        largeur_perso = 8
        pyxel.init(l,h,title="FLOP")
        self.time_s = 0
        self.time_m = 0
        self.ennemie = Ennemi_arbre(h,l,taille_perso,largeur_perso)
        self.player = Player(3,h,l,taille_perso,largeur_perso)
        pyxel.load("../assets/images.pyxres")
        pyxel.run(self.update, self.draw)
    
    def update(self):
        if self.player.vie != 0:
            self.player.mouv()
            self.ennemie.creation_ennemi()
            self.ennemie.mouv()
            self.player.vie = self.ennemie.player_collision(self.player.x,self.player.y) + self.player.vie 
            self.player.update_vie()
            if pyxel.frame_count % 30 == 0:
                self.time_s= self.time_s + 1
                i1 = 24
                i2 = 21
                tab = {"0":(2,2),"1":(2,1),"2":(3,1),"3":(3,2),"4":(4,1),"5":(4,2),"6":(5,1),"7":(5,2),"8":(6,1),"9":(6,2)}
                for elt in str(self.time_s)[::-1]:
                    if self.time_s == 60:
                        self.time_m = self.time_m + 1
                        self.time_s = 0
                    if len(str(self.time_s)) == 2:
                        pyxel.tilemap(0).pset(i1,0,tab[elt])
                        i1=i1-1
                    if len(str(self.time_s)) == 1:
                        pyxel.tilemap(0).pset(24,0,tab[elt])
                        pyxel.tilemap(0).pset(23,0,tab["0"])

                for elt in str(self.time_m)[::-1]:
                    if len(str(self.time_m)) == 2:
                        pyxel.tilemap(0).pset(i2,0,tab[elt])
                        i2=i2-1
                    if len(str(self.time_m)) == 1:
                        pyxel.tilemap(0).pset(21,0,tab[elt])
                        pyxel.tilemap(0).pset(20,0,tab["0"])
        else:
            self.time_s = 0
            self.time_m = 0
            self.ennemie.tab = []
            self.player = Player(3,60,200,16,8)
            self.player.vie = 3
            self.ennemie.speed = 1
            self.ennemie.cap = 0
            pyxel.tilemap(0).pset(6,0,(1,0))
            pyxel.tilemap(0).pset(5,0,(1,0))
            pyxel.tilemap(0).pset(4,0,(1,0))
        pass
    
    def draw(self):
        pyxel.cls(3)
        pyxel.bltm(0, 0, 0, 0, 0, 200, 60) 
        self.player.draw()
        self.ennemie.draw()
        pass

Game()
