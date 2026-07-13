from __future__ import annotations

from dataclasses import dataclass

@dataclass
class HierarchyTracker:
    """Tracks hierarchical depth during linear parsing."""
    current_title: str = ""
    current_part: str = ""
    current_section: str = ""
    current_heading: str = ""
    
    def reset(self) -> None:
        self.current_title = ""
        self.current_part = ""
        self.current_section = ""
        self.current_heading = ""
        
    def get_parent_section(self) -> str:
        """Return the closest structural parent section."""
        return self.current_section or self.current_part or self.current_title
        
    def get_parent_heading(self) -> str:
        """Return the closest textual heading."""
        return self.current_heading or self.current_title
        
    def get_depth_level(self) -> int:
        """Calculate arbitrary depth for metrics."""
        depth = 0
        if self.current_title: depth += 1
        if self.current_part: depth += 1
        if self.current_section: depth += 1
        if self.current_heading: depth += 1
        return max(1, depth)
