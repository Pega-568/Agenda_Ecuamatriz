# 05 — Guía Visual Ecuamatriz

## Paleta de colores corporativa

| Nombre             | Hex       | Uso principal                                    |
|--------------------|-----------|--------------------------------------------------|
| Electric Blue      | `#003091` | Color principal. Navbar, headers, botones primarios. |
| Blue Lightning     | `#0057FF` | Acento y hover. Links activos, badges.           |
| Celeste Corporativo| `#48C9E3` | Destacados, alertas informativas, tags.          |
| Gris claro         | `#F3F3F3` | Fondos de sección, fondos de cards.              |
| Gris medio         | `#C0C0C0` | Bordes, separadores, textos secundarios.         |
| Gris oscuro        | `#4D4D4D` | Texto principal sobre fondos claros.             |
| Blanco             | `#FFFFFF` | Fondos de cards, texto sobre fondos oscuros.     |

### Variables CSS

```css
:root {
  /* Paleta corporativa Ecuamatriz */
  --color-primary:     #003091;  /* Electric Blue */
  --color-accent:      #0057FF;  /* Blue Lightning */
  --color-highlight:   #48C9E3;  /* Celeste corporativo */
  --color-bg-light:    #F3F3F3;  /* Gris claro */
  --color-border:      #C0C0C0;  /* Gris medio */
  --color-text:        #4D4D4D;  /* Gris oscuro */
  --color-white:       #FFFFFF;

  /* Estados funcionales */
  --color-success:     #198754;
  --color-warning:     #FFC107;
  --color-danger:      #DC3545;
  --color-info:        #48C9E3;  /* = highlight */

  /* Disponibilidad */
  --color-available:       #198754;
  --color-busy:            #DC3545;
  --color-pending:         #FFC107;
  --color-partial-conflict:#FF6B35;
  --color-out-of-hours:    #6C757D;
  --color-non-working:     #4D4D4D;
}
```

---

## Tipografía

| Tipo             | Fuente              | Fallback        |
|------------------|---------------------|-----------------|
| Sistema principal| **Lato**            | Inter, sans-serif |
| Títulos especiales | Horizon / Frederik | Lato, sans-serif |

> **Regla**: No subir fuentes propietarias al repositorio si no hay licencia clara.
> Horizon y Frederik son fuentes del manual de identidad. Si no están disponibles via licencia,
> usar Lato como fuente única.

### Importación Google Fonts (Lato)

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Lato:wght@300;400;500;700;900&display=swap" rel="stylesheet">
```

```css
body {
  font-family: 'Lato', Inter, -apple-system, BlinkMacSystemFont, sans-serif;
  font-size: 14px;
  color: var(--color-text);
}
```

---

## Escala tipográfica

```css
/* Títulos */
h1 { font-size: 1.75rem; font-weight: 700; color: var(--color-primary); }
h2 { font-size: 1.375rem; font-weight: 700; }
h3 { font-size: 1.125rem; font-weight: 600; }
h4 { font-size: 1rem; font-weight: 600; }

/* Texto */
.text-sm    { font-size: 0.8125rem; }
.text-base  { font-size: 0.875rem; }
.text-lg    { font-size: 1rem; }
.text-muted { color: var(--color-border); }
```

---

## Layout por rol

### Estructura base (3 columnas en sidebar)

```
┌────────────────────────────────────────────────┐
│                   TOPBAR                        │
│  Logo Ecuamatriz    Título módulo    🔔 Usuario │
├────────────┬───────────────────────────────────┤
│            │                                   │
│  SIDEBAR   │        CONTENIDO PRINCIPAL        │
│  Navegación│                                   │
│  por rol   │                                   │
│            │                                   │
└────────────┴───────────────────────────────────┘
```

### Colores de navbar/sidebar por rol

| Rol         | Sidebar                  | Acento activo |
|-------------|--------------------------|---------------|
| Admin       | `#003091` (Electric Blue)| `#0057FF`     |
| Secretaría  | `#003091`                | `#48C9E3`     |
| Usuario     | `#003091`                | `#0057FF`     |

---

## Estados de disponibilidad

Los estados de disponibilidad deben mostrarse con colores consistentes en web y Android:

| Estado               | Color          | Ícono    |
|----------------------|----------------|----------|
| Disponible           | `#198754` verde| ✅        |
| Ocupado (confirmado) | `#DC3545` rojo | 🔴        |
| Pendiente            | `#FFC107` ámbar| 🟡        |
| Conflicto parcial    | `#FF6B35` naranja| 🟠      |
| Fuera de horario     | `#6C757D` gris | ⛔        |
| Día no laborable     | `#4D4D4D` oscuro| ⛔       |
| Sala ocupada         | `#DC3545` rojo | 🔴        |

---

## Componentes UI requeridos

### Botones

```css
.btn-primary {
  background: var(--color-primary);
  color: white;
  border: none;
  border-radius: 6px;
  padding: 8px 20px;
  font-weight: 600;
  transition: background 0.2s;
}
.btn-primary:hover { background: var(--color-accent); }

.btn-secondary {
  background: transparent;
  border: 1.5px solid var(--color-primary);
  color: var(--color-primary);
}

.btn-danger { background: #DC3545; color: white; }
```

### Cards

```css
.card {
  background: white;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.08);
}
```

### Notificaciones badge

```css
.notification-badge {
  background: var(--color-accent);
  color: white;
  border-radius: 50%;
  font-size: 0.7rem;
  font-weight: 700;
  padding: 2px 6px;
}
```

---

## Principios de diseño

1. **Diseño empresarial, sobrio y limpio.** Sin saturación visual.
2. **Consistencia.** Los mismos colores y componentes en todo el sistema.
3. **Información clara.** El estado de cada elemento debe ser inmediatamente legible.
4. **Espaciado generoso.** No amontonar información. Usar margen y padding adecuados.
5. **Responsive.** El sistema web debe funcionar en tablet y computador de oficina.
6. **No inventar colores.** Usar solo la paleta definida.

---

## Normas de uso de la identidad

- **Sí**: Usar la paleta corporativa en todos los componentes.
- **No**: Usar los colores generados automáticamente por Stitch como definitivos.
- **No**: Saturar pantallas con demasiados elementos.
- **No**: Usar gradientes no corporativos o colores sin justificación.
- **No**: Cambiar colores del sidebar por módulo sin decisión de diseño documentada.

---

*Guía visual — Fase 0 — Agenda Ecuamatriz*
