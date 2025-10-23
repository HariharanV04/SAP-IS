#!/usr/bin/env python3
"""Quick test to verify Neo4j connection works on mobile hotspot"""

from neo4j import GraphDatabase
import sys

# Your credentials
URI = "neo4j+s://a09ee8ee.databases.neo4j.io"
USER = "neo4j"
PASSWORD = "X1hAOjlDuAPAMLE3cA7inKb5RQL6JHKeJeV57hKQ_YY"

print("Testing Neo4j connection...")
print("-" * 50)

try:
    # Create driver
    driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))
    
    # Verify connectivity
    driver.verify_connectivity()
    print("✅ Connection successful!")
    
    # Run a simple query
    with driver.session(database="neo4j") as session:
        result = session.run("RETURN 'Hello Neo4j!' as message, timestamp() as ts")
        record = result.single()
        print(f"✅ Query successful: {record['message']}")
        print(f"   Server timestamp: {record['ts']}")
    
    # Check database status
    with driver.session(database="neo4j") as session:
        result = session.run("MATCH (n) RETURN count(n) as count")
        count = result.single()['count']
        print(f"✅ Database has {count} nodes")
    
    driver.close()
    print("\n🎉 ALL TESTS PASSED - Neo4j is working!")
    print("You can now run your full scripts.")
    sys.exit(0)
    
except Exception as e:
    print(f"\n❌ Connection failed: {e}")
    print("\nTroubleshooting:")
    print("1. Make sure you're still on mobile hotspot")
    print("2. Check Neo4j Aura Console: https://console.neo4j.io")
    print("3. Verify database is running (not paused)")
    sys.exit(1)