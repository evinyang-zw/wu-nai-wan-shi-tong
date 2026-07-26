"""Search tool executor."""
from __future__ import annotations

import random
from typing import Any

from src.schema.types import SearchParams

# Template-based mock results
SEARCH_TEMPLATES = [
    {
        "title": "Python Tutorial for Beginners",
        "url": "https://example.com/python-tutorial",
        "snippet": "Learn Python programming from scratch with this comprehensive tutorial.",
    },
    {
        "title": "Advanced Python Techniques",
        "url": "https://example.com/advanced-python",
        "snippet": "Master advanced Python concepts including decorators, generators, and async programming.",
    },
    {
        "title": "Python Best Practices",
        "url": "https://example.com/python-best-practices",
        "snippet": "Follow these best practices to write clean, maintainable Python code.",
    },
    {
        "title": "Python Libraries Guide",
        "url": "https://example.com/python-libraries",
        "snippet": "Discover the most useful Python libraries for web development, data science, and automation.",
    },
    {
        "title": "Python Performance Optimization",
        "url": "https://example.com/python-performance",
        "snippet": "Tips and techniques to optimize your Python code for better performance.",
    },
]


async def search_executor(params: SearchParams) -> Any:
    """Execute web search queries.
    
    Args:
        params: Search query parameters
        
    Returns:
        Search results list
    """
    num_results = min(params.num_results, len(SEARCH_TEMPLATES))
    
    # Select random templates (in a real implementation, we'd actually search)
    selected_indices = random.sample(range(len(SEARCH_TEMPLATES)), num_results)
    results = [SEARCH_TEMPLATES[i] for i in selected_indices]
    
    return results