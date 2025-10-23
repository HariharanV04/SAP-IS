"""
Complete Migration Script for all iflow tables
Migrates: iflow_packages, iflow_assets, iflow_components
Order matters due to foreign key dependencies
"""

from supabase import create_client, Client
import os
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv('.env.test')

class IFlowMigration:
    def __init__(self):
        """Initialize connections to both databases"""
        # Source database
        self.source_url = os.getenv("SOURCE_SUPABASE_URL")
        self.source_key = os.getenv("SOURCE_SUPABASE_KEY")
        
        # Destination database
        self.dest_url = os.getenv("DEST_SUPABASE_URL")
        self.dest_key = os.getenv("DEST_SUPABASE_KEY")
        
        if not all([self.source_url, self.source_key, self.dest_url, self.dest_key]):
            raise ValueError("All database credentials must be set")
        
        self.source_client = create_client(self.source_url, self.source_key)
        self.dest_client = create_client(self.dest_url, self.dest_key)
        
        print("✓ Connected to source and destination databases")
        print(f"  Source: {self.source_url}")
        print(f"  Destination: {self.dest_url}")
    
    def export_table(self, table_name, batch_size=100):
        """Export all data from a table in smaller batches"""
        print(f"\n📤 Exporting {table_name}...")
        all_data = []
        offset = 0
        
        try:
            while True:
                try:
                    response = self.source_client.table(table_name)\
                        .select("*")\
                        .range(offset, offset + batch_size - 1)\
                        .execute()
                    
                    batch_data = response.data
                    if not batch_data:
                        break
                    
                    all_data.extend(batch_data)
                    offset += batch_size
                    print(f"  Fetched {len(all_data)} rows so far...")
                    
                    if len(batch_data) < batch_size:
                        break
                        
                except Exception as batch_error:
                    error_msg = str(batch_error)
                    if 'timeout' in error_msg.lower():
                        print(f"  ⚠️  Timeout at offset {offset}, reducing batch size...")
                        # Reduce batch size and retry
                        batch_size = max(10, batch_size // 2)
                        continue
                    else:
                        raise
            
            print(f"✓ Exported {len(all_data)} rows from {table_name}")
            
            # Save to file
            filename = f"{table_name}_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(all_data, f, indent=2, default=str)
            print(f"✓ Saved to {filename}")
            
            return all_data
            
        except Exception as e:
            print(f"✗ Error exporting {table_name}: {str(e)}")
            if all_data:
                # Save partial data
                filename = f"{table_name}_partial_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(all_data, f, indent=2, default=str)
                print(f"⚠️  Saved {len(all_data)} partial rows to {filename}")
            raise
    
    def prepare_vector_data(self, data):
        """Convert vector strings to arrays"""
        print(f"  Preparing {len(data)} rows...")
        prepared_data = []
        
        for row in data:
            prepared_row = row.copy()
            
            # Convert all embedding fields
            embedding_fields = [
                'content_embedding', 
                'description_embedding', 
                'code_embedding',
                'activity_type_embedding'
            ]
            
            for embed_field in embedding_fields:
                if embed_field in prepared_row and isinstance(prepared_row[embed_field], str):
                    try:
                        embed_str = prepared_row[embed_field].strip('[]')
                        prepared_row[embed_field] = [float(x.strip()) for x in embed_str.split(',')]
                    except Exception as e:
                        prepared_row[embed_field] = None
            
            prepared_data.append(prepared_row)
        
        return prepared_data
    
    def import_table(self, table_name, data, batch_size=10):
        """Import data to destination table"""
        print(f"\n📥 Importing {len(data)} rows to {table_name}...")
        
        if not data:
            print("⚠️  No data to import")
            return 0
        
        # Prepare data
        prepared_data = self.prepare_vector_data(data)
        
        imported_count = 0
        failed_count = 0
        
        for i in range(0, len(prepared_data), batch_size):
            batch = prepared_data[i:i + batch_size]
            
            try:
                self.dest_client.table(table_name).insert(batch).execute()
                imported_count += len(batch)
                print(f"  ✓ Imported {imported_count}/{len(data)} rows...")
            except Exception as batch_error:
                # Try individual rows if batch fails
                for row in batch:
                    try:
                        self.dest_client.table(table_name).insert([row]).execute()
                        imported_count += 1
                    except Exception as row_error:
                        failed_count += 1
                        error_msg = str(row_error)[:150]
                        print(f"    ✗ Failed row {row.get('id')}: {error_msg}")
        
        print(f"✓ Import complete: {imported_count} success, {failed_count} failed")
        return imported_count
    
    def migrate_table(self, table_name, batch_size=10):
        """Export and import a single table"""
        print(f"\n{'='*70}")
        print(f"MIGRATING: {table_name.upper()}")
        print(f"{'='*70}")
        
        # Export
        data = self.export_table(table_name)
        
        # Import
        if data:
            imported = self.import_table(table_name, data, batch_size)
            return len(data), imported
        return 0, 0
    
    def verify_table_exists(self, table_name):
        """Check if table exists in destination"""
        try:
            self.dest_client.table(table_name).select('id').limit(1).execute()
            return True
        except Exception:
            return False


def main():
    """Run complete migration"""
    try:
        print("="*70)
        print("COMPLETE IFLOW TABLES MIGRATION")
        print("="*70)
        
        migrator = IFlowMigration()
        
        # Tables to migrate (order matters due to foreign keys)
        tables = [
            'iflow_packages',      # Must be first (parent table)
            'iflow_assets',        # References iflow_packages
            'iflow_components'     # References iflow_packages
        ]
        
        # Verify all tables exist
        print("\n🔹 STEP 1: Verify Tables Exist")
        print("-" * 70)
        
        all_exist = True
        for table in tables:
            exists = migrator.verify_table_exists(table)
            status = "✓ EXISTS" if exists else "✗ MISSING"
            print(f"  {table:25} {status}")
            if not exists:
                all_exist = False
        
        if not all_exist:
            print("\n⚠️  Some tables are missing!")
            print("   Please run create_all_tables.sql in Supabase SQL Editor")
            return
        
        # Migrate each table
        print("\n🔹 STEP 2: Migrate Data")
        print("-" * 70)
        
        results = {}
        for table in tables:
            exported, imported = migrator.migrate_table(table, batch_size=10)
            results[table] = {'exported': exported, 'imported': imported}
        
        # Summary
        print("\n" + "="*70)
        print("MIGRATION SUMMARY")
        print("="*70)
        
        for table, counts in results.items():
            exported = counts['exported']
            imported = counts['imported']
            status = "✓" if exported == imported else "⚠️"
            print(f"{status} {table:25} {exported} exported → {imported} imported")
        
        total_exported = sum(c['exported'] for c in results.values())
        total_imported = sum(c['imported'] for c in results.values())
        
        print("-" * 70)
        print(f"TOTAL: {total_exported} exported → {total_imported} imported")
        
        if total_exported == total_imported:
            print("\n✓ MIGRATION SUCCESSFUL!")
        else:
            print(f"\n⚠️  Some rows failed: {total_exported - total_imported} rows not imported")
        
        print("="*70)
        
    except Exception as e:
        print(f"\n✗ Migration failed: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

