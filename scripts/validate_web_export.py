"""Check the actual embedded GLB channels, including non-flat relief and AO."""
import io
import json
from pathlib import Path
import struct

from PIL import Image, ImageStat

root = Path(__file__).resolve().parents[1]
data = (root / "web/assets/elisabethkirche.glb").read_bytes()
assert data[:4] == b"glTF", "Run git lfs pull to obtain the real GLB"
size = struct.unpack_from("<I", data, 12)[0]
doc = json.loads(data[20:20 + size])
binary = data[28 + size:]


def texture_image(texture):
    image = doc["images"][doc["textures"][texture["index"]]["source"]]
    view = doc["bufferViews"][image["bufferView"]]
    start = view.get("byteOffset", 0)
    return Image.open(io.BytesIO(binary[start:start + view["byteLength"]]))


textured = 0
for material in doc["materials"]:
    assert material.get("alphaMode", "OPAQUE") == "OPAQUE"
    assert "KHR_materials_unlit" not in material.get("extensions", {})
    ao = material["occlusionTexture"]
    assert ao.get("texCoord") == 1, "AO needs its unique atlas, not repeating UVs"
    channel = texture_image(ao).getchannel("R")
    low, high = channel.getextrema()
    assert low < 100 and high > 220, (material["name"], low, high)
    if "baseColorTexture" in material["pbrMetallicRoughness"]:
        normal = material["normalTexture"]
        assert normal.get("texCoord", 0) == 0
        variation = ImageStat.Stat(texture_image(normal).convert("RGB")).stddev
        assert max(variation[:2]) > 1, "Normal map must contain actual relief"
        textured += 1
def accessor(index):
    item = doc["accessors"][index]
    view = doc["bufferViews"][item["bufferView"]]
    code = {5123: "H", 5125: "I", 5126: "f"}[item["componentType"]]
    width = {"SCALAR": 1, "VEC2": 2}[item["type"]]
    fmt = "<" + code * width
    offset = view.get("byteOffset", 0) + item.get("byteOffset", 0)
    stride = view.get("byteStride", struct.calcsize(fmt))
    return [struct.unpack_from(fmt, binary, offset + i * stride) for i in range(item["count"])]


surface_ao = []
for mesh in doc["meshes"]:
    for primitive in mesh["primitives"]:
        assert {"NORMAL", "TEXCOORD_0", "TEXCOORD_1"} <= primitive["attributes"].keys()
        uv = accessor(primitive["attributes"]["TEXCOORD_1"])
        indices = [i[0] for i in accessor(primitive["indices"])]
        img = texture_image(doc["materials"][primitive["material"]]["occlusionTexture"]).convert("RGB")
        for i in range(0, len(indices), 3):
            # glTF UVs already use the image's top-left convention.
            u, v = [sum(uv[j][axis] for j in indices[i:i + 3]) / 3 for axis in range(2)]
            surface_ao.append(img.getpixel((min(img.width - 1, int(u * img.width)), min(img.height - 1, int(v * img.height))))[0])
assert min(surface_ao) < 100 and max(surface_ao) > 220, "No contrast on actual surface texels"
assert textured == 4
assert (root / "web/assets/studio.hdr").stat().st_size > 1000
print("WEB VALIDATION OK: opaque PBR, 4 relief maps, architectural AO on UV1, studio environment")
print(f"AO surface samples: {len(surface_ao)}, range {min(surface_ao)}..{max(surface_ao)}")
