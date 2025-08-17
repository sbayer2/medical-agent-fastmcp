#!/usr/bin/env python3
"""Test the Medical Agent API"""

import httpx
import asyncio
import json

async def test_api():
    """Test the medical agent API"""
    
    # API base URL
    base_url = "http://localhost:8000"
    
    # First, get the test customer
    async with httpx.AsyncClient() as client:
        print("1. Getting test customer...")
        response = await client.get(f"{base_url}/api/test-customer")
        customer = response.json()
        print(f"   Customer ID: {customer['customer_id']}")
        print(f"   Name: {customer['name']}")
        
        # Test with a file
        print("\n2. Analyzing SOAP note file...")
        analysis_request = {
            "customer_id": customer['customer_id'],
            "type": "basic",
            "file_path": "/app/medical_files_data/sample_soap_note.txt"
        }
        
        response = await client.post(
            f"{base_url}/api/analyze",
            json=analysis_request
        )
        result = response.json()
        print(f"   Status: {result['status']}")
        
        if result.get('job_id'):
            # If background processing, check job status
            print(f"   Job ID: {result['job_id']}")
            await asyncio.sleep(2)  # Wait for processing
            
            response = await client.get(f"{base_url}/api/job/{result['job_id']}")
            result = response.json()
        
        # Display results
        print("\n3. Analysis Results:")
        print(f"   Status: {result.get('status')}")
        print(f"   Billed: {result.get('billed')}")
        print(f"   Tier: {result.get('tier')}")
        print(f"   Price: ${result.get('price')}")
        print(f"   Customer ID: {result.get('customer_id')}")
        
        if result.get('analysis'):
            print("\n4. Medical Analysis:")
            print("-" * 70)
            print(result['analysis'])
            print("-" * 70)
        
        if result.get('error'):
            print(f"\n   Error: {result['error']}")
        
        # Test with direct text
        print("\n5. Testing with direct text query...")
        analysis_request = {
            "customer_id": customer['customer_id'],
            "type": "comprehensive",
            "query": "Patient presents with headache, fever 101.5F, BP 130/85"
        }
        
        response = await client.post(
            f"{base_url}/api/analyze",
            json=analysis_request
        )
        result = response.json()
        print(f"   Status: {result['status']}")
        print(f"   Tier: {result.get('tier')}")
        print(f"   Price: ${result.get('price')}")

if __name__ == "__main__":
    print("Testing Medical Agent API...")
    asyncio.run(test_api())
