# -*- coding: utf-8 -*-
"""Check Chroma collections"""
import sys
sys.path.insert(0, '.')
from app.db.chroma import chroma_client

try:
    faq = chroma_client.get_collection("faq")
    print(f"faq: {faq.count()}")
except Exception as e:
    print(f"faq: error - {e}")

try:
    policies = chroma_client.get_collection("policies")
    print(f"policies: {policies.count()}")
except Exception as e:
    print(f"policies: error - {e}")

try:
    guides = chroma_client.get_collection("guides")
    print(f"guides: {guides.count()}")
except Exception as e:
    print(f"guides: error - {e}")
