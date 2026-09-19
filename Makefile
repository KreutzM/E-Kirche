.PHONY: setup validate fetch fetch-priority1 contacts scene

setup:
	python -m pip install -r requirements.txt

validate:
	python scripts/validate_dataset.py

fetch:
	python scripts/fetch_assets.py --max-width 2500

fetch-priority1:
	python scripts/fetch_assets.py --priority 1 --max-width 2500

contacts:
	python scripts/make_contact_sheets.py

scene:
	blender --background --python scripts/blender/00_scene_setup.py
