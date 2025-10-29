"""
Database configuration and utilities for the MuleSoft Documentation Generator.
"""

import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from models import db, Job, Document, IFlowMatch, IFlowGeneration, UserSession, SystemMetrics
from datetime import datetime
import json

# Initialize Flask-Migrate
migrate = Migrate()

def get_database_url():
    """
    Get the database URL from environment variables.
    Supports both GCP Cloud SQL and local PostgreSQL.
    """
    # Check for GCP Cloud SQL connection
    if os.getenv('CLOUD_SQL_CONNECTION_NAME'):
        # GCP Cloud SQL with Unix socket
        db_user = os.getenv('DB_USER', 'postgres')
        db_password = os.getenv('DB_PASSWORD')
        db_name = os.getenv('DB_NAME', 'mulesoft_docs')
        connection_name = os.getenv('CLOUD_SQL_CONNECTION_NAME')
        
        if not db_password:
            raise ValueError("DB_PASSWORD environment variable is required for Cloud SQL")
        
        # Unix socket path for Cloud SQL
        unix_socket_path = f"/cloudsql/{connection_name}"
        database_url = f"postgresql://{db_user}:{db_password}@/{db_name}?host={unix_socket_path}"
        
        logging.info(f"Using GCP Cloud SQL connection: {connection_name}")
        return database_url
    
    # Check for direct PostgreSQL connection
    elif os.getenv('DATABASE_URL'):
        database_url = os.getenv('DATABASE_URL')
        logging.info("Using DATABASE_URL environment variable")
        return database_url
    
    # Build from individual components
    else:
        db_host = os.getenv('DB_HOST', 'localhost')
        db_port = os.getenv('DB_PORT', '5432')
        db_user = os.getenv('DB_USER', 'postgres')
        db_password = os.getenv('DB_PASSWORD', 'password')
        db_name = os.getenv('DB_NAME', 'mulesoft_docs')
        
        database_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        logging.info(f"Using PostgreSQL connection: {db_host}:{db_port}/{db_name}")
        return database_url

def init_database(app: Flask):
    """
    Initialize the database with the Flask app.
    """
    try:
        # Get database URL
        database_url = get_database_url()
        
        # Configure SQLAlchemy
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            'pool_pre_ping': True,
            'pool_recycle': 300,
            'connect_args': {
                'connect_timeout': 10,
                'application_name': 'mulesoft_docs_generator'
            }
        }
        
        # Initialize extensions
        db.init_app(app)
        migrate.init_app(app, db)
        
        logging.info("Database configuration initialized successfully")
        return True
        
    except Exception as e:
        logging.error(f"Failed to initialize database: {str(e)}")
        return False

def create_tables(app: Flask):
    """
    Create all database tables.
    """
    try:
        with app.app_context():
            db.create_all()
            logging.info("Database tables created successfully")
            return True
    except Exception as e:
        logging.error(f"Failed to create database tables: {str(e)}")
        return False

def test_connection(app: Flask):
    """
    Test the database connection.
    """
    try:
        with app.app_context():
            # Try to execute a simple query
            result = db.session.execute(db.text('SELECT 1'))
            result.fetchone()
            logging.info("Database connection test successful")
            return True
    except Exception as e:
        logging.error(f"Database connection test failed: {str(e)}")
        return False

class DatabaseManager:
    """
    Database manager class for handling job persistence and retrieval.
    """
    
    @staticmethod
    def create_job(job_id, filename, enhance_with_llm=False, llm_service=None):
        """
        Create a new job in the database.
        """
        try:
            job = Job(
                id=job_id,
                filename=filename,
                status='pending',
                enhance_with_llm=enhance_with_llm,
                llm_service=llm_service
            )
            db.session.add(job)
            db.session.commit()
            logging.info(f"Created job {job_id} in database")
            return job
        except Exception as e:
            db.session.rollback()
            logging.error(f"Failed to create job {job_id}: {str(e)}")
            raise
    
    @staticmethod
    def get_job(job_id):
        """
        Get a job by ID.
        """
        try:
            job = Job.query.get(job_id)
            return job
        except Exception as e:
            logging.error(f"Failed to get job {job_id}: {str(e)}")
            return None
    
    @staticmethod
    def update_job(job_id, **kwargs):
        """
        Update a job with new data.
        """
        try:
            job = Job.query.get(job_id)
            if job:
                job.update_status(**kwargs)
                logging.debug(f"Updated job {job_id}")
                return job
            else:
                logging.warning(f"Job {job_id} not found for update")
                return None
        except Exception as e:
            db.session.rollback()
            logging.error(f"Failed to update job {job_id}: {str(e)}")
            raise
    
    @staticmethod
    def get_all_jobs(limit=100, offset=0):
        """
        Get all jobs with pagination.
        """
        try:
            jobs = Job.query.order_by(Job.created_at.desc()).limit(limit).offset(offset).all()
            return jobs
        except Exception as e:
            logging.error(f"Failed to get jobs: {str(e)}")
            return []
    
    @staticmethod
    def create_document(job_id, document_type, filename, file_path, content=None, file_size=None):
        """
        Create a document record.
        """
        try:
            document = Document(
                job_id=job_id,
                document_type=document_type,
                filename=filename,
                file_path=file_path,
                content=content,
                file_size=file_size
            )
            db.session.add(document)
            db.session.commit()
            logging.info(f"Created document {filename} for job {job_id}")
            return document
        except Exception as e:
            db.session.rollback()
            logging.error(f"Failed to create document for job {job_id}: {str(e)}")
            raise
    
    @staticmethod
    def get_job_documents(job_id):
        """
        Get all documents for a job.
        """
        try:
            documents = Document.query.filter_by(job_id=job_id).all()
            return documents
        except Exception as e:
            logging.error(f"Failed to get documents for job {job_id}: {str(e)}")
            return []
    
    @staticmethod
    def create_iflow_match(job_id):
        """
        Create an iFlow match record.
        """
        try:
            iflow_match = IFlowMatch(job_id=job_id)
            db.session.add(iflow_match)
            db.session.commit()
            logging.info(f"Created iFlow match for job {job_id}")
            return iflow_match
        except Exception as e:
            db.session.rollback()
            logging.error(f"Failed to create iFlow match for job {job_id}: {str(e)}")
            raise
    
    @staticmethod
    def update_iflow_match(job_id, **kwargs):
        """
        Update an iFlow match record.
        """
        try:
            iflow_match = IFlowMatch.query.filter_by(job_id=job_id).first()
            if iflow_match:
                for key, value in kwargs.items():
                    if hasattr(iflow_match, key):
                        setattr(iflow_match, key, value)
                
                if kwargs.get('status') in ['completed', 'failed']:
                    iflow_match.completed_at = datetime.utcnow()
                
                db.session.commit()
                logging.info(f"Updated iFlow match for job {job_id}")
                return iflow_match
            else:
                logging.warning(f"iFlow match not found for job {job_id}")
                return None
        except Exception as e:
            db.session.rollback()
            logging.error(f"Failed to update iFlow match for job {job_id}: {str(e)}")
            raise
    
    @staticmethod
    def create_iflow_generation(generation_id, original_job_id, markdown_content=None):
        """
        Create an iFlow generation record.
        """
        try:
            generation = IFlowGeneration(
                id=generation_id,
                original_job_id=original_job_id,
                markdown_content=markdown_content
            )
            db.session.add(generation)
            db.session.commit()
            logging.info(f"Created iFlow generation {generation_id}")
            return generation
        except Exception as e:
            db.session.rollback()
            logging.error(f"Failed to create iFlow generation {generation_id}: {str(e)}")
            raise
    
    @staticmethod
    def get_iflow_generation(generation_id):
        """
        Get an iFlow generation by ID.
        """
        try:
            generation = IFlowGeneration.query.get(generation_id)
            return generation
        except Exception as e:
            logging.error(f"Failed to get iFlow generation {generation_id}: {str(e)}")
            return None
    
    @staticmethod
    def record_metric(metric_name, metric_value, metric_data=None):
        """
        Record a system metric.
        """
        try:
            metric = SystemMetrics(
                metric_name=metric_name,
                metric_value=metric_value,
                metric_data=metric_data
            )
            db.session.add(metric)
            db.session.commit()
            logging.debug(f"Recorded metric: {metric_name} = {metric_value}")
        except Exception as e:
            db.session.rollback()
            logging.error(f"Failed to record metric {metric_name}: {str(e)}")

    @staticmethod
    def delete_job(job_id):
        """
        Delete a job and all its associated records.
        """
        try:
            # Delete associated documents
            Document.query.filter_by(job_id=job_id).delete()

            # Delete associated iFlow matches
            IFlowMatch.query.filter_by(job_id=job_id).delete()

            # Delete associated iFlow generations
            IFlowGeneration.query.filter_by(job_id=job_id).delete()

            # Delete the job itself
            job = Job.query.get(job_id)
            if job:
                db.session.delete(job)

            db.session.commit()
            logging.info(f"Successfully deleted job {job_id} and all associated records")
            return True

        except Exception as e:
            db.session.rollback()
            logging.error(f"Failed to delete job {job_id}: {str(e)}")
            raise

def migrate_existing_jobs(app: Flask, jobs_file_path: str):
    """
    Migrate existing jobs from JSON file to database.
    """
    if not os.path.exists(jobs_file_path):
        logging.info("No existing jobs file found, skipping migration")
        return
    
    try:
        with app.app_context():
            with open(jobs_file_path, 'r') as f:
                jobs_data = json.load(f)
            
            migrated_count = 0
            for job_id, job_data in jobs_data.items():
                # Check if job already exists
                existing_job = Job.query.get(job_id)
                if existing_job:
                    continue
                
                # Create new job from existing data
                job = Job(
                    id=job_id,
                    filename=job_data.get('filename', 'unknown'),
                    status=job_data.get('status', 'unknown'),
                    processing_step=job_data.get('processing_step'),
                    processing_message=job_data.get('processing_message'),
                    error_message=job_data.get('error'),
                    file_info=job_data.get('file_info'),
                    parsed_details=job_data.get('parsed_details'),
                    enhance_with_llm=job_data.get('enhance', False),
                    upload_path=job_data.get('upload_path'),
                    results_path=job_data.get('results_path')
                )
                
                # Set timestamps if available
                if 'timestamp' in job_data:
                    try:
                        job.created_at = datetime.fromisoformat(job_data['timestamp'])
                    except:
                        pass
                
                db.session.add(job)
                migrated_count += 1
            
            db.session.commit()
            logging.info(f"Migrated {migrated_count} jobs from JSON file to database")
            
    except Exception as e:
        db.session.rollback()
        logging.error(f"Failed to migrate jobs: {str(e)}")
