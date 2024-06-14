# DirecteSaintAubin API

![](https://raw.githubusercontent.com/noappertBD/DirecteStAubin/main/static/img/banner.png)

## Directe Saint Aubin


> **Warning**  
> DirecteStAubin n'est plus maintenu

Ce repo est la partie backend de DSA. Le backend (API) ne rend aucune template (sauf login.html), renvoies uniquement du JSON et le frontend utilisera ionic-vue afin de rendre l'expérience utilisateur plus rapide.

**Se connecter à ED par l'API.**

> **Via cURL:**

```bash
curl -X POST -d "username=[*nomdutilisateur]&password=[*motdepasse]" http://[*host]:[*port]/login/
```

| Fonctionnalités | Status |
| ------------ | ------------ |
| Emploi du temps | OK |
| Vie scolaire | OK |
| Devoirs | OK |
| Notes | OK |
| Messagerie | OK |
| Espaces de travail | En cours... |
| Cloud | PAS OK |
