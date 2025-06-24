# -*- coding: utf-8 -*-
from __future__ import annotations
from pathlib import Path
import json

class path():
    def home_directory() -> Path:
        """get home directory of the user."""
        path = Path(f'{Path.home()}/{'FIGs'}')
        path.mkdir(parents=True, exist_ok=True)
    
        return path