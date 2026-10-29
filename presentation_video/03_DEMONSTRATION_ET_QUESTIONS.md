# Répétition, démonstration et questions possibles

## Avant l’enregistrement

1. Dans le dossier du pricer, activer `venv` puis lancer `python main.py`. Ouvrir http://127.0.0.1:5001. Si le serveur tourne déjà, utiliser sa page ; après modification Python, le relancer.
2. Ouvrir les quatre fichiers Python, `templates/index.html` et les deux fichiers de tests. Fermer les autres onglets, agrandir le texte et couper les notifications.
3. Faire une répétition complète. La démonstration manuelle est le fil principal ; une recherche de ticker peut être montrée en complément si les données externes répondent.
4. Relever les résultats de votre propre session. Ne pas lire un prix d’exemple comme s’il provenait de l’écran.

## Démonstration principale : Plain

| Paramètre | Valeur |
|---|---|
| Ticker | Aucun, départ normalisé à 100 sur une page fraîche |
| Volatilité | Manuelle, 25 % |
| Taux / dividende | 3 % / 2 % |
| Nominal | 1 000 |
| Maturité / fréquence | 36 mois / semestrielle |
| Coupon par observation | 4 % |
| Seuil rappel et coupon final | 100 % |
| Protection finale | Activée, barrière 60 % |
| Premier rappel autorisé | 6 mois |
| Simulations / graine | 50 000 / 42 |

Calculer une fois avec rappel, relever le prix et la durée. Décocher uniquement le rappel, puis recalculer. Dans le second cas, durée = 3 ans, probabilité de maturité = 100 %, rappels = 0 %. Ne pas annoncer un sens universel de variation du prix lorsqu’on supprime le rappel : les paiements et leur calendrier changent.

Sur le graphique sans rappel, à maturité : à un cours de 50, principal 500 et aucun coupon ; à 80, principal 1 000 et aucun coupon ; à 100, total 1 240. Les six coupons de 4 % ne sont versés que si le seuil final est atteint. Les courbes sont non actualisées.

Si un ticker a déjà été chargé, ne pas supposer que le départ vaut encore 100 : les seuils s’expriment en pourcentage du cours initial chargé.

## Démonstration complémentaire : Phoenix

Montrer la case mémoire et les trois barrières. Expliquer le cas 65 puis 80 du script. Le changement de prix entre deux calculs ne mesure pas parfaitement l’effet de la mémoire si les tirages ont changé : l’interface Phoenix n’impose pas de graine fixe. S’appuyer sur les règles de flux pour expliquer la mémoire.

## Vérification locale

Depuis le dossier du projet :

```bash
source venv/bin/activate
python -B -m unittest discover -s tests -v
```

Lors de la préparation de ce dossier, les 14 tests passent. Ce résultat contrôle la logique Python et les routes Flask ; il ne constitue pas une validation visuelle complète du navigateur ni une garantie de disponibilité de Yahoo.

## Questions et réponses à préparer ensemble

**Pourquoi Monte Carlo ?** Les paiements dépendent de plusieurs constats et parfois des coupons passés. Nous simulons ces trajectoires puis suivons les règles du produit.

**Pourquoi ne pas utiliser le rendement moyen historique de l’action ?** Nous calculons un prix sous une mesure risque-neutre avec une dérive r−q, pas une prévision de performance réelle.

**Pourquoi le terme −sigma²/2 ?** Il corrige le passage entre le rendement logarithmique simulé et le niveau du cours ; avec ce terme, le facteur de croissance moyen du cours correspond à exp((r−q)dt).

**Pourquoi un zéro-coupon n’apparaît-il pas comme un module séparé ?** L’actualisation du remboursement du principal est déjà comprise dans les flux. Une décomposition obligataire et optionnelle serait une autre présentation du même problème, pas un montant à ajouter une seconde fois.

**Protection à 60 % : perd-on seulement ce qui dépasse 40 % de baisse ?** Non. Si le cours final est sous 60 %, le principal suit toute la baisse depuis S0. À 50 % de S0, on récupère 50 % du nominal.

**Que fait exactement la case de rappel du Plain ?** Cochée : possibilité de sortir avant maturité. Décochée : aucune sortie anticipée et coupons tous conditionnés au constat final. Elle ne crée aucun coupon acquis à chaque constat intermédiaire.

**Que fait la case de protection conditionnelle ?** Cochée : principal réduit sous la barrière finale. Décochée : le modèle rembourse le nominal quel que soit le cours final, sans prendre en compte le défaut de l’émetteur.

**Le risque de perte affiché est-il une prévision ?** Non, il s’agit d’une fréquence sous les hypothèses risque-neutres du modèle. Le principal est étudié avant compensation éventuelle par les coupons.

**Peut-on perdre avec des coupons déjà reçus ?** Oui, le principal peut être réduit. La perte totale après coupons peut différer de la perte du principal ; l’indicateur affiché concerne ce dernier.

**Pourquoi deux calculs Phoenix peuvent-ils différer ?** Sans graine imposée, les trajectoires changent. L’intervalle de confiance mesure cette incertitude Monte Carlo.

**Pourquoi la marge peut-elle être négative ?** Si le prix théorique dépasse 100 %, l’écart 100 % moins prix est négatif. Ce n’est pas un calcul de rentabilité commerciale complet.

**Pourquoi le graphe Phoenix ne montre-t-il pas tout ?** Un même cours final peut correspondre à des historiques de coupons différents. Le graphe à une seule variable ne compte que le dernier coupon, avec le capital et le bonus éventuel, sans rappel antérieur.

**Quelle est la principale limite de la volatilité historique ?** Elle décrit les variations passées ; elle ne calibre pas automatiquement les scénarios aux prix des options actuelles. Le modèle ne représente pas de smile ni de volatilité variable.

**Que tester en priorité ?** Des trajectoires dont les paiements sont connus, l’égalité aux barrières, l’absence de rappel, le principal sans perte conditionnelle, les unités et les paramètres invalides. La convergence Monte Carlo seule ne prouve pas que les règles sont correctes.

**Quelle amélioration proposer ?** Une courbe d’actualisation, une calibration aux options et une prise en compte explicite du risque émetteur et des coûts, avant de parler d’un prix commercial.

## Format court : 6 à 7 minutes

Conserver l’objectif, une minute d’architecture et données, une minute de simulation, deux minutes de règles des produits, puis la démonstration et les limites. Ne pas parcourir toutes les fonctions : montrer les quelques lignes qui relient paramètres, flux et valeur.
