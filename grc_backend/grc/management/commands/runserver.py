"""
Custom runserver command that suppresses warning messages
"""
import sys
import os
from django.core.management.commands.runserver import Command as RunserverCommand


class FilteredOutput:
    """Filter out warning messages from output"""
    def __init__(self, original):
        self.original = original
        self.buffer = ""
        
    def write(self, message):
        # Skip warning messages completely
        if any(phrase in message for phrase in [
            'WARNING: This is a development server',
            'Do not use it in a production setting',
            'For more information on production servers see',
            'https://docs.djangoproject.com'
        ]):
            return
        self.original.write(message)
        
    def flush(self):
        self.original.flush()


class Command(RunserverCommand):
    """Custom runserver that suppresses development server warnings"""
    
    def handle(self, *args, **options):
        """Override to suppress warning messages"""
        # Replace stdout and stderr
        sys.stdout = FilteredOutput(sys.__stdout__)
        sys.stderr = FilteredOutput(sys.__stderr__)
        
        # Call parent's handle
        super().handle(*args, **options)

