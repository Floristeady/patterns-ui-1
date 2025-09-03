# 🔗 Content-Template Merger

Script para combinar el JSON del **Content** con el HTML template del **Materializer** en el modo Chain.

## 🎯 **¿Para qué sirve?**

El modo Chain genera:
1. **Content (JSON)**: Datos estructurados
2. **Materializer (HTML)**: Template con placeholders `{{variable}}`

Este script **los une automáticamente** para crear el HTML final con contenido real.

## 🚀 **Uso Rápido**

### **Opción 1: Con archivos locales**
```bash
python3 merge_content_template.py \
  --json content.json \
  --html template.html \
  --output result.html
```

### **Opción 2: Desde API session (cuando funcione)**
```bash
python3 merge_content_template.py \
  --session-id abc123-def456-ghi789 \
  --output result.html
```

## 📋 **Ejemplo Completo**

### **1. Probar con archivos de ejemplo:**
```bash
# Usar los archivos de ejemplo incluidos
python3 merge_content_template.py \
  --json docs/example_content.json \
  --html docs/example_template.html \
  --output demo.html

# Abrir resultado
open demo.html
```

### **2. Estructura del JSON (Content):**
```json
{
  "title": "Product Comparison Table",
  "subtitle": "Compare features and specifications",
  "productComparison": [
    {
      "name": "MacBook Pro 16\"",
      "price": "$2,499",
      "processor": "M3 Max"
    }
  ]
}
```

### **3. Template HTML (Materializer):**
```html
<h1>{{title}}</h1>
<p>{{subtitle}}</p>
<table>
  <tr>
    <td>{{productComparison_1_name}}</td>
    <td>{{productComparison_1_price}}</td>
  </tr>
</table>
```

### **4. Resultado Final:**
```html
<h1>Product Comparison Table</h1>
<p>Compare features and specifications</p>
<table>
  <tr>
    <td>MacBook Pro 16"</td>
    <td>$2,499</td>
  </tr>
</table>
```

## 🧠 **Cómo Funciona el Mapeo Inteligente**

### **1. Mapeo Exacto**
- `{{title}}` → `"title": "Product Comparison"`

### **2. Mapeo por Palabras Clave**
- `{{product_name}}` → busca campos con "name", "title", "label"
- `{{description}}` → busca "description", "desc", "content", "text"
- `{{price}}` → busca "price", "cost", "amount", "value"

### **3. Mapeo por Arrays**
- `{{productComparison_1_name}}` → primer elemento del array
- `{{productComparison_2_price}}` → segundo elemento, campo price

### **4. Mapeo por Similitud**
- Compara palabras en común entre placeholder y datos JSON

## 🛠️ **Casos de Uso**

### **Para Developers:**
```bash
# Probar diferentes combinaciones
python3 merge_content_template.py --json data.json --html layout.html

# Generar múltiples versiones
for template in templates/*.html; do
  python3 merge_content_template.py \
    --json content.json \
    --html "$template" \
    --output "result_$(basename $template)"
done
```

### **Para Testing:**
```bash
# Verificar que todos los placeholders se llenan
python3 merge_content_template.py \
  --json test_data.json \
  --html template.html | grep -o "{{[^}]*}}"
```

## 📁 **Archivos Incluidos**

- `merge_content_template.py` - Script principal
- `docs/example_content.json` - Datos de ejemplo (Product comparison)
- `docs/example_template.html` - Template de ejemplo (Tabla responsive)
- `README_MERGER.md` - Esta documentación

## 🔧 **Personalización**

### **Agregar nuevas palabras clave:**
Edita el diccionario `keyword_map` en el script:
```python
keyword_map = {
    'title': ['title', 'name', 'heading', 'header'],
    'description': ['description', 'desc', 'content', 'text'],
    'custom_field': ['custom', 'special', 'unique'],  # ← Agregar aquí
}
```

### **Cambiar formato de placeholders:**
Modifica `placeholder_pattern`:
```python
# Para usar ${variable} en lugar de {{variable}}
self.placeholder_pattern = re.compile(r'\$\{([^}]+)\}')
```

## 🎯 **Próximos Pasos**

1. **Integrar con Chain mode**: Automáticamente ejecutar merge al completar Chain
2. **UI Web**: Interfaz web para hacer merge sin línea de comandos
3. **Templates predefinidos**: Biblioteca de templates comunes
4. **Validación**: Verificar que todos los placeholders se llenan

## 🚀 **¡Listo para usar!**

```bash
# Prueba rápida
python3 merge_content_template.py \
  --json docs/example_content.json \
  --html docs/example_template.html \
  --output my_result.html && open my_result.html
```
