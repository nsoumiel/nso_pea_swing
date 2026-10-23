# PEA Swing 1.0 — ETF Monde, décisions mensuelles

Version autonome créée le 21 octobre 2026, issue du changement d'horizon du projet PEA. Python 3.11+ sans bibliothèque Python externe. Elle ne remplace pas l'ancien projet intraday et n'utilise aucun de ses secrets.

## Ce que fait le bot

- ETF analysé : Amundi MSCI World Swap UCITS ETF EUR Acc, CW8.PA, ISIN LU1681043599. Vérifier l'ISIN et l'éligibilité sur le ticket Bourse Direct avant une opération.
- Au début d'un mois : dernière clôture mensuelle strictement supérieure à la moyenne des 10 dernières clôtures mensuelles → régime investi ; sinon → liquidités. Égalité → liquidités. Le mois courant est exclu.
- Maintien du régime tout le mois. La position peut durer plusieurs semaines, plusieurs mois ou plus d'un an. Pas de durée maximale, pas de stop intrajournalier, pas de levier, pas de vente à découvert.
- Variante de recherche `weekly200` : dernière clôture de la semaine passée supérieure à la moyenne des 200 séances achevées à la fin de cette semaine. Décision figée pendant la semaine.
- Téléchargement des cours et contrôle toutes les 6 heures. Lecture des clôtures antérieures à la date courante uniquement. Signal initial puis notification Telegram uniquement lors d'un changement de régime. Les notifications sont désactivées par défaut.
- Le message indique une allocation cible théorique, **pas un ordre**. Le bot ne connaît ni votre solde, ni vos positions, ni vos exécutions. L'achat, la vente, la quantité et le contrôle du prix restent manuels chez Bourse Direct. Ne pas racheter à chaque contrôle si vous êtes déjà investi.

## Installation locale et reproduction hors ligne

Décompresser l'archive, ouvrir un terminal dans `pea_swing` :

```bash
python3 -m unittest -v
python3 bot.py backtest
python3 bot.py scan
```

`backtest` utilise la copie historique fournie (sans accès réseau). Les résultats se trouvent dans `results/`. `scan` affiche uniquement le régime et refuse les cours trop anciens. La copie historique sera donc impropre aux alertes quelques jours après sa date de fin : télécharger dans un dossier séparé pour conserver les backtests reproductibles.

```bash
python3 bot.py download --data live_data
python3 bot.py scan --data live_data
python3 bot.py run --data live_data
```

## Surveillance de plusieurs symboles

Toutes les commandes acceptent `--symbols` suivi de symboles Yahoo séparés par des espaces. Sans cette option, `CW8.PA` reste la valeur par défaut.

```bash
python3 bot.py download --symbols CW8.PA ESE.PA --data live_data
python3 bot.py scan --symbols CW8.PA ESE.PA --data live_data
python3 bot.py run --symbols CW8.PA ESE.PA --data live_data
python3 bot.py backtest --symbols CW8.PA ESE.PA --data live_data
```

Chaque symbole dispose de son fichier de cours et de son audit (`<symbole>.json` et `<symbole>.download.json`). Les signaux et la déduplication Telegram sont indépendants par symbole et stratégie. La base SQLite existante est migrée automatiquement en conservant les notifications historiques de CW8.PA. Aucun ISIN n'est supposé pour les autres symboles.

Un échec sur un symbole est affiché et les autres sont traités. Les commandes ponctuelles renvoient un code d'échec si au moins un symbole échoue ; `run` poursuit ses cycles toutes les six heures. Les doublons dans la liste ne sont traités qu'une fois par cycle.

Les contrôles existants restent applicables : cours en EUR uniquement et blocage des opérations sur titres. Vérifiez vous-même l'identité et l'éligibilité PEA des instruments. Chaque backtest simule un capital indépendant de 5 000 €, sans allocation commune entre symboles. Avec plusieurs symboles, les sorties sont séparées dans `results/<symbole>/` ; avec un seul symbole, le chemin historique est conservé. `plot_results.py` reste prévu pour les résultats au chemin historique.

Avec Docker Compose, ajouter les arguments `"--symbols", "CW8.PA", "ESE.PA"` à la liste `command` de `compose.yml`.

## Docker / Synology

Depuis ce même dossier, sur un hôte ayant Docker Compose :

```bash
docker compose up -d --build
docker compose logs --tail 50
```

Sur les versions utilisant l'ancienne commande, remplacer `docker compose` par `docker-compose`. Le DS218+ dispose d'une architecture x86-64 ; disponibilité de Docker/Compose à vérifier sur votre version DSM. Cette image n'a pas été construite ni exécutée sur votre NAS dans cette session.

Pour Telegram : copier `.env.example` en `.env`, saisir votre token et chat ID, puis ajouter `"--telegram"` à la fin de la liste `command` dans `compose.yml` et relancer `docker compose up -d`. Ne jamais partager `.env`. Le premier message résume le régime courant ; ce n'est pas la preuve d'un achat effectué.

Pour arrêter : `docker compose down`. Les données et la déduplication persistent dans les dossiers montés. Sauvegarder `state`. Une panne entre l'envoi Telegram et l'enregistrement SQLite peut exceptionnellement produire un doublon au redémarrage. Aucun message n'a été envoyé pendant la création du projet.

## Exécution manuelle

1. Lire le nouveau régime ; contrôler qu'il correspond à votre compte, à votre horizon et à votre exposition souhaitée.
2. Vérifier cours, spread, ISIN et quantité. En cas d'achat, garder assez d'espèces pour les frais et l'écart de prix ; les parts sont entières. Exemple de calcul dans Python : `affordable(cash, prix)`.
3. Enregistrer vous-même l'opération dans votre suivi de compte. Le scanner ne tient pas de registre des positions réelles.

Le backtest suppose une exécution à l'ouverture de la séance suivant la décision. Une alerte lue tard ou une exécution à un autre prix donnera un autre résultat. Le bot lancé toutes les 6 h n'est pas un automate d'exécution à l'ouverture. Surveiller les journaux : un échec réseau ou des cours périmés bloque l'alerte ; aucun ancien cours n'est présenté comme une nouvelle donnée.

## Fichiers

- `bot.py` : téléchargement, signaux, simulation, alertes et boucle.
- `test_bot.py` : tests de causalité, coûts, état et intégrité.
- `protocol.json` : règles fixées avant lecture des résultats de cette exécution.
- `data/CW8.PA.json` : réponse quotidienne Yahoo figée jusqu'au 20/10/2026 ; `audit.json` précise les limites.
- `results/summary.csv` et `.json` : comparaison ; fichiers equity/orders/months : audit complet par stratégie et période.
- `RAPPORT.md` : interprétation, hypothèses et limites.

Le projet est un outil de recherche et d'alerte. Il n'est pas connecté au courtier. La simulation ne démontre pas une rentabilité future ni un revenu mensuel régulier.
