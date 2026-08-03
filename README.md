# OdontologiaPaulaMunoz

Sitio web de la **Clínica Odontológica Dra. Paula Muñoz** — Envigado, Antioquia.

Sitio estático, sin build ni dependencias. Se abre `index.html` en el navegador
y funciona; se publica subiendo los archivos tal cual.

## Estructura

```
index.html      Página completa (español). Incluye datos estructurados
                schema.org/Dentist para búsqueda local.
css/styles.css  Estilos. La paleta vive en :root.
js/main.js      Dibuja la arcada dental interactiva del encabezado.
```

## La arcada

El elemento central es un odontograma de la arcada superior. Los dientes se
dibujan con sus medidas reales de corona en milímetros (ancho mesiodistal ×
altura) y se reparten sobre una elipse por longitud de arco, de modo que los
puntos de contacto entre dientes vecinos cierran igual que en una boca.

Cada zona lleva a un tratamiento, y la relación es clínica, no decorativa:

| Zona | Tratamiento | Por qué ahí |
|------|-------------|-------------|
| Incisivos (12–22) | Blanqueamiento y diseño de sonrisa | Son los dientes que se ven al hablar |
| Caninos (13, 23) | Ortodoncia | El canino guía la mordida |
| Premolares (14–25) | Rehabilitación oral | Reparten la fuerza al masticar |
| Molares (16–27) | Limpieza dental | El sarro se acumula donde desemboca la glándula salival |
| Cordales (18, 28) | Cirugía maxilofacial | Muelas del juicio |
| Encía | Periodoncia | Sostiene el diente |

La numeración es FDI, la misma de la historia clínica.

La arcada es un realce. Sin JavaScript, la lista de tratamientos sigue siendo
contenido real y legible, y los buscadores la indexan igual.

## Pendiente

Cosas que necesitan material de la clínica y quedaron marcadas en el HTML:

- **Fotos.** Hoy no hay ninguna: el diseño se sostiene con tipografía y color.
  Faltan fotos del consultorio, del equipo y casos de antes/después.
- **Biografía de la Dra. Muñoz** (`#clinica`). El párrafo actual es genérico a
  propósito; hay que reemplazarlo con formación y trayectoria reales.
- **Testimonios.** Solo hay uno verificado. Los demás deben salir de reseñas
  reales de pacientes.
- **Dominio.** Las etiquetas `canonical` y `og:url` apuntan a
  `clinicaodontologicapaulamunoz.com`; ajustar al dominio definitivo.

## Publicar

Cualquier hosting estático sirve. Con GitHub Pages: Settings → Pages → Deploy
from a branch → `main` / `root`.
