# Utilisation Docker pour llama.cpp

## Construction de l'image

```bash
docker build -t llama_cpp ./llama.cpp
```

## Lancement du conteneur

```bash
docker run -it --rm llama_cpp
```

## Utilisation avec Docker Compose

```bash
docker compose up --build
```

Le dossier `/workspace` dans le conteneur correspond au dossier `llama.cpp` du projet.

Adapte le Dockerfile et le script de build selon tes besoins spécifiques.
