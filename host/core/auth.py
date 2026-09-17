import secrets
import random
import time
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

PAIRING_CODE_VALID_FOR = 300 # 5 minutes

class AuthManager:
    def __init__(self):
        self.pairing_code = None
        self.pairing_code_expiry = 0
        self.pending_requests = {} # client_id -> dict
        self.rejected_requests = {} # client_id -> dict
        self.approved_clients = {} # client_id -> dict
        self.tokens = {} # token -> client_id
    
    def generate_pairing_code(self):
        self.pairing_code = f'{random.randint(100000, 999999)}'
        self.pairing_code_expiry = time.time() + PAIRING_CODE_VALID_FOR
        return self.pairing_code
    
    def get_pairing_code(self):
        if not self.pairing_code or time.time() > self.pairing_code_expiry:
            self.generate_pairing_code()
        return self.pairing_code

    def receive_pairing_request(self, pairing_code: str, client_info: dict):
        if not self.pairing_code or time.time() > self.pairing_code_expiry:
            raise HTTPException(status_code=400, detail='Pairing code expired or invalid')
        if pairing_code != self.pairing_code:
            raise HTTPException(status_code=400, detail='Invalid pairing code')
        
        client_id = client_info.get('client_id')
        if not client_id:
            raise HTTPException(status_code=400, detail='Missing client_id')
            
        self.pending_requests[client_id] = {
            'info': client_info,
            'status': 'pending',
            'timestamp': time.time()
        }
        return {'status': 'pending'}
        
    def approve_client(self, client_id: str):
        if client_id not in self.pending_requests:
            raise HTTPException(status_code=404, detail='Pending request not found')
            
        token = secrets.token_urlsafe(32)
        client_data = self.pending_requests.pop(client_id)
        client_data['status'] = 'approved'
        client_data['token'] = token
        
        self.approved_clients[client_id] = client_data
        self.tokens[token] = client_id
        
        self.pairing_code = None # Invalidate
        return {'status': 'approved'}
        
    def reject_client(self, client_id: str):
        if client_id in self.pending_requests:
            client_data = self.pending_requests.pop(client_id)
            client_data['status'] = 'rejected'
            self.rejected_requests[client_id] = client_data
            return {'status': 'rejected'}
        raise HTTPException(status_code=404, detail='Pending request not found')
        
    def revoke_client(self, client_id: str):
        if client_id in self.approved_clients:
            client_data = self.approved_clients.pop(client_id)
            token = client_data.get('token')
            if token in self.tokens:
                del self.tokens[token]
            return {'status': 'revoked'}
        raise HTTPException(status_code=404, detail='Client not found')
        
    def verify_token(self, token: str):
        client_id = self.tokens.get(token)
        if not client_id:
            raise HTTPException(status_code=401, detail='Invalid token')
        if client_id not in self.approved_clients:
            raise HTTPException(status_code=401, detail='Client revoked')
        return client_id

auth_manager = AuthManager()
security = HTTPBearer()

def get_current_client(credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    client_id = auth_manager.verify_token(token)
    return client_id

