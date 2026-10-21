# Backtests PEA Swing — 21 octobre 2026

## Conclusion

La stratégie mensuelle produit un résultat historique positif et une baisse maximale inférieure à l'achat-conservation. Elle ne le bat pas en rendement. La variante hebdomadaire est moins convaincante sur les deux critères. La règle mensuelle est donc livrée comme outil d'alerte prudent à observer en simulation, pas comme stratégie ayant prouvé un avantage de rendement.

Le choix mensuel et les deux règles ont été fixés avant lecture de ces résultats, sans recherche de paramètres. Les performances historiques connues de la classe d'actifs ont néanmoins influencé le choix de l'ETF et de l'approche : la validation reste rétrospective, pas un test prospectif indépendant.

## Résultats avec 5 000 €

Capital initial réinitialisé à 5 000 € pour chaque période et chaque stratégie. Aucun apport, aucun retrait. Valeur finale nette d'une liquidation hypothétique. Montants arrondis.

| Période | Stratégie | Capital final | Rendement annualisé | Baisse maximale | Ordres |
|---|---|---:|---:|---:|---:|
| 2011–20/10/2026 | Mensuelle 10 mois | 16 088 € | 7,68 % | −20,87 % | 25 |
| 2011–20/10/2026 | Hebdomadaire 200 séances | 11 197 € | 5,24 % | −30,36 % | 65 |
| 2011–20/10/2026 | Achat-conservation | 29 102 € | 11,80 % | −33,43 % | 1 |
| 2011–2019 | Mensuelle 10 mois | 9 346 € | 7,21 % | −20,87 % | 13 |
| 2011–2019 | Hebdomadaire 200 séances | 7 552 € | 4,69 % | −27,03 % | 35 |
| 2011–2019 | Achat-conservation | 12 734 € | 10,96 % | −21,63 % | 1 |
| 2020–20/10/2026 | Mensuelle 10 mois | 8 397 € | 7,92 % | −16,71 % | 13 |
| 2020–20/10/2026 | Hebdomadaire 200 séances | 7 265 € | 5,65 % | −23,43 % | 31 |
| 2020–20/10/2026 | Achat-conservation | 10 922 € | 12,18 % | −31,72 % | 1 |

La baisse maximale est la perte entre un sommet du portefeuille et un creux ultérieur ; ce n'est pas une limite de perte garantie. Les ordres sont les achats et ventes effectivement simulés, sans l'ultime liquidation hypothétique. L'achat-conservation n'a donc qu'un ordre.

Sur la validation, la mensuelle est exposée environ 77 % des séances. Elle comporte 24 mois négatifs sur 82 observations mensuelles, octobre 2026 étant incomplet. Son pire mois est février 2020 : −8,23 %, environ −411 € sur le portefeuille alors détenu. Les six positions closes de cette période durent de 31 à 638 jours, médiane 258 jours ; la septième reste ouverte à la fin. « Plusieurs semaines » peut donc devenir plusieurs mois ou plus d'un an.

## Frais, exécution et stress

- Parts entières, aucun emprunt ; la quantité réserve les frais dès l'achat. Le reliquat de cash reste non rémunéré.
- Signal calculé avec les données strictement antérieures à la séance d'exécution. Pour la mensuelle, seules les clôtures des mois terminés interviennent. Exécution à l'ouverture suivante, jamais à la clôture ayant créé le signal.
- Commission Internet Bourse Direct : minimum de la grille standard et du plafond PEA 0,5 %. 0,99 € jusqu'à 500 €, 1,90 € jusqu'à 1 000 €, 2,90 € jusqu'à 2 000 €, 3,80 € jusqu'à 4 400 €, puis 0,09 %. Grille actuelle appliquée à toutes les années pour comparer à conditions constantes ; ce n'est pas une reconstitution des tarifs historiques. Pas de promotion.
- Écart défavorable de 0,10 % à chaque achat et chaque vente pour approximer spread et glissement. L'écart à l'ouverture précédente est déjà contenu dans le prix d'ouverture suivant.
- Valorisation quotidienne avec frais et glissement d'une liquidation hypothétique, sans déduction répétée de ces coûts du cash.
- Les frais internes de l'ETF sont déjà reflétés dans ses cours ; ils ne sont pas déduits une seconde fois. Pas de fiscalité des retraits, aucun retrait simulé. Pas de frais de données, NAS ou électricité inclus.
- Aucun stop garanti : un krach entre deux décisions mensuelles peut entraîner une perte importante.

Avec un écart défavorable porté à 0,30 % par côté sur 2020–2026 : mensuelle 8 229 € (7,60 % annualisés, baisse maximale −17,09 %), hebdomadaire 6 779 € (4,58 %, −24,73 %), achat-conservation 10 892 € (12,13 %, −31,77 %). La conclusion comparative ne change pas.

## Qualité des données et portée de la validation

Réponse Yahoo quotidienne figée : 4 441 entrées du 16/06/2009 au 20/10/2026. Trois dates OHLC manquantes sont exclues, sans interpolation : 13/01/2010, 10/01/2013, 10/04/2013. Aucune n'appartient à la période de validation 2020–2026. Les calculs ont 2009–2010 pour amorcer les indicateurs avant le début 2011.

Cours ajustés identiques aux clôtures, aucun événement dividende/split déclaré par cette réponse. Le programme bloque une nouvelle réponse contenant une opération sur titres, car elle nécessite un traitement audité. Il ne fabrique pas un historique nominal à partir de séries ajustées. Les dates, devises, granularités et OHLC sont contrôlés ; le cache et son empreinte sont fournis. Il n'y a pas de reconstruction complète du calendrier Euronext ni de recoupement indépendant de chaque ouverture. Les cours gratuits peuvent contenir des erreurs ; les résultats restent conditionnés à cette source.

L'historique CW8 antérieur à 2018 correspond à son fonds prédécesseur ; la fiche Amundi indique l'absorption du fonds français le 18/04/2018 et une première valeur liquidative le 16/06/2009. Il ne s'agit donc pas d'une part sous l'ISIN luxembourgeois actuel pendant toute la période.

Limites : aucun test de 2008 ou de l'éclatement de la bulle Internet ; longue période favorable aux actions mondiales ; un seul ETF sélectionné aujourd'hui ; absence de coûts de change explicites car les transactions sont en EUR, mais l'ETF garde une exposition économique aux devises ; ouverture quotidienne supposée exécutable au prix modélisé. Les barres de prix seules ne prouvent pas les conditions réelles d'exécution.

La séparation 2011–2019 / 2020–2026 empêche de mélanger les tableaux de développement et de validation, mais ne rend pas ces années inconnues à l'analyste. Aucune règle n'a été modifiée après consultation de la validation dans cette exécution. La prochaine étape probante est l'observation prospective des alertes et des prix réalisables.

## Objectif 100–200 €/mois

Cet objectif n'est pas démontré avec 5 000 €. Il représente 24–48 % du capital initial par an en retraits simples. Les 7,92 % annualisés historiques de la mensuelle représentent environ 396 €/an sur une base de 5 000 €, sans régularité mensuelle, sans garantie, et avant fiscalité éventuelle. Ne pas confondre croissance composée du portefeuille et revenu disponible.

## Vérifications et livraison

11 tests automatisés réussis : commission, capacité d'achat, causalité, gel mensuel, prix d'ouverture, invariance au futur, coûts sur marché plat, blocage des opérations sur titres, cours périmés, déduplication Telegram, absence d'enregistrement après échec d'envoi. Les tests Telegram utilisent des réponses simulées ; aucun message réel n'a été envoyé. Python exécuté dans cet environnement ; Docker indisponible ici, image et déploiement NAS non testés. Le programme ne passe aucun ordre et ne suit pas les positions réelles.

## Sources

- Données : https://query1.finance.yahoo.com/v8/finance/chart/CW8.PA (réponse brute conservée ; bornes explicites et intervalle quotidien).
- Tarifs Bourse Direct consultés le 21/10/2026 : https://www.boursedirect.fr/fr/bourse/tarifs
- Fiche officielle Amundi, 29/02/2024 : https://www.amundietf.fr/pdfDocuments/download/6fb43afc-51c2-492a-b680-7c73cee0f4fd/MonthlyFactsheet_2832240_13136_FRA_ENG_ETF_INSTITUTIONNEL_20240229.pdf
- Page produit actuelle : https://www.amundietf.lu/en/individual/products/equity/amundi-msci-world-swap-ucits-etf-eur-acc/lu1681043599
