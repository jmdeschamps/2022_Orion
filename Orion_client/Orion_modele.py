 # -*- coding: utf-8 -*-   
import random

import ast
from Id import *
from helper import Helper as hlp
        
class Etoile():
    def __init__(self,x,y):
        self.id=get_prochain_id()
        self.proprietaire=""
        self.x=x
        self.y=y
        self.taille=random.randrange(4,8)
        self.ressources= {"metal":0,
                          "energie":0,
                          "existentielle":0}

class Vaisseau():
    def __init__(self,parent,nom,x,y):
        self.parent=parent
        self.id=get_prochain_id()
        self.proprietaire=nom
        self.x=x
        self.y=y
        self.espace_cargo=0
        self.energie=100
        self.taille=5
        self.vitesse=2
        self.cible=0
        self.angle_cible=0

    def jouer_prochain_coup(self,trouver_nouveau=0):
        if self.cible!=0:
            return self.avancer()
        elif trouver_nouveau:
            cible = random.choice(self.parent.parent.etoiles)
            self.acquerir_cible(cible)

    def acquerir_cible(self,cible):
        self.cible=cible
        self.angle_cible = hlp.calcAngle(self.x, self.y, self.cible.x, self.cible.y)

    def avancer(self):
        if self.cible!=0:
            x=self.cible.x
            y=self.cible.y
            self.x,self.y=hlp.getAngledPoint(self.angle_cible,self.vitesse,self.x,self.y)
            if hlp.calcDistance(self.x,self.y,x,y) <=self.vitesse:
                self.parent.log.append(["Arrive:",self.parent.parent.cadre_courant,self.id,self.cible.id,self.cible.proprietaire])
                if not self.cible.proprietaire:
                    self.cible.proprietaire=self.proprietaire
                    cible=self.cible
                    self.cible=0
                    return ["rendu",cible]

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
        self.log=[]
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

        if self.nom==self.parent.parent.mon_nom:
            self.parent.parent.lister_objet(type_vaisseau,v.id)
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
                    return
        
        
    def jouer_prochain_coup(self):
        self.avancer_flotte()

    def avancer_flotte(self,chercher_nouveau=0):
        for i in self.flotte:
            for j in self.flotte[i]:
                j=self.flotte[i][j]
                rep=j.jouer_prochain_coup(chercher_nouveau)
                if rep:
                    self.etoilescontrolees.append(rep[1])
                    self.parent.parent.afficher_etoile(self.nom,rep[1])

# IA- nouvelle classe de joueur
class IA(Joueur):
    def __init__(self,parent,nom,etoilemere,couleur):
        Joueur.__init__(self, parent, nom, etoilemere, couleur)  
        self.cooldownmax=200
        self.cooldown=20
        
    def jouer_prochain_coup(self):
        # for i in self.flotte:
        #     for j in self.flotte[i]:
        #         j=self.flotte[i][j]
        #         rep=j.jouer_prochain_coup(1)
        #         if rep:
        #             self.etoilescontrolees.append(rep[1])
        self.avancer_flotte(1)
                
        if self.cooldown==0:
            v=self.creervaisseau(["Vaisseau"])
            cible = random.choice(self.parent.etoiles)
            v.acquerir_cible(cible)
            self.cooldown=random.randrange(self.cooldownmax) + self.cooldownmax
        else:
            self.cooldown-=1

class Modele():
    def __init__(self,parent,joueurs):
        self.parent=parent
        self.largeur=6000
        self.hauteur=6000
        self.nb_etoiles=100
        self.joueurs={}
        self.actions_a_faire={}
        self.etoiles=[]
        self.objets_spatiaux={}
        self.cadre_courant=None
        self.creeretoiles(joueurs,1)
        
    def creeretoiles(self,joueurs,ias=0):
        bordure=10
        for i in range(self.nb_etoiles):
            x=random.randrange(self.largeur-(2*bordure))+bordure
            y=random.randrange(self.hauteur-(2*bordure))+bordure
            self.etoiles.append(Etoile(x,y))
        np=len(joueurs)+ias
        etoile_occupee=[]
        while np:
            p=random.choice(self.etoiles)
            if p not in etoile_occupee:
                etoile_occupee.append(p)
                self.etoiles.remove(p)
                np-=1

        couleurs=["red","blue","lightgreen","yellow",
                  "lightblue","pink","gold","purple"]
        for i in joueurs:
            self.joueurs[i]=Joueur(self,i,etoile_occupee.pop(0),couleurs.pop(0))
        
        # IA- creation des ias
        couleursia=["orange","green","cyan",
                  "SeaGreen1","turquoise1","firebrick1"]
        for i in range(ias):
            self.joueurs["IA_"+str(i)]=IA(self,"IA_"+str(i),etoile_occupee.pop(0),couleursia.pop(0))
        
    ##############################################################################
    def jouer_prochain_coup(self,cadre):
        #  NE PAS TOUCHER LES LIGNES SUIVANTES  ################
        self.cadre_courant=cadre
        # insertion de la prochaine action demandée par le joueur
        if cadre in self.actions_a_faire:
            for i in self.actions_a_faire[cadre]:
                self.joueurs[i[0]].actions[i[1]](i[2])
                """
                i a la forme suivante [nomjoueur, action, [arguments]
                alors self.joueurs[i[0]] -> trouve l'objet représentant le joueur de ce nom
                """
            del self.actions_a_faire[cadre]
        # FIN DE L'INTERDICTION #################################

        # demander aux objets de jouer leur prochain coup
        # aux joueurs en premier
        for i in self.joueurs:
            self.joueurs[i].jouer_prochain_coup()

        # NOTE si le modele (qui représente l'univers !!! )
        #      fait des actions - on les activera ici...
        self.creer_bibittes_spatiales(12)
        # EXEMPLE

    def creer_bibittes_spatiales(self,nb_biittes=0):
        pass

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

                if cadrecle not in self.actions_a_faire.keys():
                    self.actions_a_faire[cadrecle] = action
                else:
                    self.actions_a_faire[cadrecle].append(action)
    # NE PAS TOUCHER - FIN
 ##############################################################################