"""
Script de prueba para el endpoint de generación de PDF de requisitos.

Este script simula el flujo completo:
1. Datos de ejemplo de requisitos
2. Envío al endpoint /generate-pdf
3. Descarga del PDF generado

Uso:
    python test_pdf_generation.py
"""

import requests
import json
from datetime import datetime

# URL del servidor (ajustar si es necesario)
BASE_URL = "http://localhost:8000/api/scraping"

def test_pdf_generation():
    """Prueba la generación de PDF con datos de ejemplo."""

    print("\n" + "="*60)
    print("🧪 PRUEBA DE GENERACIÓN DE PDF")
    print("="*60)

    # Datos de ejemplo de requisitos
    sample_data = {
        "app_id": "com.example.banking.app",
        "fecha_generacion": datetime.now().isoformat(),
        "total_comentarios_analizados": 150,
        "requisitos": [
            {
                "id": "NFR-001",
                "categoria": "autenticidad",
                "requisito": "El sistema debe implementar autenticación biométrica (huella digital y reconocimiento facial) con una tasa de error menor al 1%",
                "prioridad": "Alta",
                "justificacion": "Múltiples usuarios reportan problemas con el inicio de sesión por huella digital, afectando la experiencia de usuario y la seguridad de acceso",
                "criterios_aceptacion": [
                    "Soporte para autenticación por huella digital en dispositivos compatibles",
                    "Soporte para reconocimiento facial en dispositivos compatibles",
                    "Tiempo de respuesta de autenticación menor a 2 segundos",
                    "Fallback a contraseña en caso de fallo biométrico",
                    "Tasa de falsos positivos menor al 0.1%"
                ],
                "comentarios_relacionados": 23
            },
            {
                "id": "NFR-002",
                "categoria": "confidencialidad",
                "requisito": "El sistema debe cifrar todos los datos sensibles usando AES-256 tanto en reposo como en tránsito",
                "prioridad": "Alta",
                "justificacion": "Usuarios expresan preocupación por la seguridad de sus datos personales y financieros",
                "criterios_aceptacion": [
                    "Cifrado AES-256 para todos los datos sensibles almacenados",
                    "Uso de TLS 1.3 o superior para comunicaciones",
                    "Implementación de certificado SSL válido",
                    "Auditoría de seguridad trimestral",
                    "Cumplimiento con GDPR y regulaciones locales"
                ],
                "comentarios_relacionados": 18
            },
            {
                "id": "NFR-003",
                "categoria": "integridad",
                "requisito": "El sistema debe implementar checksums y validación de integridad para todas las transacciones financieras",
                "prioridad": "Alta",
                "justificacion": "Se reportaron casos de pérdida o corrupción de datos en transacciones",
                "criterios_aceptacion": [
                    "Validación de integridad mediante checksums SHA-256",
                    "Logs auditables de todas las transacciones",
                    "Mecanismo de rollback ante detección de anomalías",
                    "Backup automático cada 24 horas",
                    "Verificación de integridad antes de cada operación crítica"
                ],
                "comentarios_relacionados": 12
            },
            {
                "id": "NFR-004",
                "categoria": "resistencia",
                "requisito": "El sistema debe tener una disponibilidad del 99.9% con mecanismos de recuperación automática ante fallos",
                "prioridad": "Media",
                "justificacion": "Usuarios reportan caídas frecuentes de la aplicación y tiempos de inactividad prolongados",
                "criterios_aceptacion": [
                    "Disponibilidad mínima del 99.9% mensual",
                    "Tiempo de recuperación ante fallos menor a 5 minutos",
                    "Balanceo de carga automático",
                    "Failover automático a servidores de respaldo",
                    "Monitoreo 24/7 con alertas automáticas"
                ],
                "comentarios_relacionados": 31
            },
            {
                "id": "NFR-005",
                "categoria": "no_repudio",
                "requisito": "El sistema debe mantener un log auditable de todas las acciones críticas con firma digital",
                "prioridad": "Media",
                "justificacion": "Necesidad de trazabilidad para investigación de disputas y auditorías",
                "criterios_aceptacion": [
                    "Registro con timestamp de todas las transacciones",
                    "Firma digital de logs para prevenir alteración",
                    "Retención de logs por mínimo 7 años",
                    "Interfaz de consulta de historial para usuarios",
                    "Exportación de logs en formato auditable"
                ],
                "comentarios_relacionados": 8
            },
            {
                "id": "NFR-006",
                "categoria": "responsabilidad",
                "requisito": "El sistema debe implementar un sistema de auditoría que registre quién, cuándo y qué modificó en cada operación",
                "prioridad": "Baja",
                "justificacion": "Se requiere accountability para cumplir con regulaciones bancarias",
                "criterios_aceptacion": [
                    "Registro de usuario, timestamp y acción para cada operación",
                    "Trazabilidad de modificaciones en datos críticos",
                    "Reportes de auditoría generables por administradores",
                    "Almacenamiento inmutable de registros de auditoría",
                    "Interfaz de consulta para auditorías internas"
                ],
                "comentarios_relacionados": 5
            }
        ],
        "resumen": {
            "total_requisitos": 6,
            "por_categoria": {
                "autenticidad": 1,
                "confidencialidad": 1,
                "integridad": 1,
                "resistencia": 1,
                "no_repudio": 1,
                "responsabilidad": 1
            },
            "prioridad_alta": 3,
            "prioridad_media": 2,
            "prioridad_baja": 1
        }
    }

    print("\n📊 Datos de prueba:")
    print(f"   App ID: {sample_data['app_id']}")
    print(f"   Requisitos: {len(sample_data['requisitos'])}")
    print(f"   Comentarios analizados: {sample_data['total_comentarios_analizados']}")

    # Intentar conectar al servidor
    try:
        print(f"\n🌐 Conectando a {BASE_URL}/generate-pdf...")

        response = requests.post(
            f"{BASE_URL}/generate-pdf",
            json=sample_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )

        # Verificar respuesta
        if response.status_code == 200:
            print("✅ PDF generado exitosamente!")

            # Guardar el PDF
            filename = f"requisitos_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            with open(filename, 'wb') as f:
                f.write(response.content)

            print(f"\n📄 PDF guardado en: {filename}")
            print(f"   Tamaño: {len(response.content)} bytes")
            print("\n✅ Prueba completada exitosamente!")
            print("\n💡 Abre el archivo PDF para verificar el contenido")

        else:
            print(f"\n❌ Error {response.status_code}: {response.text}")

    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: No se pudo conectar al servidor")
        print("   Asegúrate de que el servidor esté ejecutándose:")
        print("   python main.py")

    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")

    print("\n" + "="*60 + "\n")


def test_with_minimal_data():
    """Prueba con datos mínimos."""

    print("\n" + "="*60)
    print("🧪 PRUEBA CON DATOS MÍNIMOS")
    print("="*60)

    minimal_data = {
        "app_id": "com.test.app",
        "fecha_generacion": datetime.now().isoformat(),
        "total_comentarios_analizados": 10,
        "requisitos": [
            {
                "id": "NFR-001",
                "categoria": "autenticidad",
                "requisito": "El sistema debe implementar autenticación de dos factores",
                "prioridad": "Alta",
                "justificacion": "Mejorar la seguridad del acceso",
                "criterios_aceptacion": [
                    "Soporte para SMS",
                    "Soporte para email",
                    "Soporte para aplicación autenticadora"
                ],
                "comentarios_relacionados": 5
            }
        ],
        "resumen": {
            "total_requisitos": 1,
            "por_categoria": {
                "autenticidad": 1
            },
            "prioridad_alta": 1,
            "prioridad_media": 0,
            "prioridad_baja": 0
        }
    }

    try:
        response = requests.post(
            f"{BASE_URL}/generate-pdf",
            json=minimal_data,
            timeout=30
        )

        if response.status_code == 200:
            filename = f"requisitos_minimal_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            with open(filename, 'wb') as f:
                f.write(response.content)
            print(f"✅ PDF mínimo generado: {filename}")
        else:
            print(f"❌ Error {response.status_code}: {response.text}")

    except Exception as e:
        print(f"❌ ERROR: {str(e)}")

    print("="*60 + "\n")


if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║  Test de Generación de PDF de Requisitos                ║
    ║  Flash Elicit - Sistema de Elicitación de Requisitos    ║
    ╚══════════════════════════════════════════════════════════╝
    """)

    print("⚠️  IMPORTANTE: Asegúrate de que el servidor esté ejecutándose:")
    print("   python main.py\n")

    # Ejecutar pruebas
    test_pdf_generation()
    test_with_minimal_data()

    print("\n✅ Todas las pruebas completadas\n")
