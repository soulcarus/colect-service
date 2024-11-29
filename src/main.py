import sys
import signal
import threading
from typing import List, Dict
from services.collector_service import CollectorService
from factories.collector_factory import OPCUACollectorFactory, MQTTCollectorFactory
from utils.logger import log
from utils.config import load_industry_configs
from utils.mongodb import cleanup_connections

class CollectorApplication:
    def __init__(self):
        self.services: Dict[str, CollectorService] = {}
        self.threads: Dict[str, threading.Thread] = {}
        self.running = False

    def start(self):
        """Start the collector application."""
        self.running = True
        
        # Load industry configurations
        industry_configs = load_industry_configs()
        
        # Create and start threads for each industry
        for industry_id, config in industry_configs.items():
            try:
                # Create appropriate factory based on protocol
                if config['protocol'] == 'opcua':
                    factory = OPCUACollectorFactory(industry_id, config)
                elif config['protocol'] == 'mqtt':
                    factory = MQTTCollectorFactory(industry_id, config)
                else:
                    log.error(f"Unsupported protocol {config['protocol']} for industry {industry_id}")
                    continue

                # Create strategy using factory
                strategy = factory.create_strategy()
                
                # Create service
                service = CollectorService(strategy, industry_id)
                self.services[industry_id] = service
                
                # Create and start thread
                thread = threading.Thread(target=self._run_service, args=(industry_id,))
                thread.daemon = True
                thread.start()
                self.threads[industry_id] = thread
                
                log.info(f"Started collection thread for industry {industry_id}")
            except Exception as e:
                log.error(f"Failed to start thread for industry {industry_id}: {str(e)}")

    def stop(self):
        """Stop the collector application."""
        self.running = False
        for industry_id, service in self.services.items():
            service.stop()
            self.threads[industry_id].join(timeout=5)  # Wait for thread to finish
        log.info("All collection services stopped")
        cleanup_connections()  # Close MongoDB connections

    def _run_service(self, industry_id: str):
        """Run the collection service for a specific industry."""
        service = self.services[industry_id]
        try:
            service.start()
        except Exception as e:
            log.error(f"Error in collection service for industry {industry_id}: {str(e)}")
        finally:
            service.stop()

def signal_handler(signum, frame):
    """Handle shutdown signals."""
    log.info("Shutdown signal received")
    app.stop()
    sys.exit(0)

if __name__ == "__main__":
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Create and start application
    app = CollectorApplication()
    
    try:
        app.start()
        log.info("Collector application started")
        
        # Keep the main thread alive
        while app.running:
            signal.pause()
    
    except Exception as e:
        log.error(f"Application error: {str(e)}")
        app.stop()
        sys.exit(1)