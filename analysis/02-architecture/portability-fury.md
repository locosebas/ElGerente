# Portabilidad: Fury ↔ Cloud independiente

**Fecha**: 2026-04-10  
**Estado**: Decisión tomada — aprobada en sesión de brainstorming

## Requerimiento

El sistema debe poder correr en Fury (MercadoLibre) como plataforma inicial, pero **sin acoplarse a Fury**. Debe poder migrarse a AWS, GCP, VPS, o cualquier cloud sin reescribir el core del negocio.

## Solución: Arquitectura Hexagonal (Ports & Adapters)

El core del negocio (ventas, inventario, facturas, para-contabilidad, agentes IA) **no sabe dónde está corriendo**. Solo habla con interfaces abstractas (puertos). Los adaptadores concretos cambian por entorno.

```
┌─────────────────────────────────────────────┐
│           CORE DEL NEGOCIO                  │
│  Ventas · Inventario · Facturas             │
│  Para-contabilidad · Agentes IA             │
│                                             │
│  IStorageService  IQueueService             │
│  ISecretService   IFileStorage              │
│  IEmailService                              │
└────────────┬────────────────────────────────┘
             │ interfaces abstractas
    ┌────────┼────────────┐
    ▼        ▼            ▼
 Fury      AWS          Local
 Adapter   Adapter      Adapter
```

## Regla de oro

> Ningún import de SDK de Fury en el core del negocio. Solo en la capa de adaptadores.  
> Si se saca Fury, solo se cambian los adaptadores — el resto no se toca.

## Qué queda igual en todos los entornos

- **Docker**: mismo contenedor corre en Fury, AWS o laptop
- **Config via ENV**: sin hardcodear rutas ni secrets de Fury en el código
- **PostgreSQL estándar**: sin usar Aurora-específico ni bases propietarias

## Qué cambia por entorno (solo los adaptadores)

| Servicio | En Fury | En AWS / Cloud | Local / Dev |
|---|---|---|---|
| Base de datos | Aurora MySQL (Fury) | RDS PostgreSQL | PostgreSQL Docker |
| Cola de mensajes | BigQueue | SQS / RabbitMQ | Redis streams |
| Archivos (facturas, fotos) | Fury Object Storage | S3 | Disco local |
| Secrets | Fury Secrets | AWS Secrets Manager | .env file |
| Despliegue | Fury CLI / Scopes | ECS / Kubernetes | docker-compose |

## Decisión

✅ Aprobada — se implementará arquitectura hexagonal desde el inicio.  
El MVP correrá en Fury, pero la estructura de adaptadores se crea desde el día 1.
