# DirecteSaintAubin API

![Logo DSA](https://cdn.discordapp.com/attachments/1124328411595288576/1149778551827079268/yWkUEnU.png)

## Directe Saint Aubin


> **Warning**  
> Ce repo, une fois fini sur la partie EcoleDirecte deviendra privé, un nouveau repo sera créé pour ne laisser que la partie ED, bien évidemment sous license

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
| Espaces de travail | En pause (vacances) |
| Cloud | PAS OK |
