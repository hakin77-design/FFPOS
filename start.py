#!/usr/bin/env python3
"""
FFPAS v2.0 - Startup Script
Automated startup with database migration and server launch.
"""
import asyncio
import sys
import subprocess
from pathlib import Path
from utils.logger import setup_logger

logger = setup_logger("startup")


async def check_requirements():
    """Check if all requirements are installed."""
    logger.info("Checking requirements...")
    try:
        import torch
        import fastapi
        import sqlalchemy
        import redis
        logger.info("✓ All core dependencies installed")
        return True
    except ImportError as e:
        logger.error(f"✗ Missing dependency: {e}")
        logger.info("Run: pip install -r requirements.txt")
        return False


async def check_env_file():
    """Check if .env file exists."""
    if not Path(".env").exists():
        logger.warning("✗ .env file not found")
        logger.info("Creating .env from .env.example...")
        try:
            import shutil
            shutil.copy(".env.example", ".env")
            logger.info("✓ .env file created. Please configure it with your API keys.")
            return False
        except Exception as e:
            logger.error(f"Failed to create .env: {e}")
            return False
    logger.info("✓ .env file found")
    return True


async def run_migration():
    """Run database migration."""
    logger.info("=" * 80)
    logger.info("Running database migration...")
    logger.info("=" * 80)
    
    try:
        from database.migrate import run_migration
        await run_migration()
        logger.info("✓ Database migration complete")
        return True
    except Exception as e:
        logger.error(f"✗ Migration failed: {e}")
        logger.info("You can run migration manually: python database/migrate.py")
        return False


async def start_server():
    """Start FastAPI server."""
    logger.info("=" * 80)
    logger.info("Starting FFPAS API Server...")
    logger.info("=" * 80)
    
    try:
        import uvicorn
        from config import settings
        
        logger.info(f"Server: http://{settings.host}:{settings.port}")
        logger.info(f"API Docs: http://{settings.host}:{settings.port}/api/docs")
        logger.info(f"Frontend: http://{settings.host}:{settings.port}")
        logger.info("=" * 80)
        
        uvicorn.run(
            "api.main:app",
            host=settings.host,
            port=settings.port,
            reload=settings.debug,
            log_level=settings.log_level.lower()
        )
        
    except KeyboardInterrupt:
        logger.info("\nShutting down server...")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)


async def main():
    """Main startup sequence."""
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║   ███████╗███████╗██████╗  █████╗ ███████╗              ║
    ║   ██╔════╝██╔════╝██╔══██╗██╔══██╗██╔════╝              ║
    ║   █████╗  █████╗  ██████╔╝███████║███████╗              ║
    ║   ██╔══╝  ██╔══╝  ██╔═══╝ ██╔══██║╚════██║              ║
    ║   ██║     ██║     ██║     ██║  ██║███████║              ║
    ║   ╚═╝     ╚═╝     ╚═╝     ╚═╝  ╚═╝╚══════╝              ║
    ║                                                           ║
    ║   Football Prediction & Analysis System v2.0             ║
    ║   AI-Powered Match Predictions                           ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    # Pre-flight checks
    if not await check_requirements():
        sys.exit(1)
    
    if not await check_env_file():
        logger.warning("Please configure .env file and restart")
        sys.exit(1)
    
    # Ask user about migration
    print("\nOptions:")
    print("1. Run with database migration (first time or after data update)")
    print("2. Skip migration and start server")
    print("3. Exit")
    
    choice = input("\nSelect option (1-3): ").strip()
    
    if choice == "1":
        if not await run_migration():
            logger.warning("Migration had issues, but continuing...")
        await start_server()
    elif choice == "2":
        await start_server()
    else:
        logger.info("Exiting...")
        sys.exit(0)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nGoodbye! 👋")
        sys.exit(0)
