# VisionGuard

Servicio Flask que detecta rostros en una imagen y devuelve una copia con los
rostros difuminados.

## Requisitos

- Python 3.14 o superior
- [uv](https://docs.astral.sh/uv/)
- Redis opcional. Si Redis no está disponible, se usa un limitador local en
  memoria.

## Ejecutar

```sh
uv sync
uv run visionguard
```

El servidor escucha en `127.0.0.1:8080`. Para cambiar la dirección o el puerto,
define `HOST` o `PORT`. `REDIS_HOST` permite configurar el host de Redis
(predeterminado: `redis`). El modo de depuración permanece desactivado.

## API

Envía una imagen como campo multipart `image`:

```sh
curl -F image=@foto.jpg http://127.0.0.1:8080/api/blur --output blurred.jpg
```

La respuesta es una imagen JPEG y contiene el número de rostros detectados en
la cabecera `X-Faces-Found`. Las cargas están limitadas a 10 MB.

## Pruebas

```sh
uv run python -m unittest discover -s tests
```