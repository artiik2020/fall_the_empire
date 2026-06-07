import json
from dataclasses import asdict, dataclass
from typing import Any, Dict, List


@dataclass
class MapData:
    """Shared map format for editor + game.

    Coordinates are pixel-based for smooth movement (no tile snapping requirement).
    width/height are in *tiles* for convenience (like 139x189), but objects use pixels.
    """

    width: int
    height: int
    tile_size: int = 16

    # Layers / classes the user requested
    units: List[Dict[str, Any]] = None  # юниты/пехота/транспорт (type in dict)
    landscapes: List[Dict[str, Any]] = None  # ландшафт
    barriers: List[Dict[str, Any]] = None  # перграды/преграды
    walls: List[Dict[str, Any]] = None  # стены
    buildings: List[Dict[str, Any]] = None  # здания

    # Optional: global barrier line settings (used for frontline rendering)
    frontline: Dict[str, Any] = None

    def __post_init__(self):
        # Нормализация полей (editor/game должны работать даже с частично заполненной картой)
        self.units = self.units or []
        self.landscapes = self.landscapes or []
        self.barriers = self.barriers or []
        self.walls = self.walls or []
        self.buildings = self.buildings or []

        # back-compat для фронта из примеров (где frontline={enabled,initial,...})
        if self.frontline is None:
            self.frontline = {
                "enabled": True,
                "initial": {"x": 0.0, "y": 0.0},
                "control_radius": 80,
                "points_per_unit": 10,
                "push_threshold_ratio": 2.0,
            }
        else:
            self.frontline.setdefault("enabled", True)
            self.frontline.setdefault("initial", {"x": 0.0, "y": 0.0})
            self.frontline.setdefault("control_radius", 80)
            self.frontline.setdefault("points_per_unit", 10)
            self.frontline.setdefault("push_threshold_ratio", 2.0)


    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "MapData":
        # Поддержка старых/расширенных полей (например version, camera, layers, palette)
        allowed = {
            "width": d.get("width"),
            "height": d.get("height"),
            "tile_size": d.get("tile_size", d.get("tileSize", 16)),
            "units": None,
            "landscapes": None,
            "barriers": None,
            "walls": None,
            "buildings": None,
            "frontline": d.get("frontline"),
        }

        # Если карта была сохранена редактором версии с layers/lists
        layers = d.get("layers") or {}
        allowed["landscapes"] = layers.get("landscape") or layers.get("landscapes") or []
        allowed["barriers"] = layers.get("barriers") or layers.get("barriers") or layers.get("barrier") or []
        allowed["walls"] = layers.get("walls") or []
        allowed["buildings"] = layers.get("buildings") or []

        # units
        allowed["units"] = (
            layers.get("unit_spawns")
            or layers.get("units")
            or d.get("unit_spawns")
            or []
        )

        return MapData(**allowed)



def save_map(map_data: MapData, path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(map_data.to_dict(), f, ensure_ascii=False, indent=2)


def load_map(path: str) -> MapData:
    with open(path, "r", encoding="utf-8") as f:
        return MapData.from_dict(json.load(f))

