# coding: utf-8
import pygame as pg
from pygame import Vector2 as Vec
import random
from statistics import mean
 
class World:
    """ Classe principale"""
    def __init__(self):
        """ initie la fenetre pygame, les groupes de sprites,
        et créé les case de la grille"""
        self.all_group = pg.sprite.RenderUpdates()
        self.cell_group = pg.sprite.RenderUpdates()
        self.ant_group = pg.sprite.RenderUpdates()
        self.allowed_values = list(range(-5, 6))
        self.allowed_values.remove(0)
        pg.init()
        pg.event.set_allowed([pg.QUIT, pg.MOUSEBUTTONUP])
        self.gameDisplay = pg.display.set_mode((int(WINDOWS.x),int(WINDOWS.y)), \
                                           pg.HWSURFACE| pg.DOUBLEBUF, 8) #| pg.FULLSCREEN pg.SRCALPHA|)
        pg.display.set_caption('Ants')
        self.clock = pg.time.Clock()
        self.running = True
        grid = Vec(int(WINDOWS.x/CELL_SIZE),int(WINDOWS.y/CELL_SIZE))
        for row in range(int(grid.x)):
            for col in range(int(grid.y)):
                # créer une case vide
                type = 'none'
                if row == 0 or col == 0 or row == grid.x-1 or col == grid.y-1: # encadre de mur
                    # créer une case mur
                    type = 'wall'
                c = Cell(Vec(row,col), type) # créer les case de la grille
                self.all_group.add(c) # ajoute la case à un group général
                self.cell_group.add(c) # ajoute la case au group sprite correspondant
 
    def update(self, FPS, end_time):
        """ fonction qui, dans une boucle, met à jours
        les différents groups de sprites,
        gère les evenements de la souris, et dessine les sprites"""
        time = 0
        for c in self.cell_group: # peut être supprimer pour commencer sur une grille vierge
            c.check_click((116,102), 1) # créer une case food
            c.check_click((195,204), 3) # créer une case colony
            if c.type == 'colony':
                init_colony(c) # créer les fourmis
        while 1: # boucle principale
            time += 1
            if time > end_time:
                break # arrete la boucle dans un temps donné (end_time)
            self.clock.tick(FPS) # gère le nombre de frame per second
            event = pg.event.poll() # récupère le dernier évenement
            if event.type == pg.QUIT:
                break # si l'évenement est la croix en haut à droite on quitte la boucle
            if event.type == pg.MOUSEBUTTONUP: # evenement souris
                for c in self.cell_group:
                    c.check_click(event.pos, event.button) # position et type du click souris
            self.gameDisplay.fill((255,255,255,250)) # rempli l'écran
            self.all_group.update() # met à jours les cases de la grille et les fourmis
            self.all_group.draw(self.gameDisplay) # dessine les sprites
            pg.display.update()
        for cell in self.cell_group:
            if cell.type == 'colony':
                score = cell.food # score basé sur le nombre de nourriture ramené à la colony
        pg.quit()
        return score
 
class Cell(pg.sprite.DirtySprite):
    """ Class de case de la grille,
    elle peut être soit vide (none) donc propre à être marquée de phéromones (mark)
    ou nourriture (food) ou (colony) ou mur (wall)"""
    def __init__(self, coord, type = 'none'):
        pg.sprite.DirtySprite.__init__(self)
        self.image = pg.Surface((CELL_SIZE, CELL_SIZE), pg.SRCALPHA)
        self.coord = coord #coordonné de la cellule
        self.rect = self.image.get_rect()
        # rect.center position réel en x, y des coordonné du milieu de la case
        self.rect.center = self.coord.x*CELL_SIZE+CELL_SIZE/2, self.coord.y*CELL_SIZE+CELL_SIZE/2
        self.marks = {'colony':0,'food':0} # initialise les phéromone à zero
        self.type = type
        self.food = 0
 
    def update(self):
        self.rect.center = self.coord.x*CELL_SIZE+CELL_SIZE/2, self.coord.y*CELL_SIZE+CELL_SIZE/2
        if self.type == 'none': # si  la case est vide alors on vérifie les phéromones possiblement dessus
            self.update_marker()
            self.color_marker()
        elif self.type =='wall':
            self.color = WALL_COLOR
        elif self.type =='food':
            self.color = FOOD_COLOR
        elif self.type =='colony':
            self.color = COLONY_COLOR
        self.image.fill(self.color) # on rempli la cellule de la couleur definie par son type
 
    def pick(self):
        """ fonction lorsqu'une fourmi à trouvé une case type = food,
        elle lui enlève une unité de nourriture """
        self.food -= 1
        if self.food <= 0:
            self.type = 'none' # si il n'y à plus de nourriture la cell devient vide
 
    def drop(self):
        """ ajoute une unité de nourriture à la cellule (que si elle est une colony)"""
        self.food += 1
 
    def check_click(self, pos, button):
        """ fonction qui gère le changement du type d'une case,
        a la base que pour les événements de la souris, mais je l'utilise aussi pour
        initialiser automatiquement une colony et une food au départ de world.update """
        if self.rect.collidepoint(pos):
            if button == 1: # clique gauche
                if self.type == 'food':
                    self.type = 'none'
                else:
                    self.type = 'food'
                    self.reset_marker('food','colony')
                    self.food = 10000
            elif button == 3: # clique droit
                if self.type == 'colony':
                    self.type = 'none'
                else:
                    self.type = 'colony'
                    self.reset_marker('food','colony')
                    init_colony(self) # créer les fourmis
            elif button == 2: # clique molette
                if self.type == 'wall':
                    self.type = 'none'
                else:
                    self.type = 'wall'
                    self.reset_marker('food','colony')
 
 
    def reset_marker(self, type_0, type_1 = ''):
        """ supprime les phéromones (mark) présentent sur une cellule """
        self.marks[type_0] = 0
        if type_1 != '':
            self.marks[type_1] = 0
 
    def update_marker(self):
        """ met à jours les phéromones """
        self.marks['food'] -= COEF # les phéromones s'évaporent un peu à chaque frame
        self.marks['colony'] -= COEF
        if self.marks['food'] <= 0: self.reset_marker('food') # valeur minimale pas en dessous de zero
        elif self.marks['food'] >= MARK: self.marks['food'] = MARK # valeur maxi ne dépasse par MARK
        if self.marks['colony'] <= 0: self.reset_marker('colony') # valeur min à zero
        elif self.marks['colony'] >= MARK: self.marks['colony'] = MARK # valeur maxi ne dépasse par MARK
 
    def color_marker(self):
        """ choisi la couleur à afficher en fonction de l'intensité des phéromones présentes """
        if self.marks['food'] != 0 and self.marks['colony'] != 0:
            self.color = TO_FOOD_COLOR - TO_COLONY_COLOR
            # si les deux types de phéromones sont présentes, alors on mélange les deux couleurs
            self.color.a = int((((self.marks['food']+self.marks['colony'])/2)/MARK)*250)
            # on joue sur la valeur alpha pour définir la transparence de la couleurs
            # plus mark est faible plus c'est transparent et inversement
        elif self.marks['colony'] == 0 and self.marks['food'] != 0:
            self.color = TO_FOOD_COLOR
            self.color.a = int((self.marks['food']/MARK)*250)
        elif self.marks['food'] == 0 and self.marks['colony'] != 0:
            self.color = TO_COLONY_COLOR
            self.color.a = int((self.marks['colony']/MARK)*250)
        elif self.marks['food'] == 0 and self.marks['colony'] == 0 and self.type == 'none':
            self.color = WHITE
            self.color.a = 0
 
class Ant(pg.sprite.DirtySprite):
    """ gère comportement des fourmis """
    def __init__(self, FORCE, SPEED, COEF, MARK, INTENSITY, LIBERTY_MOVE, pos, actual_cell):
        pg.sprite.DirtySprite.__init__(self)
        self.image = pg.Surface((ANT_SIZE, ANT_SIZE), pg.SRCALPHA)
        self.image.fill(pg.Color(55,50,68,250))
        self.pos = pos
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        # les quatres variables suivantes gèrent le déplacement de la fourmi
        self.vel = Vec(random.choice(world.allowed_values), random.choice(world.allowed_values))
        self.acc = Vec(0,0)
        self.max_force = FORCE
        self.max_speed = SPEED
 
        self.goal = 'food' # défini le but de la fourmi soit food, soit colony
        self.actual_cell = actual_cell # défini la case sur laquelle la fourmi est
        self.last_cell = 0
        self.LIBERTY_MOVE = LIBERTY_MOVE # il y a 1 chance sur LIBERTY_MOVE pour que la fourmi ne suivent pas les phéromones
        self.INTENSITY = INTENSITY # le nombre de phéromones à déposer sur une case
 
    def update(self):
        self.actual_cell = pg.sprite.spritecollideany(self,  world.cell_group)
        if self.actual_cell != self.last_cell:
            self.leave_mark() # dépose ses phéromones
            self.ecart = self.pos - self.actual_cell.rect.center # défini si fourmi est + ou - au centre de la cellule actuelle
            if self.ecart.x <= 0.5 or self.ecart.x >= -0.5 and self.ecart.y <= 0.5 or self.ecart.y >= -0.5:
                                    # si fourmi est au centre de la case
                if self.check_goal() == False: # si on est pas sur une case food ou colony en fonction
                    self.target_cell = self.desired_move() # alors cherche la prochaine case pour bouger
                else: self.target_cell = self.last_cell.rect.center # sinon la fourmi fait demi tour pour retrouver sa route
            self.last_cell = self.actual_cell # défini la dernière case visité
        self.update_forces() # gère le mouvement de la fourmi ( vélocité, accélération, vitesse)
        self.seek(self.target_cell)
 
    def update_forces(self):
        """ met à jour les vecteurs de déplacement de la fourmi
        c'est comme un steering agent"""
        self.rect.center = self.pos
        self.pos += self.vel
        self.vel += self.acc
        if self.vel.magnitude() > self.max_speed:
            self.vel.x, self.vel.y = self.max_speed*self.vel.x/self.vel.magnitude(), self.max_speed*self.vel.y/self.vel.magnitude()
 
    def leave_mark(self):
        """ dépose ses phéromones"""
        if self.actual_cell.type == 'none':
            self.actual_cell.marks[self.goal] += self.INTENSITY
 
    def check_goal(self):
        """ vérifie si la case actuelle n'est pas son but"""
        if self.goal == self.actual_cell.type:
            if self.goal == 'food':
                self.goal = 'colony'
                self.actual_cell.pick() # prend une nourriture dans la case nourriture
                return True
            elif self.goal == 'colony':
                self.goal = 'food'
                self.actual_cell.drop() # dépose nourriture dans la colony
                return True
        return False
 
    def desired_move(self):
        """ défini la meilleure case où aller """
        directions = [self.actual_cell.coord + Vec(-1,0), self.actual_cell.coord + Vec(1,0), self.actual_cell.coord + Vec(0,-1), self.actual_cell.coord + Vec(0,1)] # left right top bottom
        real_direction = []
        max_intens = 0
        for arrow in directions: # pour les quatres cases gauche, droite, haut, bas
            for cell in  world.cell_group:
                if arrow == cell.coord:
                    if cell.type == self.goal:
                        return cell.rect.center # si case est le but directement la proposer comme prochain mouvement
                    elif cell.type != 'wall' and cell != self.last_cell: # si case n'est pas un mur où la case précedente
                        if self.goal == 'colony':
                            mark_goal = 'food'
                        elif self.goal == 'food':
                            mark_goal = 'colony'
                        if cell.marks[mark_goal] > max_intens: # si cette case est plus intense en phéromone
                            max_intens = cell.marks[mark_goal]
                            best_cell = cell # on l'ajoute comme meilleur choix pour le prochain mouvement
                        real_direction.append(cell)
        liberty = random.randrange(1, self.LIBERTY_MOVE) # défini un certain degré de liberté pour choisir une case au hasard
        if max_intens == 0 or liberty == 1: # si pas de phéromone autour de soit ou si liberty ==1 c-a-d que c'est l'option choix au hasard
            if len(real_direction) == 1: # si qu'une seule case possible pour le prochain mouvement
                alea_cell = real_direction[0]
            else:
                alea_cell = random.choice(real_direction) # sinon on choisi au hasard la prochaine case parmis les possibles
            return alea_cell.rect.center
        else:
            return best_cell.rect.center # sinon on choisi la case la plus intense en phéromones
 
    def seek(self, target):
        """ défini le mouvement de la fourmi en tant que steering agent en changeant son vecteur d'accéléaration """
        self.desired = (target - self.pos).normalize() * self.max_speed
        steering_force = self.desired - self.vel
        if steering_force.magnitude() > self.max_force:
            steering_force = self.max_force*steering_force/steering_force.magnitude()
        self.acc = steering_force
 
def init_colony(cell):
    """ quand on instancie une case colony, on créer les objets fourmis """
    for i in range(ANT_NB):
        ant = Ant(FORCE, SPEED, COEF, MARK, INTENSITY, LIBERTY_MOVE, Vec(cell.rect.center), cell)
        world.ant_group.add(ant)
        world.all_group.add(ant)
 
WHITE = pg.Color(255,255,255,0)
WALL_COLOR = pg.Color(0,0,0,250)
COLONY_COLOR = pg.Color(67,46,163,250)
FOOD_COLOR = pg.Color(29,129,18,250)
TO_FOOD_COLOR = pg.Color(109,105,219,250)
TO_COLONY_COLOR = pg.Color(250,105,109,250)
 
if __name__ == "__main__": # définition des constances
    WINDOWS = Vec(400,400)
    FPS = 60
    CELL_SIZE = 10
    ANT_SIZE = 3
    ANT_NB = 80
    FORCE = 5
    SPEED = 2.2
    COEF = 0.1
    MARK = 500
    INTENSITY = 10
    LIBERTY_MOVE = 15
    world = World() # initie la grille et pygame
    score = world.update(FPS, 100000)
