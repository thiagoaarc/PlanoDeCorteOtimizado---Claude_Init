import json
import os
from datetime import datetime


class VersionControl:
    def __init__(self, base_dir="data"):
        self.base_dir = base_dir
        self.versions_dir = os.path.join(base_dir, "versions")
        self.current_version = 0
        os.makedirs(self.versions_dir, exist_ok=True)

    def save_version(self, data, description=""):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        version_file = os.path.join(
            self.versions_dir,
            f"v{self.current_version + 1}_{timestamp}.json"
        )

        version_data = {
            "version": self.current_version + 1,
            "timestamp": timestamp,
            "description": description,
            "data": data
        }

        with open(version_file, "w", encoding="utf-8") as handle:
            json.dump(version_data, handle, indent=2)

        self.current_version += 1
        return self.current_version

    def load_version(self, version):
        version_files = os.listdir(self.versions_dir)
        target_file = next(
            (name for name in version_files if name.startswith(f"v{version}_")),
            None
        )

        if not target_file:
            raise ValueError(f"Versao {version} nao encontrada")

        with open(os.path.join(self.versions_dir, target_file), "r", encoding="utf-8") as handle:
            return json.load(handle)["data"]

    def list_versions(self):
        versions = []
        for filename in os.listdir(self.versions_dir):
            with open(os.path.join(self.versions_dir, filename), "r", encoding="utf-8") as handle:
                data = json.load(handle)
                versions.append({
                    "version": data["version"],
                    "timestamp": data["timestamp"],
                    "description": data["description"]
                })
        return sorted(versions, key=lambda item: item["version"])
