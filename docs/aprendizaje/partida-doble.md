# Partida doble (contabilidad, lo justo para este proyecto)

## La idea en una frase

Todo movimiento de dinero se anota **dos veces**: de dónde salió y a dónde entró. Las dos
anotaciones siempre suman lo mismo. Si no cuadran, hay un error.

## Vocabulario

| Término | Qué es |
|---|---|
| **Cuenta** | Una "bolsa" donde se acumula un tipo de valor: Caja, Bancos, Cuentas por cobrar, Ingresos por ventas, Gastos... El catálogo de todas las cuentas es el **plan de cuentas**. |
| **Asiento** | El registro de un hecho económico. Tiene una fecha, una descripción, y varias **líneas**. |
| **Línea de asiento** | Una anotación en una cuenta: un monto en la columna **débito** o en la columna **crédito**. |
| **Débito / Crédito** | Las dos columnas. No significan "entra/sale" ni "bueno/malo" — son solo izquierda y derecha. Lo que significan depende del tipo de cuenta (ver abajo). |

## La regla de oro

**En cada asiento, la suma de todos los débitos = la suma de todos los créditos.**

Ejemplo: pagas $100.000 de arriendo desde el banco.

| Cuenta | Débito | Crédito |
|---|---:|---:|
| Gastos (arriendo) | 100.000 | |
| Bancos | | 100.000 |
| **Totales** | **100.000** | **100.000** ✓ |

El gasto "aumenta" con un débito; el banco "disminuye" con un crédito. El asiento cuadra.

## Débito o crédito, ¿cuál aumenta la cuenta?

Depende de la **naturaleza** de la cuenta:

| Tipo de cuenta | Aumenta con | Su saldo normal es |
|---|---|---|
| Activo (Caja, Bancos, Cuentas por cobrar) | Débito | débito − crédito |
| Gasto | Débito | débito − crédito |
| Pasivo (Cuentas por pagar, Impuestos) | Crédito | crédito − débito |
| Patrimonio (Capital) | Crédito | crédito − débito |
| Ingreso (Ventas) | Crédito | crédito − débito |

Esto es exactamente lo que hace `calcular_balance()` en el código: para cada cuenta, aplica
la resta según su tipo.

## Por qué el proyecto usa partida doble (y no algo más simple)

Se evaluó "partida simple" (anotar cada movimiento una sola vez, como una libreta de
ingresos y egresos). Se descartó porque:

- El dueño ya maneja el concepto de partida doble.
- La contabilidad formal en Colombia (DIAN, NIIF) la exige. Empezar simple obligaría a una
  migración costosa después.
- La regla "débito = crédito" es una **red de seguridad automática**: cualquier error de
  registro que descuadre el asiento se detecta al instante, antes de guardarlo.

## Cómo aparece esto en el código

- Tablas: `cuenta`, `asiento`, `linea_asiento` (en `app/contabilidad/models.py`).
- La regla de oro: el método `Asiento.cuadra()` y la función `crear_asiento()`, que **es el
  único camino** para escribir un asiento. Nadie inserta líneas sueltas.
- El usuario normal **no piensa en débito/crédito**: registra "una factura recibida de
  $500.000 + $95.000 de IVA" y el sistema arma el asiento correcto por él. Las tablas de
  esas reglas están en
  [`../features/facturas/spec.md`](../features/facturas/spec.md) y
  [`../features/pagos/spec.md`](../features/pagos/spec.md).

## Los dos libros: oficial e interno

El proyecto lleva **dos contabilidades en paralelo** sobre el mismo plan de cuentas:

- **Libro oficial**: la contabilidad real. Todo asiento exige un documento de soporte
  (número de factura, recibo...). Es lo que cuenta para el balance y para la DIAN.
- **Libro interno** ("para-contabilidad"): movimientos que se quieren rastrear pero no
  tienen soporte formal (el dueño saca efectivo para un gasto personal, un préstamo
  informal). Se registran igual con partida doble, pero **no aparecen en el balance
  oficial** salvo que se pida expresamente.

Así se puede comparar la "caja oficial" con la "caja real" (oficial + interno).
