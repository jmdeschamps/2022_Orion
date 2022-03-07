 # -*- coding: utf-8 -*-   
import random

import ast
from Id import *
from helper import Helper as hlp
        
class etoile():
    def __init__(self,x,y):
        self.id=get_prochain_id()
        self.proprietaire="inconnu"
        self.x=x
        self.y=y
        self.taille=random.randrange(4,8)
        self.ressource=random.randrange(10)+1
        
class Vaisseau():
    def __init__(self,parent,nom,x,y):
        self.parent=parent
        self.id=get_prochain_id()
        self.proprietaire=nom
        self.x=x
        self.y=y
        self.cargo=0
        self.energie=100
        self.taille=5
        self.vitesse=2
        self.cible=0
        self.ang=0

    def jouer_prochain_coup(self,trouver_nouveau=0):
        if self.cible!=0:
            self.avancer()
        elif trouver_nouveau:
            cible = random.choice(self.parent.parent.etoiles)
            self.acquerir_cible(cible)
    # else:
    #    i.cible=random.choice(self.parent.etoiles)

    def acquerir_cible(self,cible):
        self.cible=cible
        self.ang = hlp.calcAngle(self.x, self.y, self.cible.x, self.cible.y)

    def avancer(self):
        if self.cible!=0:
            x=self.cible.x
            y=self.cible.y
            x1,y1=hlp.getAngledPoint(self.ang,self.vitesse,self.x,self.y)
            self.x,self.y=x1,y1 #int(x1),int(y1)
            if hlp.calcDistance(self.x,self.y,x,y) <=self.vitesse:
                print("RESSOURCES...",self.cible.id,self.cible.ressource,self.cible.proprietaire)
                self.cible.proprietaire=self.proprietaire
                self.cible=0
class Cargo(Vaisseau):
    def __init__(self,parent,nom,x,y):
        Vaisseau.__init__(self,parent,nom,x,y)
        self.cargo=1000
        self.energie=500
        self.taille=6
        self.vitesse=1
        self.cible=0
        self.ang=0
              
class Joueur():
    def __init__(self,parent,nom,etoilemere,couleur):
        self.id=get_prochain_id()
        self.parent=parent
        self.nom=nom
        self.etoilemere=etoilemere
        self.etoilemere.proprietaire=self.nom
        self.couleur=couleur
        self.etoilescontrolees=[etoilemere]
        self.flotte={"Vaisseau":{},
                     "Cargo":{}}
        self.actions={"creervaisseau":self.creervaisseau,
                      "ciblerflotte":self.ciblerflotte}
        
    def creervaisseau(self,params):
        type_vaisseau=params[0]
        if type_vaisseau=="Cargo":
            v=Cargo(self,self.nom,self.etoilemere.x+10,self.etoilemere.y)
        else:
            v=Vaisseau(self,self.nom,self.etoilemere.x+10,self.etoilemere.y)
        self.flotte[type_vaisseau][v.id]=v
        return v
        
    def ciblerflotte(self,ids):
        idori,iddesti=ids
        ori=None
        for i in self.flotte.keys():
            if idori in self.flotte[i]:
                ori=self.flotte[i][idori]

        if ori:
            for j in self.parent.etoiles:
                if j.id== iddesti:
                    ori.acquerir_cible(j)
                    #i.cible=j
                    print("GOT TARGET")
                    return
        
        
    def prochaineaction(self):
        for i in self.flotte:
            for j in self.flotte[i]:
                j=self.flotte[i][j]
                j.jouer_prochain_coup()
            
    

# IA- nouvelle classe de joueur
class IA(Joueur):
    def __init__(self,parent,nom,etoilemere,couleur):
        Joueur.__init__(self, parent, nom, etoilemere, couleur)  
        self.cooldownmax=50
        self.cooldown=20
        print("IA",self.etoilemere.x,self.etoilemere.y)
        
    def prochaineaction(self):
        for i in self.flotte:
            for j in self.flotte[i]:
                j=self.flotte[i][j]
                j.jouer_prochain_coup(1)
                
        if self.cooldown==0:
            v=self.creervaisseau(["Vaisseau"])
            cible = random.choice(self.parent.etoiles)
            v.acquerir_cible(cible)
            self.cooldown=random.randrange(self.cooldownmax) + (self.cooldownmax/2)
        else:
            self.cooldown-=1

class Modele():
    def __init__(self,parent):
        self.parent=parent
        self.partie=None

class Partie():
    def __init__(self,parent,joueurs):
        self.parent=parent
        self.largeur=15000 #self.parent.vue.root.winfo_screenwidth()
        self.hauteur=15000 #self.parent.vue.root.winfo_screenheight()
        self.nb_etoiles=2000#int((self.hauteur*self.largeur)/300000)
        self.joueurs={}
        self.ias=[]
        self.actionsafaire={}
        self.etoiles=[]
        self.creeretoiles(joueurs,1)
        
    def creeretoiles(self,joueurs,ias=1):
        bordure=10
        for i in range(self.nb_etoiles):
            x=random.randrange(self.largeur-(2*bordure))+bordure
            y=random.randrange(self.hauteur-(2*bordure))+bordure
            self.etoiles.append(etoile(x,y))
        np=len(joueurs)+ias
        planes=[]
        while np:
            p=random.choice(self.etoiles)
            if p not in planes:
                planes.append(p)
                self.etoiles.remove(p)
                np-=1
        couleurs=["red","blue","lightgreen","yellow",
                  "lightblue","pink","gold","purple"]
        for i in joueurs:
            self.joueurs[i]=Joueur(self,i,planes.pop(0),couleurs.pop(0))
        
        # IA- creation des ias - max 2 
        couleursia=["orange","green","cyan",
                  "SeaGreen1","turquoise1","firebrick1"]
        for i in range(ias):
            self.ias.append(IA(self,"IA_"+str(i),planes.pop(0),couleursia.pop(0)))  
        
    ##############################################################################
    # insertion de la preochaine action demandée par le joueur<
    def jouer_prochain_coup(self,cadre):
        if cadre in self.actionsafaire:
            for i in self.actionsafaire[cadre]:
                #print(i)
                self.joueurs[i[0]].actions[i[1]](i[2])
                """
                i a la forme suivante [nomjoueur, action, [arguments]
                alors self.joueurs[i[0]] -> trouve l'objet représentant le joueur de ce nom
                """
            del self.actionsafaire[cadre]
                
        for i in self.joueurs:
            self.joueurs[i].prochaineaction()
            
        # IA- appelle prochaine action
        for i in self.ias:
            i.prochaineaction()

    #############################################################################
    # ATTENTION : NE PAS TOUCHER
    def ajouter_actions_a_faire(self, actionsrecues):
        cadrecle=None
        for i in actionsrecues:
            cadrecle = i[0]
            if cadrecle:
                if (self.parent.cadrejeu - 1) > int(cadrecle):
                    print("PEUX PASSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS")
                action = ast.literal_eval(i[1])

                if cadrecle not in self.actionsafaire.keys():
                    self.actionsafaire[cadrecle] = action
                else:
                    self.actionsafaire[cadrecle].append(action)
 ##############################################################################