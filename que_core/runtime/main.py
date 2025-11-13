"""
Main runtime entrypoint for QUE CORE.

Usage:
    python -m que_core.runtime.main
    
Starts the complete QUE CORE runtime with:
- Event bus system
- API server (FastAPI)
- Plugin system
- Context monitoring
- Tool registry
"""
import sys
import asyncio
import logging
import signal
import os
from typing import Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("que_core.runtime")

class QUECoreRuntime:
    """Main QUE CORE runtime manager"""
    
    def __init__(self):
        self.eventbus = None
        self.api_server = None
        self.running = False
        self.shutdown_event = asyncio.Event()
    
    async def start(self, host: str = "localhost", port: int = 8000):
        """Start the complete QUE CORE runtime"""
        logger.info("🚀 QUE CORE Runtime starting...")
        
        try:
            # 1. Start Event Bus
            logger.info("📡 Starting Event Bus...")
            from que_core.runtime.eventbus import start_eventbus, get_eventbus
            await start_eventbus()
            self.eventbus = get_eventbus()
            logger.info("✅ Event Bus started")
            
            # 2. Initialize context monitoring
            logger.info("👁️ Initializing context monitoring...")
            await self._setup_context_monitoring()
            logger.info("✅ Context monitoring initialized")
            
            # 3. Start API Server
            logger.info(f"🌐 Starting API Server on {host}:{port}...")
            await self._start_api_server(host, port)
            logger.info(f"✅ API Server started on http://{host}:{port}")
            
            # 4. Setup signal handlers
            self._setup_signal_handlers()
            
            self.running = True
            logger.info("🎉 QUE CORE Runtime fully operational!")
            logger.info(f"📊 Available tools: {self._get_tool_count()}")
            logger.info(f"🔗 API Documentation: http://{host}:{port}/docs")
            logger.info(f"🔗 WebSocket endpoint: ws://{host}:{port}/ws/tools")
            
            # Publish startup event
            self.eventbus.publish("que_core.runtime.started", {
                "host": host,
                "port": port,
                "tool_count": self._get_tool_count()
            })
            
            # Wait for shutdown signal
            await self.shutdown_event.wait()
            
        except Exception as e:
            logger.error(f"❌ Failed to start QUE CORE Runtime: {e}")
            raise
    
    async def stop(self):
        """Stop the QUE CORE runtime gracefully"""
        if not self.running:
            return
        
        logger.info("🛑 QUE CORE Runtime shutting down...")
        
        try:
            # Publish shutdown event
            if self.eventbus:
                self.eventbus.publish("que_core.runtime.stopping")
            
            # Stop API server
            if self.api_server:
                logger.info("🌐 Stopping API Server...")
                # API server will be stopped by uvicorn signal handling
            
            # Stop event bus
            if self.eventbus:
                logger.info("📡 Stopping Event Bus...")
                from que_core.runtime.eventbus import stop_eventbus
                await stop_eventbus()
            
            self.running = False
            logger.info("✅ QUE CORE Runtime stopped gracefully")
            
        except Exception as e:
            logger.error(f"❌ Error during shutdown: {e}")
        
        finally:
            self.shutdown_event.set()
    
    async def _start_api_server(self, host: str, port: int):
        """Start the FastAPI server"""
        try:
            import uvicorn
            from que_core.api.server import app
            
            # Configure uvicorn
            config = uvicorn.Config(
                app=app,
                host=host,
                port=port,
                log_level="info",
                access_log=True
            )
            
            self.api_server = uvicorn.Server(config)
            
            # Start server in background task
            server_task = asyncio.create_task(self.api_server.serve())
            
            # Wait a moment for server to start
            await asyncio.sleep(1)
            
        except ImportError as e:
            logger.error(f"❌ Failed to import required modules: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ Failed to start API server: {e}")
            raise
    
    async def _setup_context_monitoring(self):
        """Setup context monitoring and periodic tasks"""
        try:
            # Start periodic context updates
            asyncio.create_task(self._context_monitor_loop())
            
        except Exception as e:
            logger.warning(f"⚠️ Context monitoring setup failed: {e}")
    
    async def _context_monitor_loop(self):
        """Periodic context monitoring loop"""
        while self.running:
            try:
                # Publish periodic context updates
                if self.eventbus:
                    self.eventbus.publish("que_core.context.heartbeat", {
                        "timestamp": asyncio.get_event_loop().time(),
                        "runtime_status": "running"
                    })
                
                # Wait 30 seconds before next update
                await asyncio.sleep(30)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.warning(f"⚠️ Context monitor error: {e}")
                await asyncio.sleep(5)  # Short delay on error
    
    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            logger.info(f"📡 Received signal {signum}, initiating shutdown...")
            asyncio.create_task(self.stop())
        
        # Handle common shutdown signals
        if hasattr(signal, 'SIGTERM'):
            signal.signal(signal.SIGTERM, signal_handler)
        if hasattr(signal, 'SIGINT'):
            signal.signal(signal.SIGINT, signal_handler)
    
    def _get_tool_count(self) -> int:
        """Get the number of available tools"""
        try:
            from que_core.api.server import TOOL_REGISTRY
            return len(TOOL_REGISTRY)
        except ImportError:
            return 0
    
    def get_status(self) -> dict:
        """Get runtime status information"""
        status = {
            "running": self.running,
            "tool_count": self._get_tool_count(),
            "eventbus_stats": None
        }
        
        if self.eventbus:
            status["eventbus_stats"] = self.eventbus.get_stats()
        
        return status

# Global runtime instance
_runtime = QUECoreRuntime()

def start(host: str = "localhost", port: int = 8000):
    """Start QUE CORE runtime (sync wrapper)"""
    try:
        asyncio.run(_runtime.start(host, port))
    except KeyboardInterrupt:
        logger.info("🛑 Interrupted by user")
    except Exception as e:
        logger.error(f"❌ Runtime error: {e}")
        sys.exit(1)

async def start_async(host: str = "localhost", port: int = 8000):
    """Start QUE CORE runtime (async)"""
    await _runtime.start(host, port)

async def stop_async():
    """Stop QUE CORE runtime (async)"""
    await _runtime.stop()

def get_runtime() -> QUECoreRuntime:
    """Get the global runtime instance"""
    return _runtime

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="QUE CORE Runtime")
    parser.add_argument("--host", default="localhost", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    
    args = parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    logger.info("🎯 Starting QUE CORE Runtime from command line")
    start(args.host, args.port)
