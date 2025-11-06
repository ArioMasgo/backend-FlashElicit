# 🚀 Resumen Rápido: Despliegue a Railway

## ¿Qué es Railway?
Railway es una plataforma de despliegue moderna que se conecta directamente con GitHub y despliega tu aplicación automáticamente.

## ✅ Tu Proyecto Ya Está Listo

He preparado tu proyecto con todos los archivos necesarios:

| Archivo | Propósito |
|---------|-----------|
| `Procfile` | Le dice a Railway cómo iniciar tu app |
| `railway.json` | Configuración específica de Railway |
| `runtime.txt` | Especifica Python 3.11 |
| `.gitignore` | Protege tu `.env` de ser subido |
| `requirements.txt` | Lista de dependencias |

## 🔄 Proceso Simple (3 Pasos)

```
┌─────────────────┐
│  1. GitHub      │  ← Sube tu código (sin .env)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  2. Railway     │  ← Conecta GitHub + Copia variables del .env
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  3. ¡Listo! 🎉  │  ← Railway te da una URL pública
└─────────────────┘
```

## 📋 Pasos Detallados

### 1️⃣ Subir a GitHub

```powershell
git add .
git commit -m "Configurar para Railway"
git push origin main
```

**IMPORTANTE:** El `.env` NO se sube (está en `.gitignore`)

### 2️⃣ Crear Proyecto en Railway

1. Ir a: https://railway.app/
2. **Login** con GitHub
3. Click **"New Project"**
4. Seleccionar **"Deploy from GitHub repo"**
5. Elegir tu repositorio: **`backend-FlashElicit`**
6. Railway detecta Python automáticamente ✨

### 3️⃣ Configurar Variables de Entorno

En Railway, ve a **Variables** y agrega las mismas que tienes en tu `.env` local:

```bash
# COPIA LOS VALORES DE TU ARCHIVO .env LOCAL
OPENROUTER_API_KEY=<valor_de_tu_.env>
HF_TOKEN=<valor_de_tu_.env>
REDIS_URL=<valor_de_tu_.env>
SITE_URL=<valor_de_tu_.env>
SITE_NAME=<valor_de_tu_.env>
```

> 💡 **Importante:** Abre tu archivo `.env` local y copia cada valor

### 4️⃣ Obtener URL de Producción

1. Settings → **Domains**
2. Click **"Generate Domain"**
3. Tu API estará en: `https://nombre-aleatorio.up.railway.app`

## 🧪 Probar la API

```bash
# Prueba básica
curl https://tu-proyecto.up.railway.app/

# Health check
curl https://tu-proyecto.up.railway.app/api/health
```

## 🔄 Actualizaciones Automáticas

**¡No necesitas hacer nada más!**

Cada vez que hagas:
```bash
git push origin main
```

Railway **automáticamente**:
1. Detecta el cambio
2. Reconstruye la aplicación
3. Despliega la nueva versión
4. En 2-3 minutos está en producción

## ⚠️ Puntos Críticos

### ❌ NO hagas esto:
- ❌ Subir el `.env` a GitHub
- ❌ Hardcodear API keys en el código
- ❌ Olvidar configurar las variables en Railway

### ✅ SÍ haz esto:
- ✅ Verifica que `.env` está en `.gitignore`
- ✅ Copia TODAS las variables a Railway
- ✅ Prueba la API después de desplegar
- ✅ Actualiza CORS cuando tengas frontend en producción

## 💰 Costos

- **Gratis:** $5 crédito mensual (suficiente para desarrollo)
- Tu app consume aprox. $0.50-$2/mes en uso normal
- Si excedes, Railway te avisa antes de cobrar

## 📊 Monitoreo

En Railway Dashboard:
- **Logs:** Ver en tiempo real qué hace tu app
- **Metrics:** CPU, RAM, requests
- **Deployments:** Historial de despliegues

## 🆘 Si algo falla

1. **Ver logs:** Railway Dashboard → Deployments → Click en el último
2. **Reiniciar:** Settings → Restart
3. **Verificar variables:** Variables tab → Check todas las keys

## 🎯 Siguiente Paso: CORS para Producción

Cuando despliegues tu frontend, actualiza `main.py`:

```python
origins = [
    "http://localhost:4200",  # Desarrollo
    "https://tu-frontend.vercel.app",  # ← Agregar producción
]
```

Haz commit y push para actualizar.

## ✨ Ventajas de Railway

| Ventaja | Descripción |
|---------|-------------|
| 🚀 **Rápido** | Despliegue en 2-3 minutos |
| 🔄 **CD Automático** | Git push = deploy automático |
| 📊 **Logs en vivo** | Ver todo en tiempo real |
| 💳 **Free tier** | $5/mes gratis |
| 🔧 **Sin config** | Detecta Python automáticamente |
| 🔐 **Seguro** | Variables de entorno encriptadas |

---

## 🎬 Resumen Ultra Rápido

```bash
# 1. Verificar que todo está listo
python check_deployment.py

# 2. Subir a GitHub
git push origin main

# 3. Ir a railway.app
# 4. New Project → GitHub → Seleccionar repo
# 5. Agregar variables de .env
# 6. Generar dominio
# 7. ¡Listo! 🎉
```

**Tiempo total:** ~10 minutos

---

¿Necesitas ayuda? Consulta `DEPLOYMENT_RAILWAY.md` para la guía completa.
