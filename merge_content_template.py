#!/usr/bin/env python3
"""
Content-Template Merger
Combina el JSON del Content con el HTML template del Materializer
"""

import json
import re
import sys
from pathlib import Path
from typing import Dict, Any, List
import argparse


class ContentTemplateMerger:
    """Combina contenido JSON con templates HTML"""
    
    def __init__(self):
        self.placeholder_pattern = re.compile(r'\{\{([^}]+)\}\}')
    
    def extract_placeholders(self, html_template: str) -> List[str]:
        """Extrae todos los placeholders del template HTML"""
        return list(set(self.placeholder_pattern.findall(html_template)))
    
    def flatten_json(self, data: Any, prefix: str = "") -> Dict[str, str]:
        """Aplana estructura JSON anidada en un diccionario plano"""
        result = {}
        
        if isinstance(data, dict):
            for key, value in data.items():
                new_key = f"{prefix}_{key}" if prefix else key
                if isinstance(value, (dict, list)):
                    result.update(self.flatten_json(value, new_key))
                else:
                    result[new_key] = str(value)
        
        elif isinstance(data, list):
            for i, item in enumerate(data):
                new_key = f"{prefix}_{i+1}" if prefix else f"item_{i+1}"
                if isinstance(item, (dict, list)):
                    result.update(self.flatten_json(item, new_key))
                else:
                    result[new_key] = str(item)
        
        else:
            result[prefix or "value"] = str(data)
        
        return result
    
    def smart_mapping(self, placeholders: List[str], json_data: Dict[str, str]) -> Dict[str, str]:
        """Mapeo inteligente de placeholders a datos JSON"""
        mapping = {}
        
        # Crear variaciones de keys para matching flexible
        json_keys_lower = {k.lower(): v for k, v in json_data.items()}
        
        for placeholder in placeholders:
            placeholder_clean = placeholder.strip().lower()
            
            # Estrategias de matching (en orden de prioridad)
            strategies = [
                # 1. Match exacto
                lambda p: json_data.get(p),
                lambda p: json_keys_lower.get(p),
                
                # 2. Match por palabras clave
                lambda p: self._match_by_keywords(p, json_data),
                
                # 3. Match por similitud
                lambda p: self._match_by_similarity(p, json_data),
                
                # 4. Match por posición (para arrays)
                lambda p: self._match_by_position(p, json_data),
            ]
            
            value = None
            for strategy in strategies:
                value = strategy(placeholder_clean)
                if value:
                    break
            
            mapping[placeholder] = value or f"[{placeholder}]"  # Fallback
        
        return mapping
    
    def _match_by_keywords(self, placeholder: str, data: Dict[str, str]) -> str:
        """Match basado en palabras clave comunes"""
        keyword_map = {
            'title': ['title', 'name', 'heading', 'header'],
            'name': ['name', 'title', 'label'],
            'description': ['description', 'desc', 'content', 'text', 'summary'],
            'price': ['price', 'cost', 'amount', 'value'],
            'image': ['image', 'img', 'photo', 'picture'],
            'url': ['url', 'link', 'href'],
            'date': ['date', 'time', 'created', 'updated'],
        }
        
        # Buscar por palabra clave en el placeholder
        for key_type, keywords in keyword_map.items():
            if any(kw in placeholder for kw in keywords):
                # Buscar en los datos
                for data_key, data_value in data.items():
                    if any(kw in data_key.lower() for kw in keywords):
                        return data_value
        
        return None
    
    def _match_by_similarity(self, placeholder: str, data: Dict[str, str]) -> str:
        """Match por similitud de strings"""
        best_match = None
        best_score = 0
        
        for data_key, data_value in data.items():
            # Calcular similitud simple (palabras en común)
            placeholder_words = set(placeholder.lower().split('_'))
            data_words = set(data_key.lower().split('_'))
            
            common_words = placeholder_words.intersection(data_words)
            score = len(common_words) / max(len(placeholder_words), 1)
            
            if score > best_score and score > 0.3:  # Threshold mínimo
                best_score = score
                best_match = data_value
        
        return best_match
    
    def _match_by_position(self, placeholder: str, data: Dict[str, str]) -> str:
        """Match por posición para elementos numerados"""
        # Buscar números en el placeholder
        numbers = re.findall(r'\d+', placeholder)
        if not numbers:
            return None
        
        num = numbers[0]
        
        # Buscar keys que contengan ese número
        for data_key, data_value in data.items():
            if num in data_key:
                return data_value
        
        return None
    
    def merge(self, json_content: str, html_template: str) -> str:
        """Combina JSON content con HTML template"""
        try:
            # Parse JSON
            content_data = json.loads(json_content)
            
            # Aplanar datos JSON
            flat_data = self.flatten_json(content_data)
            
            # Extraer placeholders
            placeholders = self.extract_placeholders(html_template)
            
            # Mapear placeholders a datos
            mapping = self.smart_mapping(placeholders, flat_data)
            
            # Reemplazar en template
            result_html = html_template
            for placeholder, value in mapping.items():
                pattern = r'\{\{' + re.escape(placeholder) + r'\}\}'
                result_html = re.sub(pattern, str(value), result_html)
            
            return result_html
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON content: {e}")
        except Exception as e:
            raise ValueError(f"Merge error: {e}")
    
    def merge_from_files(self, json_file: str, html_file: str, output_file: str = None):
        """Combina archivos JSON y HTML"""
        json_path = Path(json_file)
        html_path = Path(html_file)
        
        if not json_path.exists():
            raise FileNotFoundError(f"JSON file not found: {json_file}")
        if not html_path.exists():
            raise FileNotFoundError(f"HTML file not found: {html_file}")
        
        # Leer archivos
        json_content = json_path.read_text(encoding='utf-8')
        html_template = html_path.read_text(encoding='utf-8')
        
        # Combinar
        result = self.merge(json_content, html_template)
        
        # Guardar resultado
        if output_file:
            output_path = Path(output_file)
            output_path.write_text(result, encoding='utf-8')
            print(f"✅ Merged content saved to: {output_file}")
        else:
            print("✅ Merged HTML:")
            print(result)
        
        return result


def main():
    parser = argparse.ArgumentParser(description="Merge JSON content with HTML template")
    parser.add_argument("--json", help="JSON content file or string")
    parser.add_argument("--html", help="HTML template file")
    parser.add_argument("--output", help="Output HTML file (optional)")
    parser.add_argument("--session-id", help="Fetch from API session ID")
    
    args = parser.parse_args()
    
    # Validar argumentos
    if args.session_id:
        if not args.session_id:
            parser.error("Session ID required when using --session-id")
    else:
        if not args.json or not args.html:
            parser.error("Both --json and --html are required when not using --session-id")
    
    merger = ContentTemplateMerger()
    
    try:
        if args.session_id:
            # Fetch from API
            import requests
            url = f"http://localhost:8000/api/sessions/{args.session_id}"
            response = requests.get(url)
            data = response.json()
            
            if "results" not in data or "responder_phase" not in data["results"]:
                print("❌ No Chain mode data found in session")
                return
            
            # Extract JSON and HTML from session
            model_key = list(data["results"]["responder_phase"].keys())[0]
            json_content = data["results"]["responder_phase"][model_key]["html_content"]
            html_template = data["results"]["materializer_phase"][model_key]["html_content"]
            
            result = merger.merge(json_content, html_template)
            
            if args.output:
                Path(args.output).write_text(result, encoding='utf-8')
                print(f"✅ Merged content saved to: {args.output}")
            else:
                print("✅ Merged HTML:")
                print(result)
        
        else:
            # Use file paths
            merger.merge_from_files(args.json, args.html, args.output)
    
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
