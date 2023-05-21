# DirecteSaintAubin API

![Logo DSA](https://media.discordapp.net/attachments/878387055409901639/1047905038464462968/dark\_logo.png)

## Directe Saint Aubin

> **Warning**  
> Ce repo, une fois fini sur la partie EcoleDirecte deviendra privé, un nouveau repo sera créé pour ne laisser que la partie ED, bien évidemment sous license

Ce repo est la partie backend de DSA. Le backend (API) ne rend aucune template (sauf login.html), renvoies uniquement du JSON et le frontend utilisera ionic-vue afin de rendre l'expérience utilisateur plus rapide.

**Se connecter à ED par l'API.**

> **Via cURL:**

```bash
curl -X POST -d "username=[*nomdutilisateur]&password=[*motdepasse]" http://[*host]:[*port]/login/
```

[O] Vie scolaire  
[O] Notes  
[-] Messagerie  
[O] Emploi du temps  
[O] Cahier de textes  
[-] Mon cloud  
[-] Espaces de travail  
