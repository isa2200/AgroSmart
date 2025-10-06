# Carpeta de Imágenes - AgroSmart

Esta carpeta contiene todas las imágenes estáticas del proyecto AgroSmart.

## Archivos:
- `logo-ico.ico` - Favicon del sitio web
- `logo.png` - Logo principal (si se agrega)

## Uso:
Para usar las imágenes en los templates, utiliza:
```html
{% load static %}
<img src="{% static 'img/nombre-imagen.ext' %}" alt="Descripción">
```

Para el favicon:
```html
<link rel="icon" type="image/x-icon" href="{% static 'img/logo-ico.ico' %}">
```