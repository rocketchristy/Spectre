"""
================================================================================
File: logger.py
Description: Centralized logging configuration for the Spectre application
Author: Rocket Software NextGen Academy
Date: 2026
================================================================================
This module configures the application logger with both console and file output.
All log messages are written to both stdout and 'spectre.log' file for debugging
and audit purposes.
================================================================================
"""

import logging

# Create logger instance
logger = logging.getLogger("spectre")
logger.setLevel(logging.INFO)

# Console handler - outputs to terminal
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

# File handler - outputs to spectre.log file
fh = logging.FileHandler("spectre.log")
fh.setLevel(logging.INFO)

# Formatter - defines log message format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
fh.setFormatter(formatter)

# Add handlers if not already added (prevents duplicate logs)
if not logger.hasHandlers():
    logger.addHandler(ch)
    logger.addHandler(fh)