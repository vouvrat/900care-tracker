# Guide utilisateur

## À quoi sert cet outil ?

900 Care propose un abonnement avec un pack de démarrage ("starter") puis des
commandes régulières. Dans un foyer de plusieurs personnes, chaque membre
consomme les produits à un rythme différent, et il est difficile de savoir
de mémoire :

- qui a déjà terminé quel produit,
- à quelle fréquence chaque produit est réellement consommé,
- ce qui a plu ou non à chacun,
- quelles quantités commander la prochaine fois pour éviter les ruptures
  ou le surstock.

Cet outil répond à ces quatre besoins avec une interface web simple, utilisable
par tous les membres du foyer depuis leur téléphone ou ordinateur sur le
réseau local.

## Vue d'ensemble des pages

| Page | Adresse | Rôle |
|---|---|---|
| Dashboard | `/` | Vue d'ensemble : consommation par produit × membre, suggestion de commande |
| Membres | `/members` | Régler la taille du foyer, renommer les membres, régler la couverture de commande |
| Produits | `/products` | Catalogue des produits 900 Care (et autres) suivis |
| Journal | `/log` | Enregistrer une utilisation ("j'ai commencé / terminé ce produit") |
| Avis | `/reviews` | Noter la satisfaction d'un membre (ou du foyer) sur un produit |
| Historique | `/history` | Timeline filtrable de toute l'activité (conso + avis) |

## Premiers pas

1. **Configurer le foyer** (`/members`)
   - Indiquer le nombre de personnes dans le foyer → l'outil crée
     automatiquement les emplacements "Membre 1", "Membre 2", etc.
   - Renommer chaque emplacement avec le prénom réel du membre.
   - Régler la "couverture de commande" (par défaut 2 mois) : c'est le nombre
     de mois de consommation que la suggestion de commande visera à couvrir.

2. **Créer le catalogue produits** (`/products`)
   - Ajouter chaque produit reçu dans le pack starter (ou commandé ensuite) :
     nom, catégorie libre (ex. "bucco-dentaire", "rasage", "peau/cheveux"),
     unité (ex. "brosse", "tube", "savon", "lame").
   - Le catalogue est modifiable à tout moment ; supprimer un produit ne
     supprime pas son historique passé, il est juste retiré des listes
     actives.

3. **Enregistrer la consommation au fil de l'eau** (`/log`)
   - Dès qu'un membre commence ou termine un produit, l'enregistrer ici :
     qui, quel produit, quel type d'événement ("a commencé" / "a terminé"),
     quelle date.
   - C'est **l'événement "a terminé" qui alimente le calcul de rythme de
     consommation** — c'est lui qui permet de savoir combien de temps dure
     un produit chez ce membre.

4. **Noter les avis** (`/reviews`)
   - Après usage, chaque membre peut donner une note de 1 à 5 et un
     commentaire libre sur un produit.
   - Un avis peut être associé à un membre précis, ou laissé "Foyer" (avis
     général, sans membre particulier) — utile par exemple pour un produit
     partagé (dentifrice familial, etc.).

5. **Consulter le dashboard** (`/`)
   - Le tableau principal croise produits (lignes) et membres (colonnes) :
     nombre de fois où le produit a été terminé par ce membre, rythme mensuel
     estimé, date de dernière utilisation.
   - La colonne "Rythme foyer" additionne les rythmes de tous les membres
     pour ce produit.
   - En dessous, la section **Suggestion pour la prochaine commande**
     indique, pour chaque produit ayant assez de données, la quantité
     recommandée à commander.

6. **Explorer l'historique** (`/history`)
   - Liste chronologique de tous les événements de consommation et avis,
     filtrable par membre et/ou par produit — pratique pour retrouver
     "qu'est-ce qu'on avait pensé de ce shampoing solide déjà ?"

## Comprendre la suggestion de commande

Pour chaque produit et chaque membre, l'outil calcule l'intervalle moyen (en
jours) entre deux événements "a terminé" consécutifs. Il en déduit un rythme
mensuel : `30 / intervalle_moyen`.

Le **rythme foyer** pour un produit est la somme des rythmes mensuels de tous
les membres qui l'utilisent.

La **quantité suggérée** est alors :

```
quantité suggérée = arrondi supérieur( rythme_foyer_mensuel × couverture_en_mois )
```

où la couverture en mois est réglable sur `/members` (2 mois par défaut).

⚠️ Il faut **au moins deux événements "a terminé"** pour un couple
produit/membre avant qu'un rythme puisse être calculé — avant ça, l'outil
affiche "pas assez de données" et ce produit n'apparaît pas encore dans les
suggestions. Plus l'historique s'accumule, plus la suggestion devient fiable.

## Bonnes pratiques d'usage

- Enregistrer les événements **au moment où ils arrivent** (pas a posteriori
  de mémoire) pour que les rythmes soient fiables.
- Toujours utiliser "a terminé" (pas seulement "a commencé") pour les
  produits consommables — c'est cet événement qui nourrit le calcul.
- Mettre à jour la taille du foyer et les prénoms dès qu'ils changent
  (déménagement d'un membre, invité longue durée, etc.) — l'historique des
  membres désactivés reste conservé, rien n'est perdu.
