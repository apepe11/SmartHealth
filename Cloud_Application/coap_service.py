import json
import socket

class CoAPService:
    """Servizio per comunicare con dispositivi IoT via CoAP (Constrained Application Protocol)."""
    
    @staticmethod
    def send_put_request(ip_address, port, resource_path, payload):
        """
        Invia una richiesta PUT CoAP a un dispositivo IoT.
        
        Args:
            ip_address: Indirizzo IPv6 del dispositivo
            port: Porta CoAP del dispositivo
            resource_path: Percorso della risorsa (es: '/sampling')
            payload: Dictionary con i dati da inviare
            
        Returns:
            True se la richiesta è stata inviata con successo, False altrimenti
        """
        try:
            # Qui andrebbe implementato il vero client CoAP
            # Per ora, restituiamo True per indicare successo simulato
            print(f"[CoAP] Invio PUT a {ip_address}:{port}{resource_path}")
            print(f"[CoAP] Payload: {json.dumps(payload)}")
            return True
        except Exception as e:
            print(f"[CoAP Errore] Impossibile contattare il dispositivo: {e}")
            return False

    @staticmethod
    def send_get_request(ip_address, port, resource_path):
        """
        Invia una richiesta GET CoAP a un dispositivo IoT.
        
        Args:
            ip_address: Indirizzo IPv6 del dispositivo
            port: Porta CoAP del dispositivo
            resource_path: Percorso della risorsa (es: '/status')
            
        Returns:
            Risposta del dispositivo o None se fallisce
        """
        try:
            print(f"[CoAP] Invio GET a {ip_address}:{port}{resource_path}")
            return None
        except Exception as e:
            print(f"[CoAP Errore] Impossibile contattare il dispositivo: {e}")
            return None
