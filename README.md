# DirecteSaintAubin API

![Logo DSA](https://media.discordapp.net/attachments/878387055409901639/1047905038464462968/dark\_logo.png)

## Directe Saint Aubin

> **Warning**  
> Ce repo, une fois fini sur la partie EcoleDirecte deviendra privé, un nouveau repo sera créé pour ne laisser que la partie ED, bien évidemment sous license

Ce repo est la partie backend de DSA. Le backend (API) ne rend aucune template (sauf login.html), renvoies uniquement du JSON et le frontend utilisera sveltekit afin de rendre l'expérience utilisateur plus rapide.

**Se connecter à ED par l'API.**

> **Via cURL:**

```bash
curl -X POST -d "username=[*nomdutilisateur]&password=[*motdepasse]" http://[*host]:[*port]/login/
```

> **Via Powershell:**

```powershell
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
Invoke-WebRequest -UseBasicParsing -Uri "http://[*host]:[*port]/login" -Method "POST" -Body "username=[*nomdutilisateur]&password=[*motdepasse]"
```
