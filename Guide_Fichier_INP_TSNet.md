# Fiche Pratique : Créer un fichier `.inp` pour TSNet (Basé sur EPANET)

Le format `.inp` est le format standard utilisé par le logiciel EPANET pour définir des réseaux de distribution d'eau. La bibliothèque **TSNet** utilise ce même format pour charger la topologie du réseau et les conditions initiales avant d'effectuer des simulations de régimes transitoires (coups de bélier).

Voici une explication détaillée des sections principales d'un fichier `.inp` (en prenant `Tnet0.inp` comme exemple), et comment les remplir.

---

## 1. Les Nœuds (Junctions, Reservoirs, Tanks)

Les nœuds représentent les points de connexion, les sources ou les stockages.

### `[JUNCTIONS]` (Les nœuds simples)
Ce sont les points où les tuyaux se rejoignent, ou les points de consommation.
```ini
[JUNCTIONS]
;ID              Elev        Demand      Pattern         
 2               0           0                       ;
 3               0           0                       ;
 4               0           50                      ;
```
* **ID** : L'identifiant unique du nœud (ex: 2, 3, 4).
* **Elev** : L'élévation ou altitude du nœud (en mètres).
* **Demand** : La demande en eau de base (en unités de débit, ex: LPS - Litres par seconde). Ici, le nœud 4 a une demande de 50.

### `[RESERVOIRS]` (Les réservoirs / Sources à charge constante)
Représentent des sources dont la charge (pression + altitude) est constante et infinie.
```ini
[RESERVOIRS]
;ID              Head        Pattern         
 1               750                         ;
```
* **ID** : Identifiant du réservoir.
* **Head** : La charge totale (altitude de la surface de l'eau en mètres). Ici, 750m.

### `[TANKS]` (Les châteaux d'eau ou bassins)
Représentent des stockages avec des niveaux variables. (Vide dans l'exemple `Tnet0`, mais utile si vous avez une cheminée d'équilibre).

---

## 2. Les Liens (Pipes, Pumps, Valves)

Les liens relient les nœuds entre eux.

### `[PIPES]` (Les tuyaux)
```ini
[PIPES]
;ID      Node1   Node2   Length      Diameter    Roughness   MinorLoss   Status
 1       1       2       1200        600         0.02        0           Open
 2       2       3       2400        1200        0.02        0           Open
```
* **ID** : Identifiant du tuyau.
* **Node1 / Node2** : Les nœuds de départ et d'arrivée.
* **Length** : Longueur (en mètres).
* **Diameter** : Diamètre (en millimètres).
* **Roughness** : Rugosité. L'unité dépend de la formule de perte de charge choisie (ex: mm pour Darcy-Weisbach, coefficient pour Hazen-Williams).
* **MinorLoss** : Coefficient de perte de charge singulière.
* **Status** : État initial (Open/Closed).

### `[VALVES]` (Les vannes)
```ini
[VALVES]
;ID      Node1   Node2   Diameter    Type    Setting     MinorLoss   
 3       3       4       158         PRV     100000      0
```
* **Diameter** : Diamètre de la vanne (mm).
* **Type** : Type de vanne (ex: PRV pour réductrice de pression, TCV pour vanne de contrôle d'étranglement, PBV, etc.).
* **Setting** : Le réglage initial (dépend du type. Pour une PRV, c'est la pression de consigne).
* **MinorLoss** : Perte de charge singulière.

---

## 3. Paramétrages Globaux

### `[STATUS]` (États initiaux forcés)
Permet de forcer l'état initial d'une pompe ou d'une vanne.
```ini
[STATUS]
;ID              Status/Setting
 3               Open
```
Ici, on s'assure que la vanne `3` est bien ouverte au lancement de la simulation.

### `[OPTIONS]` (Options de calcul hydraulique)
**Très important pour TSNet** car cela définit les unités de base et la formulation des pertes de charges pour le calcul de l'état initial (Steady State).
```ini
[OPTIONS]
 Units              LPS         ; Litres Par Seconde (LPS), CMH, GPM...
 Headloss           D-W         ; Formule de perte de charge (D-W = Darcy-Weisbach, H-W = Hazen-Williams)
 Specific Gravity   1
 Viscosity          1
```

### `[TIMES]` (Paramètres temporels EPANET)
```ini
[TIMES]
 Duration           0:00 
 Hydraulic Timestep 1:00 
```
*Note pour TSNet :* TSNet n'utilise pas ces paramètres pour la simulation transitoire (il utilise `tm.set_time(tf, dt)` dans votre script Python), mais EPANET a besoin que ces valeurs soient valides pour son initialisation.

---

## 4. Affichage et Esthétique (Optionnel)

### `[COORDINATES]` (Coordonnées)
Définit sur un plan X, Y où se trouvent les nœuds. Utile uniquement si vous visualisez le réseau dans l'interface graphique d'EPANET ou via certaines fonctions de tracé de TSNet.
```ini
[COORDINATES]
;Node            X-Coord         Y-Coord
 2               -1167.70        8919.75         
```

### `[LABELS]` (Étiquettes)
Pour ajouter du texte sur le plan.

---

## 💡 Conseils Pratiques pour TSNet :
1. **Éditeur EPANET** : Le plus simple pour créer un fichier `.inp` de zéro n'est pas de l'écrire à la main dans un fichier texte, mais de **télécharger le logiciel officiel EPANET 2.2** (gratuit), de dessiner votre réseau graphiquement, et de faire "File > Export > Network...".
2. **Choix des unités** : Vérifiez bien `Units` dans `[OPTIONS]`. Si vous êtes en `LPS` (Système international), les longueurs sont en mètres, les diamètres en millimètres, les pressions en mètres.
3. **Pertes de charge** : `Headloss D-W` (Darcy-Weisbach) est généralement préférable et plus rigoureux physiquement pour les calculs de coups de bélier que `H-W` (Hazen-Williams). Dans TSNet, vous pourrez choisir le modèle de friction instationnaire (`steady`, `quasi-steady`, `unsteady`).
4. **Fermeture/Ouverture MOC** : Les manipulations transitoires (fermer une vanne en 5s, casser un tuyau) ne se définissent **pas** dans le fichier `.inp`. Le fichier `.inp` décrit le réseau à **t=0**. Tout ce qui se passe après (temps transitoire) se code en Python avec les règles TSNet (ex: `tm.valve_closure(...)`).
