"""
WebSocket API Server for iOS App
Real-time alerts và monitoring
"""
import asyncio
import websockets
import json
from typing import Set, Dict
import threading
import time


class WebSocketServer:
    """
    WebSocket server for iOS app integration
    """
    
    def __init__(self, config: dict):
        self.config = config
        api_config = config.get('ios_api', {})
        
        self.enabled = api_config.get('enabled', False)
        self.host = api_config.get('host', '0.0.0.0')
        self.port = api_config.get('port', 8080)
        self.alert_cooldown = api_config.get('alert_cooldown', 10)
        
        # Connected clients
        self.clients: Set[websockets.WebSocketServerProtocol] = set()
        
        # Alert history (for cooldown)
        self.last_alert_time = {}  # {track_id: timestamp}
        
        # Server thread
        self.server_thread = None
        self.running = False
    
    def start(self):
        """Start WebSocket server in background thread"""
        if not self.enabled:
            return
        
        self.running = True
        self.server_thread = threading.Thread(target=self._run_server, daemon=True)
        self.server_thread.start()
        
        print(f"[API] WebSocket server starting on {self.host}:{self.port}")
    
    def stop(self):
        """Stop WebSocket server"""
        self.running = False
    
    def _run_server(self):
        """Run asyncio event loop in thread"""
        asyncio.run(self._async_server())
    
    async def _async_server(self):
        """Async server main"""
        async with websockets.serve(self._handle_client, self.host, self.port):
            while self.running:
                await asyncio.sleep(0.1)
    
    async def _handle_client(
        self, 
        websocket: websockets.WebSocketServerProtocol, 
        path: str
    ):
        """Handle new client connection"""
        # Register client
        self.clients.add(websocket)
        print(f"[API] Client connected: {websocket.remote_address}")
        
        try:
            # Send welcome message
            await websocket.send(json.dumps({
                'type': 'CONNECTED',
                'message': 'Fall Detection API',
                'timestamp': time.time()
            }))
            
            # Keep connection alive
            async for message in websocket:
                # Handle client messages
                try:
                    data = json.loads(message)
                    await self._handle_message(websocket, data)
                except json.JSONDecodeError:
                    await websocket.send(json.dumps({
                        'type': 'ERROR',
                        'message': 'Invalid JSON'
                    }))
        
        except websockets.exceptions.ConnectionClosed:
            pass
        
        finally:
            # Unregister client
            self.clients.remove(websocket)
            print(f"[API] Client disconnected: {websocket.remote_address}")
    
    async def _handle_message(
        self, 
        websocket: websockets.WebSocketServerProtocol,
        data: dict
    ):
        """Handle message from client"""
        msg_type = data.get('type')
        
        if msg_type == 'PING':
            await websocket.send(json.dumps({
                'type': 'PONG',
                'timestamp': time.time()
            }))
        
        elif msg_type == 'ACK':
            # Client acknowledged alert
            track_id = data.get('track_id')
            print(f"[API] Alert acknowledged for track {track_id}")
        
        elif msg_type == 'CANCEL':
            # User cancelled alert ("I'm OK" button)
            track_id = data.get('track_id')
            print(f"[API] Alert cancelled by user for track {track_id}")
            # TODO: Update state machine to cancel alarm
    
    def send_alert(
        self,
        track_id: int,
        risk_score: float,
        state: str,
        snapshot_path: str = None,
        clip_path: str = None,
        features: dict = None
    ):
        """
        Send alert to all connected clients
        """
        if not self.enabled or len(self.clients) == 0:
            return
        
        # Check cooldown
        current_time = time.time()
        last_time = self.last_alert_time.get(track_id, 0)
        
        if current_time - last_time < self.alert_cooldown:
            return  # Too soon
        
        # Update last alert time
        self.last_alert_time[track_id] = current_time
        
        # Create alert message
        alert = {
            'type': 'ALARM',
            'track_id': track_id,
            'risk_score': risk_score,
            'state': state,
            'timestamp': current_time,
            'snapshot': snapshot_path,
            'clip': clip_path,
            'features': features
        }
        
        # Send to all clients
        asyncio.run(self._broadcast(alert))
        
        print(f"[API] Alert sent to {len(self.clients)} clients (track {track_id})")
    
    def send_warning(
        self,
        track_id: int,
        risk_score: float,
        state: str
    ):
        """Send warning (lower priority than alarm)"""
        if not self.enabled or len(self.clients) == 0:
            return
        
        warning = {
            'type': 'WARNING',
            'track_id': track_id,
            'risk_score': risk_score,
            'state': state,
            'timestamp': time.time()
        }
        
        asyncio.run(self._broadcast(warning))
    
    def send_status_update(self, status: dict):
        """Send system status update"""
        if not self.enabled or len(self.clients) == 0:
            return
        
        message = {
            'type': 'STATUS',
            'data': status,
            'timestamp': time.time()
        }
        
        asyncio.run(self._broadcast(message))
    
    async def _broadcast(self, message: dict):
        """Broadcast message to all clients"""
        if not self.clients:
            return
        
        message_str = json.dumps(message)
        
        # Send to all clients
        disconnected = set()
        for client in self.clients:
            try:
                await client.send(message_str)
            except:
                disconnected.add(client)
        
        # Remove disconnected clients
        self.clients -= disconnected


class AlertHandler:
    """
    Manage alerts and notifications
    """
    
    def __init__(self, config: dict, websocket_server: WebSocketServer):
        self.config = config
        self.websocket_server = websocket_server
        
        # Alert history
        self.alert_history = []
    
    def trigger_alarm(
        self,
        track_id: int,
        risk_score: float,
        state: str,
        snapshot_path: str = None,
        clip_path: str = None,
        features: dict = None
    ):
        """Trigger alarm alert"""
        # Log to history
        alert = {
            'track_id': track_id,
            'risk_score': risk_score,
            'state': state,
            'timestamp': time.time(),
            'type': 'ALARM'
        }
        self.alert_history.append(alert)
        
        # Send to iOS app
        self.websocket_server.send_alert(
            track_id=track_id,
            risk_score=risk_score,
            state=state,
            snapshot_path=snapshot_path,
            clip_path=clip_path,
            features=features
        )
        
        print(f"[ALERT] ALARM triggered for track {track_id} (risk: {risk_score:.1f})")
    
    def trigger_warning(
        self,
        track_id: int,
        risk_score: float,
        state: str
    ):
        """Trigger warning alert"""
        # Log to history
        alert = {
            'track_id': track_id,
            'risk_score': risk_score,
            'state': state,
            'timestamp': time.time(),
            'type': 'WARNING'
        }
        self.alert_history.append(alert)
        
        # Send to iOS app
        self.websocket_server.send_warning(
            track_id=track_id,
            risk_score=risk_score,
            state=state
        )
        
        print(f"[ALERT] WARNING for track {track_id} (risk: {risk_score:.1f})")
    
    def get_recent_alerts(self, count: int = 10) -> list:
        """Get recent alerts"""
        return self.alert_history[-count:]
