# l10n_mx_hm_express
Desarrollo personalizado para HM Express

## Facturación desde remisiones

La cantidad pendiente es una referencia: se puede facturar una cantidad mayor
para los productos de las remisiones seleccionadas. El saldo se descuenta al
confirmar la factura; crearla en borrador no modifica el reporte.

Por ejemplo, con 4 unidades pendientes y una factura de 6 unidades, el pendiente
queda en -2. El total pendiente conserva el signo: con un costo promedio de 10,
el total será -20. Se puede seguir facturando aunque el saldo ya sea cero o negativo.

Para aplicar el cambio, desplegar el módulo actualizado en el servidor y reiniciar
los procesos de Odoo que lo cargan.

## Pruebas en Odoo 18

En una base de pruebas con el módulo instalado, ejecutar con la configuración
habitual del servidor y la carpeta padre del módulo incluida en `addons_path`:

```sh
odoo-bin -d BASE_DE_PRUEBAS -u l10n_mx_hm_express --test-enable --test-tags /l10n_mx_hm_express --stop-after-init
```

Las pruebas cubren la creación y confirmación de facturas, los saldos negativos,
la facturación repetida, las líneas repetidas del mismo producto, la existencia
de remisiones y las facturas ordinarias.
