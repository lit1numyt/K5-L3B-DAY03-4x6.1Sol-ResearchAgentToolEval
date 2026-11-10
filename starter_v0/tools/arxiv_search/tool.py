"""Explicit folder entry point for the existing arXiv search implementation.

This is an alias of ``papers``, not a new independently implemented tool.
"""
from tools.papers.tool import arxiv_search

__all__ = ["arxiv_search"]
