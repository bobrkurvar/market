import asyncio
import logging
from pathlib import Path
from shared import LAYERS_IMAGE_EXTENSION

import aiofiles  # type: ignore

log = logging.getLogger(__name__)


class FileSystemStorage:
    @staticmethod
    async def save(path: Path | str, data: bytes):
        path = Path(path)
        upload_dir = path.parent
        if upload_dir:
            path.parent.mkdir(parents=True, exist_ok=True)
            async with aiofiles.open(path, "xb") as fw:
                await fw.write(data)

    @staticmethod
    async def delete(path: Path | str):
        path = Path(path)
        await asyncio.to_thread(path.unlink, missing_ok=True)


    @staticmethod
    async def get_directory(main_path: str | Path, other_path: str | Path) -> str:
        path_exists = await asyncio.to_thread(Path(main_path).exists)
        if path_exists:
            return Path(main_path).as_posix()
        return Path(other_path).as_posix()


class FileManager:
    def __init__(self, layers: dict | None = None, storage=None, root=None):
        self._root = Path(root) if root else Path("media")
        self._storage = storage if storage is not None else FileSystemStorage()
        self._layers = layers if layers else {}

    def session(self):
        return FileSession(self)

    def resolve_path(self, file_name: str = "", layer: str | None = None) -> Path:
        if layer not in self._layers:
            raise ValueError(f"Unknown layer: {layer}")
        return self._root / self._layers.get(layer, "") / file_name

    async def save(self, image_path: Path | str, img):
        path = Path(image_path).as_posix()
        await self._storage.save(path, img)
        return image_path

    async def save_by_layer(self, file_name: str, img: bytes, layer: str):
        file_name = Path(file_name).with_suffix(LAYERS_IMAGE_EXTENSION).name
        path = self.resolve_path(file_name, layer)
        await self.save(path, img)
        return path

    async def delete_by_layers(self, base_path: str | Path, layers: list[str]) -> int:
        log.debug("deleted by layers: %s", layers)
        base_path = Path(base_path)
        layer_file_name = base_path.with_suffix(LAYERS_IMAGE_EXTENSION).name
        paths = [
            self.resolve_path(layer_file_name, layer)
            for layer in layers
        ]
        paths.append(base_path)
        return await self.delete(paths)

    async def delete(self, paths: list[Path]) -> int:
        deleted = 0
        for path in paths:
            if isinstance(path, str):
                path = Path(path).as_posix()
            await self._storage.delete(path)
            deleted += 1
        return deleted

    def get_layer_path(
        self,
        base_path: str | Path,
        layer: str,
    ) -> str:
        layer_file_name = Path(base_path).with_suffix(LAYERS_IMAGE_EXTENSION).name
        return str(self.resolve_path(file_name=layer_file_name, layer=layer))


class FileSession:
    def __init__(self, file_manager: FileManager):
        self._fm = file_manager
        self._saved_files: list[Path] = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        try:
            if exc:
                await self.rollback()
        finally:
            self._saved_files.clear()

    async def save(self, image_path: Path, img: bytes):
        image_path = await self._fm.save(image_path, img)
        self._saved_files.append(image_path)

    async def save_by_layer(self, file_name: str, img: bytes, layer: str):
        image_path = await self._fm.save_by_layer(file_name, img, layer)
        self._saved_files.append(image_path)

    async def rollback(self):
        log.debug("paths to rollback: %s", self._saved_files)
        await self._fm.delete(self._saved_files)
