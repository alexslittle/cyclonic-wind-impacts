# !/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@File    :   get_data.py
@Date    :   2022-06-08
@Author  :   Alex Little
@Desc    :   Downloads all data required to compute wind footprints from a Backblaze bucket.
"""

# --------------------------------------------------------------------------------

# Built-in modules
import sys
import time

# conda-installed modules
from b2sdk.v2 import B2Api, InMemoryAccountInfo, parse_sync_folder, Synchronizer, SyncReport

# App key credentials (read-only access)
application_key_id = "00405ff7eb09bd3000000000c"
application_key = "K004zX1DjyHw2eoq6swRD43J3qTjrjs"
b2_api = B2Api(InMemoryAccountInfo())
b2_api.authorize_account(
    "production", application_key_id, application_key
)

# Cloud to local data transfer
source = "b2://europe-cyclones/"
destination = "./data"

# Sync data from source to destination
synchronizer = Synchronizer(
    max_workers=10,
    dry_run=False,
)
with SyncReport(sys.stdout, no_progress=False) as reporter:
    synchronizer.sync_folders(
        source_folder=parse_sync_folder(source, b2_api),
        dest_folder=parse_sync_folder(destination, b2_api),
        now_millis=int(round(time.time() * 1000)),
        reporter=reporter,
    )
