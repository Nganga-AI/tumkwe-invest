"""
Unified data collection script that uses the collector manager to gather financial data.
"""
import os
import sys
import json
import pandas as pd
import argparse
from datetime import datetime
from tqdm import tqdm
import logging

from tumkwe_invest.datacollection.collector_manager import CollectorManager
from tumkwe_invest.datacollection.config import CACHE_DIRECTORY


def setup_logging():
    """Set up logging for the script."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(os.path.join(CACHE_DIRECTORY, "unified_collection.log")),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger("unified_collector")


def collect_data(symbols, scheduler=False, validate_only=False):
    """
    Collect financial data for the given symbols.
    
    Args:
        symbols: List of stock symbols to collect data for
        scheduler: If True, start the background scheduler
        validate_only: If True, only validate existing data without collection
    """
    logger = setup_logging()
    logger.info(f"Starting data collection for {len(symbols)} symbols")
    
    # Initialize collector manager
    manager = CollectorManager()
    
    # Add symbols for monitoring
    for symbol in tqdm(symbols, desc="Adding companies"):
        manager.add_company(symbol)
    
    if validate_only:
        logger.info("Validation-only mode: skipping collection")
        validation_summary = manager.get_validation_summary()
        print("\nValidation Summary:")
        print(json.dumps(validation_summary, indent=4))
        return
    
    if scheduler:
        # Start background collection thread
        logger.info("Starting background collection scheduler")
        manager.start_collection_thread()
        
        try:
            print("Press Ctrl+C to stop the collection scheduler")
            while True:
                # Just keep the main thread alive
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Stopping collection scheduler")
            manager.stop_collection_thread()
    else:
        # Perform immediate collection for all symbols
        logger.info("Performing immediate data collection")
        
        for symbol in tqdm(symbols, desc="Collecting data"):
            manager.collect_all_data_for_symbol(symbol)
        
        # Get validation summary
        validation_summary = manager.get_validation_summary()
        print("\nValidation Summary:")
        print(json.dumps(validation_summary, indent=4))


def main():
    """Parse command line arguments and run the collector."""
    parser = argparse.ArgumentParser(description='Collect financial data for companies')
    
    parser.add_argument('symbols', nargs='*', default=['AAPL'], 
                        help='Stock ticker symbols (default: AAPL)')
    parser.add_argument('--file', '-f', type=str,
                        help='File with list of symbols, one per line')
    parser.add_argument('--scheduler', '-s', action='store_true',
                        help='Run as a background scheduler')
    parser.add_argument('--validate', '-v', action='store_true',
                        help='Only validate existing data, no collection')
    
    args = parser.parse_args()
    
    symbols = args.symbols
    
    # Load symbols from file if specified
    if args.file and os.path.exists(args.file):
        with open(args.file, 'r') as f:
            file_symbols = [line.strip() for line in f if line.strip()]
            symbols.extend(file_symbols)
    
    # Remove duplicates and ensure uppercase
    symbols = list(set([s.upper() for s in symbols]))
    
    if not symbols:
        print("No symbols provided. Using default: AAPL")
        symbols = ['AAPL']
    
    collect_data(symbols, scheduler=args.scheduler, validate_only=args.validate)


if __name__ == "__main__":
    main()
