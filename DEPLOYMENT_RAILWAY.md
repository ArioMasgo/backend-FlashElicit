# 🚀 Guía de Despliegue en Railway

## Requisitos Previos
- Cuenta en [Railway](https://railway.app/)
- Repositorio de GitHub con tu código
- Archivo `.env` con tus variables de entorno (NO lo subas a GitHub)

## 📦 Archivos Necesarios para el Despliegue

Tu proyecto ya incluye todos los archivos necesarios:

1. **`requirements.txt`** - Dependencias de Python
2. **`Procfile`** - Comando para iniciar la aplicación
3. **`railway.json`** - Configuración específica de Railway
4. **`runtime.txt`** - Versión de Python a usar
5. **`.gitignore`** - Archivos a ignorar (incluye `.env`)

## 🔧 Proceso de Despliegue

### Paso 1: Preparar el Repositorio en GitHub

1. **Asegúrate de que `.env` NO está en GitHub:**
   ```bash
   git status
   # Verifica que .env aparece en .gitignore
   ```

2. **Sube tu código a GitHub:**
   ```bash
   git add .
   git commit -m "Preparar para despliegue en Railway"
   git push origin main
   ```

### Paso 2: Crear Proyecto en Railway

1. Ve a [railway.app](https://railway.app/) y haz login
2. Click en **"New Project"**
3. Selecciona **"Deploy from GitHub repo"**
4. Autoriza Railway para acceder a tus repositorios
5. Selecciona tu repositorio `backend-FlashElicit`
6. Railway detectará automáticamente que es una aplicación Python

### Paso 3: Configurar Variables de Entorno

**MUY IMPORTANTE:** Debes copiar todas las variables de tu archivo `.env` local a Railway.

1. En el dashboard de Railway, ve a tu proyecto
2. Click en la pestaña **"Variables"**
3. Agrega cada variable **una por una** (copia los valores de tu `.env` local):

   ```bash
   # Ejemplo de variables (USA TUS VALORES REALES del archivo .env)
   OPENROUTER_API_KEY=<tu_clave_de_openrouter>
   SITE_URL=<tu_url_del_sitio>
   SITE_NAME=Requirements Elicitation System
   HF_TOKEN=<tu_token_de_hugging_face>
   REDIS_URL=<tu_url_de_redis>
   ```

   ⚠️ **IMPORTANTE:** 
   - Reemplaza `<...>` con tus valores reales del archivo `.env` local
   - NO copies estos ejemplos, usa tus claves reales
   - Railway encripta automáticamente estas variables

4. Railway automáticamente agregará la variable `PORT` (no la agregues manualmente)

### Paso 4: Verificar el Despliegue

1. Railway comenzará a construir y desplegar automáticamente
2. Puedes ver los logs en tiempo real en la pestaña **"Deployments"**
3. El proceso toma aproximadamente 2-5 minutos

### Paso 5: Obtener la URL de Producción

1. Una vez desplegado, ve a **"Settings"** → **"Domains"**
2. Click en **"Generate Domain"**
3. Railway te dará una URL como: `https://tu-proyecto.up.railway.app`

### Paso 6: Probar la API

Prueba tu API en producción:

```bash
curl https://tu-proyecto.up.railway.app/
curl https://tu-proyecto.up.railway.app/api/health
```

## 🔄 Actualizaciones Automáticas

Railway está configurado para **despliegue continuo**:
- Cada vez que hagas `git push` a `main`, Railway desplegará automáticamente
- No necesitas hacer nada más

## ⚙️ Configuraciones Adicionales

### Actualizar CORS para Producción

Cuando tengas tu frontend desplegado, actualiza el archivo `main.py`:

```python
origins = [
    "http://localhost:4200",
    "http://127.0.0.1:4200",
    "https://tu-frontend-produccion.vercel.app",  # Tu dominio de producción
]
```

### Monitoreo y Logs

- **Ver logs:** Railway Dashboard → Tu proyecto → "Deployments" → Click en el deployment actual
- **Métricas:** Railway Dashboard → "Metrics" (CPU, RAM, Network)
- **Reiniciar:** Railway Dashboard → Settings → "Restart"

## 🚨 Troubleshooting

### El deployment falla
- Revisa los logs en Railway
- Verifica que todas las dependencias estén en `requirements.txt`
- Asegúrate de que las variables de entorno estén configuradas

### La aplicación no responde
- Verifica que el puerto esté configurado correctamente (usa `$PORT`)
- Revisa los logs para errores de inicio
- Verifica la conexión a Redis

### Error de CORS
- Agrega el dominio de tu frontend a la lista `origins` en `main.py`
- Haz commit y push para redesplegar

## 💰 Costos

Railway ofrece:
- **Plan gratuito:** $5 de crédito mensual (suficiente para desarrollo/testing)
- **Plan hobby:** $5/mes por proyecto
- **Plan pro:** Facturación por uso

## 📚 Recursos

- [Documentación de Railway](https://docs.railway.app/)
- [Railway Community](https://help.railway.app/)
- [Status de Railway](https://status.railway.app/)

## ✅ Checklist de Despliegue

- [ ] `.env` está en `.gitignore`
- [ ] Código subido a GitHub
- [ ] Proyecto creado en Railway
- [ ] Variables de entorno configuradas (desde tu `.env` local)
- [ ] Deployment exitoso
- [ ] URL generada
- [ ] API probada y funcionando
- [ ] CORS configurado para producción

## 🔐 Seguridad

- ✅ **NUNCA** subas el archivo `.env` a GitHub
- ✅ **NUNCA** hagas hard-code de API keys en el código
- ✅ Verifica que `.env` esté en `.gitignore`
- ✅ Usa variables de entorno en Railway para datos sensibles
- ✅ Revoca tokens si accidentalmente los expones
