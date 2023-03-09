![Logo DSA](https://media.discordapp.net/attachments/878387055409901639/1047905038464462968/dark_logo.png)
# Directe Saint Aubin
Ce repo est la partie backend de DSA.
Le backend (API) ne rend aucune template (sauf login.html) et renvoies uniquement du JSON et le frontend utilisera sveltekit afin de rendre l'expérience utilisateur plus rapide.

###### Se connecter à ED par l'API.
> **Via cURL:**
```bat
curl -X POST -d "username=<nomdutilisateur>&password=<motdepasse>" http://localhost:5000/login
```  
> **Via Powershell:**
```Powershell
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
Invoke-WebRequest -UseBasicParsing -Uri "http://localhost:5000/login" -Method "POST" -Body "username=<nomdutilisateur>&password=<motdepasse>"
```
