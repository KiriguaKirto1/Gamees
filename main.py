#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Heartwood-inspired Forest Map Generator / Viewer
------------------------------------------------
Original procedural map tool for a cozy top-down RPG. It does not copy any
official map or asset; it only aims for a similar *composition idea*:
left river, dense pine forest, earthy clearings, small village, camp area,
rocky cliffs/mountains and layered objects.

Controls:
WASD / arrows = move camera player
R = regenerate map
G = debug grid
H = hitboxes
F5 = export full map as generated_map.png
ESC = quit
"""

import math
import os
import random
from pathlib import Path
import pygame

SCREEN_W, SCREEN_H = 1280, 720
FPS = 60
TILE = 48
MAP_W, MAP_H = 120, 78
TITLE = "Forest RPG Map Generator - Reference Style V3"

BASE = Path(__file__).resolve().parent
ASSETS = BASE / "assets"
TILES_DIR = ASSETS / "tiles"
OBJECTS_DIR = ASSETS / "objects"

# tile names available from the previous extracted pack
GRASS_DARK = "grass_dark"
GRASS_LIGHT = "grass_light"
GRASS_MID = "grass_mid"
GRASS_YELLOW = "grass_yellow"
DIRT = "dirt_cracked"
WATER = "water"
WATER_DEEP = "water_deep"
SAND = "sand"
STONE_1 = "stone_1"
STONE_2 = "stone_2"
STONE_3 = "stone_3"
COBBLE_BROWN = "cobble_brown"
COBBLE_BROWN_ALT = "cobble_brown_alt"
COBBLE_GRAY = "cobble_gray_1"
COBBLE_GRAY_2 = "cobble_gray_2"

WATER_TILES = {WATER, WATER_DEEP}
ROCK_TILES = {STONE_1, STONE_2, STONE_3, COBBLE_GRAY, COBBLE_GRAY_2, COBBLE_BROWN, COBBLE_BROWN_ALT}


def clamp(v, a, b):
    return max(a, min(b, v))


def dist(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def load_png(path, size=None, crop_inner=False):
    if not path.exists():
        surf = pygame.Surface(size or (TILE, TILE), pygame.SRCALPHA)
        surf.fill((255, 0, 255, 160))
        return surf
    img = pygame.image.load(str(path)).convert_alpha()
    if crop_inner and img.get_width() >= 40 and img.get_height() >= 40:
        # These generated tiles have strong illustrated borders. Cropping the inner
        # area makes repeated tiles less grid-like.
        margin = max(4, int(min(img.get_width(), img.get_height()) * 0.10))
        rect = pygame.Rect(margin, margin, img.get_width() - margin * 2, img.get_height() - margin * 2)
        img = img.subsurface(rect).copy()
    if size:
        img = pygame.transform.smoothscale(img, size)
    return img


def draw_pine(size=(76, 124), shade=0):
    w, h = size
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.ellipse(s, (0, 0, 0, 45), (int(w*.18), int(h*.82), int(w*.64), int(h*.12)))
    pygame.draw.rect(s, (104, 68, 38), (int(w*.43), int(h*.66), int(w*.14), int(h*.25)), border_radius=4)
    pygame.draw.rect(s, (55, 35, 22), (int(w*.43), int(h*.66), int(w*.14), int(h*.25)), 2, border_radius=4)
    greens = [(18+shade, 88+shade, 52+shade), (22+shade, 114+shade, 62+shade), (46+shade, 148+shade, 80+shade)]
    layers = [(0.13, 0.18, 0.87, 0.48), (0.08, 0.34, 0.92, 0.68), (0.04, 0.50, 0.96, 0.86)]
    for i, (x1, y1, x2, y2) in enumerate(layers):
        pts = [(w//2, int(y1*h)), (int(x2*w), int(y2*h)), (int(x1*w), int(y2*h))]
        pygame.draw.polygon(s, greens[i], pts)
        pygame.draw.polygon(s, (8, 47, 30), pts, 2)
        pygame.draw.line(s, (100, 185, 108), (w//2 - 7, int(y1*h + 8)), (w//2 - 19, int(y2*h - 12)), 2)
        pygame.draw.line(s, (9, 62, 38), (w//2 + 8, int(y1*h + 12)), (w//2 + 23, int(y2*h - 12)), 2)
    pygame.draw.ellipse(s, greens[2], (int(w*.40), int(h*.06), int(w*.20), int(h*.16)))
    pygame.draw.ellipse(s, (8, 47, 30), (int(w*.40), int(h*.06), int(w*.20), int(h*.16)), 2)
    return s


def draw_cloud(size=(190, 70)):
    w, h = size
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    for off, alpha, col in [(4, 45, (155, 155, 155)), (0, 225, (255, 255, 255))]:
        c = (*col, alpha)
        pygame.draw.ellipse(s, c, (8, 26+off, int(w*.32), int(h*.52)))
        pygame.draw.ellipse(s, c, (int(w*.24), 8+off, int(w*.43), int(h*.66)))
        pygame.draw.ellipse(s, c, (int(w*.52), 20+off, int(w*.42), int(h*.60)))
        pygame.draw.rect(s, c, (int(w*.19), int(h*.50)+off, int(w*.56), int(h*.34)))
    return s


def draw_red_roof_house(size=(170, 150)):
    w, h = size
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.ellipse(s, (0,0,0,45), (int(w*.13), int(h*.84), int(w*.72), int(h*.12)))
    pygame.draw.rect(s, (204,184,146), (int(w*.20), int(h*.43), int(w*.60), int(h*.43)))
    pygame.draw.rect(s, (88,63,42), (int(w*.20), int(h*.43), int(w*.60), int(h*.43)), 3)
    for x in (0.29, 0.50, 0.70):
        pygame.draw.rect(s, (112,79,49), (int(w*x), int(h*.45), 6, int(h*.40)))
    pygame.draw.line(s, (112,79,49), (int(w*.20), int(h*.60)), (int(w*.80), int(h*.60)), 5)
    pygame.draw.rect(s, (100,88,78), (int(w*.28), int(h*.23), int(w*.10), int(h*.22)))
    pygame.draw.rect(s, (62,50,44), (int(w*.28), int(h*.23), int(w*.10), int(h*.22)), 2)
    roof = [(int(w*.11), int(h*.45)), (int(w*.50), int(h*.07)), (int(w*.89), int(h*.45))]
    pygame.draw.polygon(s, (224, 92, 63), roof)
    pygame.draw.polygon(s, (92, 46, 35), roof, 3)
    pygame.draw.polygon(s, (242,112,78), [(int(w*.17), int(h*.45)), (int(w*.50), int(h*.13)), (int(w*.83), int(h*.45))])
    pygame.draw.line(s, (255,160,110), (int(w*.50), int(h*.07)), (int(w*.50), int(h*.45)), 3)
    pygame.draw.rect(s, (245,235,158), (int(w*.29), int(h*.58), int(w*.13), int(h*.13)))
    pygame.draw.rect(s, (66,48,38), (int(w*.29), int(h*.58), int(w*.13), int(h*.13)), 3)
    pygame.draw.rect(s, (67,172,202), (int(w*.53), int(h*.64), int(w*.17), int(h*.24)), border_radius=4)
    pygame.draw.rect(s, (69,48,38), (int(w*.53), int(h*.64), int(w*.17), int(h*.24)), 3, border_radius=4)
    pygame.draw.circle(s, (240,207,77), (int(w*.66), int(h*.76)), 2)
    pygame.draw.rect(s, (151,135,116), (int(w*.42), int(h*.88), int(w*.38), int(h*.07)), border_radius=4)
    pygame.draw.rect(s, (73,65,58), (int(w*.42), int(h*.88), int(w*.38), int(h*.07)), 2, border_radius=4)
    return s


class AssetBank:
    def __init__(self):
        self.tiles = {}
        self.objects = {}
        self.generated = {}
        self.load_all()

    def load_all(self):
        for p in sorted(TILES_DIR.glob("*.png")):
            self.tiles[p.stem] = load_png(p, (TILE, TILE), crop_inner=True)
        fallback = {
            GRASS_DARK:(71,148,62), GRASS_MID:(91,162,65), GRASS_LIGHT:(119,176,70), GRASS_YELLOW:(157,174,70),
            DIRT:(139,103,70), WATER:(58,171,211), WATER_DEEP:(35,125,184), SAND:(210,181,116),
            STONE_1:(125,126,122), STONE_2:(130,130,126), STONE_3:(118,118,114), COBBLE_BROWN:(137,93,55),
            COBBLE_BROWN_ALT:(153,105,61), COBBLE_GRAY:(114,116,112), COBBLE_GRAY_2:(126,126,121)
        }
        for name, color in fallback.items():
            if name not in self.tiles:
                s = pygame.Surface((TILE, TILE), pygame.SRCALPHA); s.fill(color)
                self.tiles[name] = s
        for p in sorted(OBJECTS_DIR.glob("*.png")):
            self.objects[p.stem] = load_png(p)
        # runtime-generated assets, closer to the forest screenshot composition
        self.generated["pine_1"] = draw_pine((72, 124), 0)
        self.generated["pine_2"] = draw_pine((64, 112), 7)
        self.generated["pine_3"] = draw_pine((82, 138), -6)
        self.generated["cloud_1"] = draw_cloud((210, 78))
        self.generated["cloud_2"] = draw_cloud((160, 62))
        self.generated["red_roof_house"] = draw_red_roof_house((176, 156))

    def tile(self, name):
        return self.tiles.get(name, self.tiles[GRASS_DARK])

    def obj(self, name, fallback=None):
        return self.objects.get(name) or self.generated.get(name) or self.objects.get(fallback or "") or self.generated.get(fallback or "") or self.make_missing()

    def make_missing(self):
        s = pygame.Surface((TILE, TILE), pygame.SRCALPHA)
        s.fill((255, 0, 255, 160))
        return s


class WorldObject:
    def __init__(self, name, tx, ty, image, solid=True, kind="object", offset=(0,0), scale=1.0):
        if scale != 1.0:
            image = pygame.transform.smoothscale(image, (max(1, int(image.get_width()*scale)), max(1, int(image.get_height()*scale))))
        self.name, self.image, self.solid, self.kind = name, image, solid, kind
        self.w, self.h = image.get_size()
        self.x = int(tx*TILE + offset[0])
        self.y = int(ty*TILE - max(0, self.h-TILE) + offset[1])
        self.hitbox = self.make_hitbox()

    def make_hitbox(self):
        if self.kind in ("tree", "pine"):
            return pygame.Rect(self.x + int(self.w*.34), self.y + int(self.h*.75), int(self.w*.30), int(self.h*.18))
        if self.kind == "house":
            return pygame.Rect(self.x + int(self.w*.15), self.y + int(self.h*.63), int(self.w*.70), int(self.h*.30))
        if self.kind in ("rock", "cliff", "ruin"):
            return pygame.Rect(self.x + int(self.w*.12), self.y + int(self.h*.47), int(self.w*.76), int(self.h*.46))
        if self.kind == "fence":
            return pygame.Rect(self.x + int(self.w*.04), self.y + int(self.h*.36), int(self.w*.92), int(self.h*.43))
        return pygame.Rect(self.x + int(self.w*.16), self.y + int(self.h*.46), int(self.w*.68), int(self.h*.42))

    @property
    def draw_y(self): return self.hitbox.bottom

    def draw(self, screen, cam):
        screen.blit(self.image, (self.x-cam.x, self.y-cam.y))


class Camera:
    def __init__(self): self.x = 0; self.y = 0
    def update(self, target):
        tx = target.centerx - SCREEN_W//2; ty = target.centery - SCREEN_H//2
        self.x += (tx-self.x)*0.13; self.y += (ty-self.y)*0.13
        self.x = int(clamp(self.x, 0, max(0, MAP_W*TILE-SCREEN_W)))
        self.y = int(clamp(self.y, 0, max(0, MAP_H*TILE-SCREEN_H)))


class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 32, 42)
        self.speed = 245
    @property
    def draw_y(self): return self.rect.bottom
    def move(self, dx, dy, solid_rects, blocked):
        old = self.rect.copy(); self.rect.x += dx
        if self.collides(solid_rects, blocked): self.rect.x = old.x
        old = self.rect.copy(); self.rect.y += dy
        if self.collides(solid_rects, blocked): self.rect.y = old.y
    def collides(self, solid_rects, blocked):
        if self.rect.left < 0 or self.rect.top < 0 or self.rect.right > MAP_W*TILE or self.rect.bottom > MAP_H*TILE: return True
        tx0, tx1 = max(0,self.rect.left//TILE), min(MAP_W-1,self.rect.right//TILE)
        ty0, ty1 = max(0,self.rect.top//TILE), min(MAP_H-1,self.rect.bottom//TILE)
        for y in range(ty0, ty1+1):
            for x in range(tx0, tx1+1):
                if blocked[y][x] and self.rect.colliderect(pygame.Rect(x*TILE,y*TILE,TILE,TILE)):
                    return True
        return any(self.rect.colliderect(r) for r in solid_rects)
    def draw(self, screen, cam):
        x,y = self.rect.x-cam.x, self.rect.y-cam.y
        pygame.draw.ellipse(screen,(0,0,0,75),(x+2,y+34,30,10))
        pygame.draw.ellipse(screen,(32,52,74),(x+5,y+14,23,25))
        pygame.draw.circle(screen,(236,194,145),(x+16,y+12),12)
        pygame.draw.ellipse(screen,(190,200,206),(x+4,y,25,14))
        pygame.draw.circle(screen,(60,45,35),(x+12,y+11),2); pygame.draw.circle(screen,(60,45,35),(x+21,y+11),2)
        pygame.draw.rect(screen,(80,52,34),(x+8,y+34,7,8)); pygame.draw.rect(screen,(80,52,34),(x+19,y+34,7,8))


class MapGenerator:
    def __init__(self, assets):
        self.assets = assets
        self.rng = random.Random()
        self.grid = [[GRASS_MID for _ in range(MAP_W)] for _ in range(MAP_H)]
        self.blocked = [[False for _ in range(MAP_W)] for _ in range(MAP_H)]
        self.objects = []
        self.path = set(); self.water = set(); self.cliff = set()
        self.player_spawn = (32*TILE, 52*TILE)

    def inb(self,x,y): return 0 <= x < MAP_W and 0 <= y < MAP_H
    def set_tile(self,x,y,tile,blocked=False):
        if self.inb(x,y): self.grid[y][x]=tile; self.blocked[y][x]=blocked
    def noise(self,x,y): return math.sin(x*.17)+math.cos(y*.21)+math.sin((x+y)*.07)

    def regenerate(self, seed=None):
        self.rng.seed(seed if seed is not None else random.randint(1, 9999999))
        self.grid = [[GRASS_MID for _ in range(MAP_W)] for _ in range(MAP_H)]
        self.blocked = [[False for _ in range(MAP_W)] for _ in range(MAP_H)]
        self.objects=[]; self.path=set(); self.water=set(); self.cliff=set()
        self.base_terrain(); self.left_river(); self.earth_clearings(); self.mountains_and_cliffs(); self.paths()
        self.village(); self.dense_forest(); self.camp_and_props(); self.water_decor(); self.clouds()

    # ---------- terrain ----------
    def paint_blob(self,cx,cy,rx,ry,tiles,blocked=False,jitter=.12):
        for y in range(int(cy-ry-3), int(cy+ry+4)):
            for x in range(int(cx-rx-3), int(cx+rx+4)):
                if not self.inb(x,y): continue
                dx=(x-cx)/max(1,rx); dy=(y-cy)/max(1,ry)
                if dx*dx + dy*dy + self.rng.uniform(-jitter,jitter) <= 1:
                    self.set_tile(x,y,self.rng.choice(tiles),blocked)

    def base_terrain(self):
        for y in range(MAP_H):
            for x in range(MAP_W):
                n = self.noise(x,y)+self.rng.uniform(-.6,.6)
                if n < -.6: t=GRASS_DARK
                elif n < .1: t=GRASS_MID
                elif n < .75: t=GRASS_LIGHT
                else: t=GRASS_YELLOW
                self.set_tile(x,y,t,False)
        # broad green/yellow patches to kill grid repetition
        for _ in range(24):
            self.paint_blob(self.rng.randint(8,MAP_W-8), self.rng.randint(6,MAP_H-6), self.rng.randint(5,15), self.rng.randint(4,11), self.rng.choice([[GRASS_DARK,GRASS_MID],[GRASS_LIGHT,GRASS_YELLOW],[GRASS_MID,GRASS_LIGHT]]), False, .24)

    def left_river(self):
        center=7
        for y in range(MAP_H):
            edge = center + int(math.sin(y*.15)*3) + int(math.sin(y*.39)*2)
            width = 7 + int(math.sin(y*.08)*2)
            for x in range(0, max(3, edge+width)):
                if x < edge+width + self.rng.randint(-1,1):
                    self.set_tile(x,y, WATER_DEEP if x < edge+2 else WATER, True); self.water.add((x,y))
            # sandy/grass bank
            for x in range(edge+width, edge+width+3):
                if self.inb(x,y) and self.rng.random()<.8:
                    self.set_tile(x,y,self.rng.choice([SAND,GRASS_LIGHT,GRASS_YELLOW]),False)
        # little dock/bridge at lower-left, similar composition but original
        for y in range(58,61):
            for x in range(0,12):
                if self.inb(x,y):
                    self.set_tile(x,y,DIRT,False); self.water.discard((x,y)); self.path.add((x,y))

    def earth_clearings(self):
        # main forest dirt/clearing similar to the reference: large brown area center/top
        self.paint_blob(63,25,34,21,[DIRT,COBBLE_BROWN,COBBLE_BROWN_ALT,GRASS_DARK],False,.20)
        self.paint_blob(60,27,26,15,[DIRT,DIRT,GRASS_DARK],False,.17)
        # village clearing lower-left
        self.paint_blob(33,54,22,15,[GRASS_YELLOW,GRASS_LIGHT,DIRT],False,.22)
        # small meadow around river
        self.paint_blob(15,46,12,13,[GRASS_LIGHT,GRASS_YELLOW],False,.20)

    def mountains_and_cliffs(self):
        # top and right rough cliff/mountain masses; blocked only on darker rock core
        for y in range(0, MAP_H):
            for x in range(MAP_W):
                h = 0
                for cx,cy,rx,ry,w in [(66,1,50,13,1.0),(100,12,28,18,.9),(95,33,18,13,.55)]:
                    dx=(x-cx)/rx; dy=(y-cy)/ry
                    h += max(0,1-(dx*dx+dy*dy))*w
                h += self.rng.uniform(-.08,.08)
                if h>.82:
                    self.set_tile(x,y,self.rng.choice([COBBLE_BROWN,COBBLE_BROWN_ALT,STONE_2]),True); self.cliff.add((x,y))
                elif h>.50:
                    self.set_tile(x,y,self.rng.choice([DIRT,COBBLE_BROWN,GRASS_DARK]),False)
        # stony work camp clearing inside mountains
        self.paint_blob(71,21,12,8,[DIRT,STONE_1,COBBLE_GRAY,COBBLE_BROWN],False,.18)

    def carve_path(self,a,b,width=2):
        x,y=a; bx,by=b; safety=0
        while (x,y)!=(bx,by) and safety<3000:
            safety+=1
            for yy in range(y-width-1,y+width+2):
                for xx in range(x-width-1,x+width+2):
                    if not self.inb(xx,yy): continue
                    if dist((xx,yy),(x,y)) <= width+self.rng.random()*.65 and (xx,yy) not in self.water:
                        self.set_tile(xx,yy,DIRT,False); self.path.add((xx,yy))
            if self.rng.random()<.54: x += 1 if x<bx else -1 if x>bx else 0
            else: y += 1 if y<by else -1 if y>by else 0

    def paths(self):
        hub=(35,54)
        for target in [(70,22),(88,33),(20,45),(12,59),(52,38)]:
            self.carve_path(hub,target,2)
        # paths inside camp
        self.carve_path((58,27),(76,21),1); self.carve_path((70,22),(82,18),1)

    # ---------- object placement ----------
    def add_obj(self,name,tx,ty,img,solid=True,kind="object",offset=(0,0),scale=1.0):
        if not self.inb(tx,ty): return None
        obj=WorldObject(name,tx,ty,self.assets.obj(img),solid,kind,offset,scale)
        self.objects.append(obj); return obj

    def occupied(self,tx,ty,r=1.0):
        c=(tx*TILE+TILE/2,ty*TILE+TILE/2)
        for o in self.objects:
            if dist(c,o.hitbox.center) < r*TILE: return True
        return False

    def near_path(self,tx,ty,r=2):
        for yy in range(ty-r,ty+r+1):
            for xx in range(tx-r,tx+r+1):
                if (xx,yy) in self.path: return True
        return False

    def valid(self,tx,ty,avoid_path=True):
        if not self.inb(tx,ty): return False
        if self.grid[ty][tx] in WATER_TILES or self.blocked[ty][tx]: return False
        if avoid_path and self.near_path(tx,ty,1): return False
        if self.occupied(tx,ty,1.1): return False
        return True

    def village(self):
        self.add_obj("main_house",25,51,"red_roof_house",True,"house",scale=1.2)
        self.add_obj("small_house",39,48,"house_small",True,"house",scale=1.0)
        self.add_obj("shop",16,60,"shop_house",True,"house",scale=1.05)
        self.add_obj("well",37,58,"well",True,"object",scale=.9)
        self.add_obj("sign",22,58,"sign",False,"object")
        self.add_obj("barrel",20,55,"barrel",True,"object",scale=.8)
        self.add_obj("crate",42,55,"crate",True,"object",scale=.8)
        self.add_obj("campfire",31,59,"campfire",False,"deco",scale=.8)
        self.player_spawn=(34*TILE,55*TILE)
        # loose fence pieces like small settlement boundary
        for tx,ty,img in [(18,47,"fence_long"),(22,47,"fence_gate"),(45,50,"fence_curved"),(12,57,"fence_long"),(48,57,"fence_gate")]:
            self.add_obj("fence",tx,ty,img,True,"fence",scale=.85)
        # flowers around houses
        for _ in range(28):
            tx=self.rng.randint(14,48); ty=self.rng.randint(47,64)
            if self.valid(tx,ty,avoid_path=True):
                self.add_obj("flower",tx,ty,self.rng.choice(["flower_pink","flower_purple","flower_orange"]),False,"deco",(self.rng.randint(-13,13),self.rng.randint(-9,9)),.9)

    def dense_forest(self):
        # Avoid the village clearing and keep main paths legible.
        forbidden=[pygame.Rect(18,46,34,22), pygame.Rect(56,18,28,14)]
        def in_forbidden(tx,ty): return any(r.collidepoint(tx,ty) for r in forbidden)
        clusters=[(54,23,220,28),(84,18,140,21),(49,45,130,22),(20,25,80,18),(95,49,60,18)]
        for cx,cy,count,rad in clusters:
            tries=count*7; placed=0
            while placed<count and tries>0:
                tries-=1
                a=self.rng.random()*math.tau; d=(self.rng.random()**.55)*rad
                tx=int(cx+math.cos(a)*d); ty=int(cy+math.sin(a)*d)
                if not self.inb(tx,ty) or in_forbidden(tx,ty): continue
                if self.valid(tx,ty,avoid_path=True):
                    img=self.rng.choice(["pine_1","pine_2","pine_3"])
                    sc=self.rng.uniform(.82,1.12)
                    self.add_obj("pine",tx,ty,img,True,"pine",(self.rng.randint(-12,12),self.rng.randint(-10,10)),sc)
                    placed+=1
        # Broadleaf trees/bushes mixed near edges
        for _ in range(70):
            tx=self.rng.randint(9,MAP_W-5); ty=self.rng.randint(7,MAP_H-5)
            if self.valid(tx,ty,avoid_path=True) and not (18<tx<50 and 46<ty<66):
                img=self.rng.choice(["tree_1","tree_2","tree_3","bush","stump"])
                self.add_obj("tree",tx,ty,img,True if img!="bush" else True,"tree",(self.rng.randint(-8,8),self.rng.randint(-7,7)),self.rng.uniform(.75,1.0))

    def camp_and_props(self):
        # Work/camp clearing in upper center like the reference, but original.
        for tx,ty,img in [(67,22,"campfire"),(64,24,"crate"),(70,24,"barrel"),(73,23,"table"),(76,21,"sign"),(60,25,"well_alt")]:
            self.add_obj("camp",tx,ty,img, img not in ("campfire","sign"), "object", scale=.75)
        # rock debris around camp and mountains
        for _ in range(100):
            tx=self.rng.randint(55,105); ty=self.rng.randint(5,42)
            if self.valid(tx,ty,avoid_path=True):
                img=self.rng.choice(["rock","rock_pile","ruin_wall","stone_pillar"])
                kind="cliff" if img in ("rock_pile","ruin_wall") else "rock"
                self.add_obj("rock",tx,ty,img,True,kind,(self.rng.randint(-10,10),self.rng.randint(-6,6)),self.rng.uniform(.65,.95))
        # small ruins lower-right
        for _ in range(28):
            tx=self.rng.randint(79,101); ty=self.rng.randint(54,70)
            if self.valid(tx,ty,avoid_path=True):
                self.add_obj("ruin",tx,ty,self.rng.choice(["stone_pillar","ruin_wall","rock_pile"]),True,"ruin",scale=self.rng.uniform(.75,1.0))

    def water_decor(self):
        # rocks, flowers and dock-ish pieces near the riverbank
        for _ in range(46):
            y=self.rng.randint(5,MAP_H-6)
            # bank around x 9-17 depending on river shape
            x=self.rng.randint(10,18)
            if self.valid(x,y,avoid_path=True):
                img=self.rng.choice(["rock","flower_pink","flower_purple","bush","stump"])
                self.add_obj("bank",x,y,img,img in ("rock","bush","stump"),"rock" if img=="rock" else "deco",scale=self.rng.uniform(.7,1.0))
        for tx in range(3,11,2):
            self.add_obj("dock_fence",tx,59,"fence_long",True,"fence",scale=.7)

    def clouds(self):
        # Decorative high clouds; non-solid. They mimic the reference composition but are optional visual atmosphere.
        for tx,ty,img,sc in [(42,0,"cloud_1",1.1),(79,3,"cloud_2",1.0),(96,15,"cloud_1",.9),(22,2,"cloud_2",.9)]:
            self.add_obj("cloud",tx,ty,img,False,"deco",(0,0),sc)

    # ---------- draw / collision ----------
    def solid_rects(self): return [o.hitbox for o in self.objects if o.solid]

    def draw_ground(self, screen, cam, grid=False):
        sx=max(0,cam.x//TILE-2); ex=min(MAP_W,(cam.x+SCREEN_W)//TILE+3)
        sy=max(0,cam.y//TILE-2); ey=min(MAP_H,(cam.y+SCREEN_H)//TILE+3)
        for y in range(sy,ey):
            for x in range(sx,ex):
                screen.blit(self.assets.tile(self.grid[y][x]),(x*TILE-cam.x,y*TILE-cam.y))
                if grid: pygame.draw.rect(screen,(0,0,0,60),(x*TILE-cam.x,y*TILE-cam.y,TILE,TILE),1)
        # soft dark soil/forest tint overlays to make terrain feel like one painted region
        # (only visible in current viewport)
        # Keeping it simple: the tile palette already carries most detail.

    def draw_world(self, screen, cam, player, grid=False, hitboxes=False):
        self.draw_ground(screen,cam,grid)
        view=pygame.Rect(cam.x-260,cam.y-300,SCREEN_W+520,SCREEN_H+600)
        items=[o for o in self.objects if view.colliderect(pygame.Rect(o.x,o.y,o.w,o.h))]
        items.append(player)
        for o in sorted(items,key=lambda obj: obj.draw_y):
            o.draw(screen,cam)
            if hitboxes and hasattr(o,"hitbox"):
                pygame.draw.rect(screen,(255,60,50),o.hitbox.move(-cam.x,-cam.y),1)
        if hitboxes: pygame.draw.rect(screen,(50,220,255),player.rect.move(-cam.x,-cam.y),1)

    def export_full_map(self, filename="generated_map.png"):
        surf=pygame.Surface((MAP_W*TILE,MAP_H*TILE),pygame.SRCALPHA)
        cam=type("C",(),{"x":0,"y":0})()
        for y in range(MAP_H):
            for x in range(MAP_W): surf.blit(self.assets.tile(self.grid[y][x]),(x*TILE,y*TILE))
        for o in sorted(self.objects,key=lambda obj:obj.draw_y): surf.blit(o.image,(o.x,o.y))
        pygame.image.save(surf,str(BASE/filename))


class Game:
    def __init__(self):
        pygame.init()
        self.screen=pygame.display.set_mode((SCREEN_W,SCREEN_H))
        pygame.display.set_caption(TITLE)
        self.clock=pygame.time.Clock()
        self.font=pygame.font.SysFont("arial",18)
        self.big=pygame.font.SysFont("arial",28,bold=True)
        self.assets=AssetBank(); self.map=MapGenerator(self.assets); self.map.regenerate()
        self.player=Player(*self.map.player_spawn); self.cam=Camera()
        self.grid=False; self.hitboxes=False
        self.msg="V3: rio à esquerda, floresta densa, clareira, vila e montanhas. R regenera | F5 exporta"

    def run(self):
        running=True
        while running:
            dt=self.clock.tick(FPS)/1000
            for e in pygame.event.get():
                if e.type==pygame.QUIT: running=False
                elif e.type==pygame.KEYDOWN:
                    if e.key==pygame.K_ESCAPE: running=False
                    elif e.key==pygame.K_g: self.grid=not self.grid
                    elif e.key==pygame.K_h: self.hitboxes=not self.hitboxes
                    elif e.key==pygame.K_r:
                        self.map.regenerate(); self.player=Player(*self.map.player_spawn); self.msg="Novo mapa gerado com composição de floresta/clareira/montanha."
                    elif e.key==pygame.K_F5:
                        self.map.export_full_map(); self.msg="Exportado como generated_map.png"
            keys=pygame.key.get_pressed()
            vx=(keys[pygame.K_d] or keys[pygame.K_RIGHT])-(keys[pygame.K_a] or keys[pygame.K_LEFT])
            vy=(keys[pygame.K_s] or keys[pygame.K_DOWN])-(keys[pygame.K_w] or keys[pygame.K_UP])
            if vx or vy:
                l=math.hypot(vx,vy); vx/=l; vy/=l
                self.player.move(int(vx*self.player.speed*dt),int(vy*self.player.speed*dt),self.map.solid_rects(),self.map.blocked)
            self.cam.update(self.player.rect)
            self.screen.fill((23,29,25))
            self.map.draw_world(self.screen,self.cam,self.player,self.grid,self.hitboxes)
            self.draw_ui()
            pygame.display.flip()
        pygame.quit()

    def draw_ui(self):
        p=pygame.Surface((SCREEN_W,64),pygame.SRCALPHA); p.fill((18,13,10,170)); self.screen.blit(p,(0,0))
        self.screen.blit(self.big.render("Forest RPG Map Generator V3",True,(255,235,190)),(18,8))
        self.screen.blit(self.font.render(self.msg,True,(235,225,205)),(18,39))
        pos=self.font.render(f"Tile: {self.player.rect.centerx//TILE}, {self.player.rect.centery//TILE}",True,(235,225,205))
        self.screen.blit(pos,(SCREEN_W-170,22))

if __name__ == "__main__":
    Game().run()
