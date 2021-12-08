# Simple tomorrow.one PDF Kontoauszug converter
This script converts multiple PDF bank statements from tomorrow.one (generated via the app) to a single csv.
The pdfs are loaded from the `pdfs` subdirectory in bulk.
Tested on python 3.9.7

```bash
pip install -r requirements.txt

python parser.py
```