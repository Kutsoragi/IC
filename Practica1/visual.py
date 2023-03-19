#!/usr/bin/env python3
import pygame
import sys
import random
from tkinter import Tk, messagebox
from constants import Colours
from algorithms import AStar


class MessageBox:

    def __init__(self):
        self.window = Tk()
        self.window.wm_withdraw()

    def show_error(self, msg):
        messagebox.showerror("Error", msg)

    def show_info(self, msg):
        messagebox.showinfo("Done", msg)

    def update_and_destroy(self):
        self.window.update()
        self.window.destroy()


class Visual:

    def __init__(self, font):
        self.mark_mode_colours = {
            0: Colours.BLUE.value,
            1: Colours.LIGHT_GREEN.value,
            2: Colours.BLACK.value,
            3: Colours.WHITE.value,
            6: Colours.PURPLE.value,
            7: Colours.YELLOW.value
        }
        self.window_size = 535
        self.screen = pygame.display.set_mode([self.window_size + 8, self.window_size + 35])
        self.screen.fill(Colours.PURE_BLACK.value)
        self.edit_mode = -1
        self.grid_size = 20
        self.algo_name = "A*"
        self.font = font
        self.start_cell = self.end_cell = None
        self.start_xy = self.end_xy = None
        self.edited_squares = []
        self.squares = []
        self.buttons = []
        self.way_points = []
        self.penalization = []

        def setup_grid():
            margin = 1
            margin_removed = self.window_size - self.grid_size * margin
            square_size = round(margin_removed / self.grid_size)

            for r in range(self.grid_size):
                sublist = []
                for c in range(self.grid_size):
                    x = margin + c * (margin + square_size)
                    y = margin + r * (margin + square_size)
                    rect = pygame.Rect(x, y, square_size, square_size)
                    pygame.draw.rect(self.screen, Colours.WHITE.value, rect)
                    sublist.append(rect)

                self.squares.append(sublist)

            self.grid = [[1 for i in range(self.grid_size)] for ii in range(self.grid_size)]

        

        def setup_buttons_and_labels():
            start_label = self.font.render("Set Start", 1, Colours.WHITE.value)
            end_label = self.font.render("Set End", 1, Colours.WHITE.value)
            obs_label = self.font.render("Set Obs.", 1, Colours.WHITE.value)
            random_label = self.font.render("Randomize", 1, Colours.WHITE.value)
            reset_label = self.font.render("Reset", 1, Colours.WHITE.value)
            findpath_label = self.font.render("Find Path", 1, Colours.WHITE.value)
            waypoints_label = self.font.render("Way Points", 1, Colours.WHITE.value)
            penalization_label = self.font.render("Set Penalization", 1, Colours.WHITE.value)

            labels = [start_label, end_label, obs_label, random_label, reset_label, findpath_label, waypoints_label, penalization_label]
            # edit_modes:   0         1          2             3            4            5             6                     7

            button_margin = 3
            text_width_margin = 4
            text_height_margin = 2
            next_pos = (2, 545)

            for l in labels:
                l_w, l_h = l.get_size()
                bg_w, bg_h = l_w + 2 * text_width_margin, l_h + 2 * text_height_margin
                bg_button = pygame.Rect(next_pos[0], next_pos[1], bg_w, bg_h)
                pygame.draw.rect(self.screen, Colours.WHITE.value, bg_button, 1)
                self.buttons.append(bg_button)

                l_rect = l.get_rect(center=(next_pos[0] + bg_w // 2, next_pos[1] + bg_h // 2))
                self.screen.blit(l, l_rect)

                next_pos = (next_pos[0] + l_w + 2 * text_width_margin + button_margin, next_pos[1])


        setup_grid()
        setup_buttons_and_labels()

    def check_button_highlight(self, mouse):
        for b in self.buttons:
            if b.collidepoint(mouse):
                pygame.draw.rect(self.screen, Colours.GRAY.value, b.copy(), 1)
            else:
                pygame.draw.rect(self.screen, Colours.WHITE.value, b.copy(), 1)

    def check_paint_obstacle(self, mouse):
        if self.edit_mode == 2:
            for y, r in enumerate(self.squares):
                for x, s in enumerate(r):
                    if s.collidepoint(mouse):
                        if (y, x) not in self.way_points and (y, x) not in self.penalization:
                            pygame.draw.rect(self.screen, Colours.BLACK.value, s)
                            self.grid[y][x] = sys.maxsize

    def check_button_actions(self, mouse):

        def reset_grid():
            for r in self.squares:
                for s in r:
                    pygame.draw.rect(self.screen, Colours.WHITE.value, s)

            self.grid = [[1 for i in range(self.grid_size)] for ii in range(self.grid_size)]
            self.start_cell = self.end_cell = None
            self.start_xy = self.end_xy = None
            self.edited_squares = []
            self.way_points = []
            self.penalization = []

        def randomize_grid():
            reset_grid()
            for y, r in enumerate(self.squares):
                for x, s in enumerate(r):
                    if random.getrandbits(1):
                        pygame.draw.rect(self.screen, Colours.BLACK.value, s)
                        self.grid[y][x] = sys.maxsize

        #llama al algoritmo
        def run_algo():
        
            msgbox = MessageBox()

            #si hay una celda de inicio y al menos una celda de final seleccionada te deja iniciarlo
            if self.start_cell and self.end_cell:
                #inicializa el algortimo
                valido = True
                if len(self.way_points) != 0:
                    suma = 0
                    w1=self.start_xy
                    for wayPoint in self.way_points:
                        a_star = AStar(self.screen, w1,wayPoint, self.squares, self.grid, self.edited_squares, self.way_points, self.penalization)
                        res, self.edited_squares = a_star.find_path()
                        if res:
                            suma = suma + res
                        else:
                            valido = False
                        w1=wayPoint
                    a_star = AStar(self.screen, w1,self.end_xy, self.squares, self.grid, self.edited_squares, self.way_points, self.penalization)
                    res, self.edited_squares = a_star.find_path()
                    if res:
                        suma = suma + res
                    else:
                        valido = False
                else:
                    a_star = AStar(self.screen, self.start_xy,self.end_xy, self.squares, self.grid, self.edited_squares, self.way_points, self.penalization)
                    suma, self.edited_squares = a_star.find_path()
                    if suma == 0:
                        valido = False

                #encuentra el camino mínimo devolviendo la distancia y las celdas que ha recorrido

                if not valido:
                    msgbox.show_error("No possible path.")
                else:
                    msgbox.show_info("There is a path.")
                    
            else:
                msgbox.show_error("Start or end not set.")
            
            msgbox.update_and_destroy()

        #ejecuta la opción seleccionada 
        for i, b in enumerate(self.buttons):
            if b.collidepoint(mouse):
                if i == 3:
                    randomize_grid()
                elif i == 4:
                    reset_grid()
                elif i == 5:
                    run_algo()                
                    
                self.edit_mode = i

    #una especie de listener que mira si se selecciona alguna celda para actualizar nuestras variables
    def check_cell_actions(self, mouse):

        ##celda de inicio
        def set_start_cell():
            if (i, j) not in self.way_points and (i, j) not in self.penalization:
                if self.start_cell:
                    pygame.draw.rect(self.screen, Colours.WHITE.value, self.start_cell)

                pygame.draw.rect(self.screen, self.mark_mode_colours[self.edit_mode], s)
                self.start_cell = s
                self.start_xy = (i, j)

                if self.grid[i][j] == sys.maxsize:
                    self.grid[i][j] = 1

        #celda de fin aqui 
        def set_end_cell():
            if (i, j) not in self.way_points and (i, j) not in self.penalization:
                if self.end_cell:
                    pygame.draw.rect(self.screen, Colours.WHITE.value, self.end_cell)

                pygame.draw.rect(self.screen, self.mark_mode_colours[self.edit_mode], s)
                self.end_cell = s
                self.end_xy = (i, j)

                if self.grid[i][j] == sys.maxsize:
                    self.grid[i][j] = 1
        
        def waypoints_cell():

            number_font = pygame.font.SysFont( None, 16 )   # default font, size 16
            
            if (i, j) not in self.way_points and (i, j) not in self.penalization:
                pygame.draw.rect(self.screen, self.mark_mode_colours[self.edit_mode], s)
                number_image = number_font.render( str(len(self.way_points)+ 1), True, Colours.BLACK.value, Colours.WHITE.value )
                self.screen.blit( number_image, s ) 
                self.way_points.append((i,j))

                if self.grid[i][j] == sys.maxsize:
                    self.grid[i][j] = 1
                    
        def penalization_cell():
            if (i, j) not in self.penalization and (i, j) not in self.way_points:
                pygame.draw.rect(self.screen, self.mark_mode_colours[self.edit_mode], s)
                self.penalization.append((i,j))
            


        for i, r in enumerate(self.squares):
            for j, s in enumerate(r):
                if s.collidepoint(mouse) and self.edit_mode in [0, 1, 6,7]:
                    if self.edit_mode == 0:
                        set_start_cell()
                    elif self.edit_mode == 1:
                        set_end_cell()
                    elif self.edit_mode == 6:
                        waypoints_cell()
                    elif self.edit_mode == 7:
                        penalization_cell()

