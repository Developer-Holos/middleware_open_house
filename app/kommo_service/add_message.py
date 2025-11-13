import os
import requests
import sys

def add_message(lead_id: int, text: str):
    print(f"🚀 Iniciando add_message para lead_id: {lead_id}", flush=True)
    print(f"📝 Texto a agregar: '{text}'", flush=True)

    msj_client_field_id = 1385357  # ID del campo personalizado para mensajes del cliente
    token = os.getenv("TOKEN_KOMMO")
    subdomain = os.getenv("SUBDOMAIN_KOMMO")

    if not token or not subdomain:
        print("❌ Error: Faltan variables de entorno", flush=True)
        raise ValueError("TOKEN_KOMMO o SUBDOMAIN_KOMMO no está definida")

    url = f"https://{subdomain}.kommo.com/api/v4/leads/{lead_id}"
    print(f"🌐 URL: {url}", flush=True)
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    try:
        print("📡 Obteniendo datos del lead...", flush=True)
        response = requests.get(url, headers=headers)
        print(f"✅ Status code GET: {response.status_code}", flush=True)
        
        if response.status_code != 200:
            print(f"❌ Error en GET: {response.text}", flush=True)
            return {"status": "error", "message": f"Error obteniendo lead: {response.status_code} - {response.text}"}

        data = response.json()
        custom_fields_values = data.get("custom_fields_values")
        print(f"📋 Campos actuales: {custom_fields_values}", flush=True)

        # Escenario 1: custom_fields_values es None
        if custom_fields_values is None:
            print("🆕 No hay campos personalizados, creando nuevo campo", flush=True)
            custom_field_update = [{
                "field_id": msj_client_field_id,
                "values": [{"value": text}]
            }]
        else:
            # Escenario 2: Buscar si existe el campo específico
            field_found = False
            for field in custom_fields_values:
                if field.get("field_id") == msj_client_field_id:
                    field_found = True
                    print("🔄 Campo encontrado, actualizando valor existente", flush=True)
                    current_value = field.get("values", [{}])[0].get("value", "")
                    print(f"📝 Valor actual del campo: '{current_value}'", flush=True)
                    custom_field_update = [{
                        "field_id": msj_client_field_id,
                        "values": [{"value": f"{current_value}\n{text}" if current_value else text}]
                    }]
                    break
            
            # Escenario 3: No se encontró el campo específico
            if not field_found:
                print("🆕 Campo no encontrado, creando nuevo campo", flush=True)
                custom_field_update = [{
                    "field_id": msj_client_field_id,
                    "values": [{"value": text}]
                }]

        # Actualizamos el campo
        payload = {"custom_fields_values": custom_field_update}
        print(f"📤 Payload del PATCH: {payload}", flush=True)
        
        print(f"🔧 Ejecutando PATCH a: {url}", flush=True)
        update_response = requests.patch(url, headers=headers, json=payload)
        print(f"📊 Status code PATCH: {update_response.status_code}", flush=True)
        print(f"📄 Respuesta PATCH: {update_response.text}", flush=True)
        
        if update_response.status_code not in (200, 201):
            print(f"❌ PATCH falló con status {update_response.status_code}", flush=True)
            return {
                "status": "error", 
                "message": f"Error actualizando lead: {update_response.status_code} - {update_response.text}"
            }

        print(f"✅ Mensaje agregado exitosamente al lead {lead_id}", flush=True)
        return {"status": "ok", "message": "Mensaje agregado correctamente"}

    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}", flush=True)
        return {"status": "error", "message": f"Error de conexión: {str(e)}"}
    except ValueError as e:
        print(f"❌ Error procesando JSON: {e}", flush=True)
        return {"status": "error", "message": f"Error procesando JSON: {str(e)}"}
    except Exception as e:
        print(f"❌ Error inesperado: {e}", flush=True)
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": f"Error inesperado: {str(e)}"}