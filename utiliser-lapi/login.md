# 🔐 Login

{% hint style="warning" %}
Avant tout, il faut se connecter pour récupérer le token.
{% endhint %}

{% swagger method="post" path="/login/" baseUrl="https://directesaapi.azurewebsites.net" summary="Se connecter à ED" %}
{% swagger-description %}

{% endswagger-description %}

{% swagger-parameter in="body" required="true" name="username" %}
nom d'utilisateur
{% endswagger-parameter %}

{% swagger-parameter in="body" name="password" required="true" %}
mot de passe
{% endswagger-parameter %}

{% swagger-response status="200: OK" description="Identifiants corrects" %}

{% endswagger-response %}

{% swagger-response status="401: Unauthorized" description="Invalid credentials (Identifiants incorrects)" %}

{% endswagger-response %}
{% endswagger %}

