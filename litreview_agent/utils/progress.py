"""
Progress tracking utilities for LitReviewAgent
"""

import sys
import time
from typing import Optional, List, Dict, Any, Callable
from contextlib import contextmanager

class ProgressTracker:
    """Tracks progress of a multi-step process with terminal output"""
    
    def __init__(self, total_steps: int, description: str = "", verbose: bool = True):
        """
        Initialize a progress tracker
        
        Args:
            total_steps: Total number of steps in the process
            description: Description of the process
            verbose: Whether to print progress messages
        """
        self.total_steps = total_steps
        self.current_step = 0
        self.description = description
        self.start_time = time.time()
        self.step_times: List[float] = []
        self.messages: List[str] = []
        self.verbose = verbose
        
        if verbose and description:
            print(f"\n{description}")
            print(f"Step 0/{total_steps}: Starting...")
    
    def next_step(self, message: str) -> None:
        """
        Move to the next step
        
        Args:
            message: Message describing the current step
        """
        # Record time for the previous step
        step_time = time.time()
        if self.current_step > 0:
            self.step_times.append(step_time - self.start_time - sum(self.step_times))
            
        self.current_step += 1
        self.messages.append(message)
        
        # If this is the last step, use "Completed" instead of step number
        if self.current_step == self.total_steps:
            status = "Completed"
        else:
            status = f"Step {self.current_step}/{self.total_steps}"
            
        # Add elapsed time
        elapsed = time.time() - self.start_time
        time_str = f"[{format_time(elapsed)}]"
        
        if self.verbose:
            print(f"{status}: {message} {time_str}")
    
    def add_message(self, message: str) -> None:
        """
        Add a message without advancing to the next step
        
        Args:
            message: Message to add
        """
        self.messages.append(message)
        if self.verbose:
            print(f"  - {message}")
    
    def summary(self) -> Dict[str, Any]:
        """
        Get a summary of the progress
        
        Returns:
            Dictionary with progress summary
        """
        elapsed = time.time() - self.start_time
        return {
            "total_steps": self.total_steps,
            "completed_steps": self.current_step,
            "elapsed_time": elapsed,
            "messages": self.messages,
            "step_times": self.step_times
        }
    
    def print_summary(self) -> None:
        """Print a summary of the progress"""
        if not self.verbose:
            return
            
        elapsed = time.time() - self.start_time
        print(f"\n{self.description} completed in {format_time(elapsed)}")
        print(f"Steps completed: {self.current_step}/{self.total_steps}")
        
        if len(self.step_times) > 0:
            print("\nTime per step:")
            for i, step_time in enumerate(self.step_times):
                print(f"  Step {i+1}: {format_time(step_time)}")

def format_time(seconds: float) -> str:
    """
    Format time in seconds to a human-readable string
    
    Args:
        seconds: Time in seconds
        
    Returns:
        Formatted time string
    """
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds // 60
        seconds %= 60
        return f"{int(minutes)}m {int(seconds)}s"
    else:
        hours = seconds // 3600
        seconds %= 3600
        minutes = seconds // 60
        seconds %= 60
        return f"{int(hours)}h {int(minutes)}m {int(seconds)}s"

def progress_bar(current: int, total: int, prefix: str = '', suffix: str = '', 
                 length: int = 50, fill: str = '█', print_end: str = '\r') -> None:
    """
    Display a progress bar in the terminal
    
    Args:
        current: Current progress value
        total: Total progress value
        prefix: Prefix string
        suffix: Suffix string
        length: Bar length
        fill: Bar fill character
        print_end: End character for print
    """
    percent = f"{100 * (current / float(total)):.1f}"
    filled_length = int(length * current // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    sys.stdout.write(f'\r{prefix} |{bar}| {percent}% {suffix}')
    sys.stdout.flush()
    
    # Print a new line when complete
    if current == total:
        print()

@contextmanager
def progress_context(description: str, verbose: bool = True) -> None:
    """
    Context manager for operations that need to show progress
    
    Args:
        description: Description of the operation
        verbose: Whether to print progress messages
    """
    if verbose:
        print(f"\n{description}...")
    start_time = time.time()
    
    try:
        yield
    finally:
        elapsed = time.time() - start_time
        if verbose:
            print(f"{description} completed in {format_time(elapsed)}") 