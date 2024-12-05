import traceback
import asyncio
import signal

from services.collector_service import CollectorService
from factories.concrete_apodi_factory import ApodiFactory
from factories.concrete_benatextil_factory import BenatextilFactory
from utils.logger import log
from utils.config import load_industry_configs
from utils.mongodb import cleanup_connections

from collections import defaultdict

class AsyncCollectorApplication:
    def __init__(self):
        self.services = defaultdict(CollectorService)
        self.running = False
        self._stop_event = asyncio.Event()

    async def start(self):
        """Start the collector application."""
        self.running = True
        industry_configs = load_industry_configs()

        tasks = []
        for industry_id, config in industry_configs.items():
            try:
                factory = self._create_factory(industry_id, config)

                if factory is None:
                    log.error(f"Unsupported protocol {config['protocol']} for industry {industry_id}")
                    continue

                strategy = factory.create_strategy()
                self.services[industry_id] = CollectorService(strategy, industry_id)
                tasks.append(self._run_service(industry_id))
                log.info(f"Scheduled collection task for industry {industry_id}")
            
            except Exception as e:
                log.error(f"Failed to start task for industry {industry_id}: {str(e)}")
        
        await asyncio.gather(*tasks, return_exceptions=True)

    def _create_factory(self, industry_id: str, config: dict):
        """Create the appropriate factory based on the protocol."""
        if config['protocol'] == 'ApodiOpcua':
            return ApodiFactory(industry_id, config)
        elif config['protocol'] == 'BenatextilMqtt':
            return BenatextilFactory(industry_id, config)
        else:
            return None

    async def stop(self):
        """Stop the collector application."""
        self.running = False
        for service in self.services.values():
            await service.stop()
        log.info("All collection services stopped")
        cleanup_connections()

    async def _run_service(self, industry_id: str):
        """Run the collection service for a specific industry."""
        service = self.services[industry_id]
        try:
            await service.start()
            await self._stop_event.wait()
        except Exception as e:
            log.error(f"Error in collection service for industry {industry_id}: {str(e)}")
        finally:
            await service.stop()

def shutdown(app: AsyncCollectorApplication, loop: asyncio.AbstractEventLoop):
    """Handle shutdown signals."""
    log.info("Shutdown signal received")
    asyncio.ensure_future(app.stop(), loop=loop)
    app._stop_event.set() 

if __name__ == "__main__":
    app = AsyncCollectorApplication()
    loop = asyncio.get_event_loop()

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda: shutdown(app, loop))

    try:
        log.info("Starting Collector application")
        loop.run_until_complete(app.start())
    except Exception as e:
        log.error(f"Application error: {str(e)}")                
        log.error(traceback.format_exc())
    finally:
        loop.run_until_complete(app.stop())
        loop.close()

