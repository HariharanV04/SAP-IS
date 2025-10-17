"""
Database models for the MuleSoft Documentation Generator application.
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
from sqlalchemy.dialects.postgresql import JSON

db = SQLAlchemy()

class Job(db.Model):
    """
    Model for storing job information and status.
    """
    __tablename__ = 'jobs'
    
    id = db.Column(db.String(36), primary_key=True)  # UUID
    filename = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(50), nullable=False, default='pending')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    # Job processing details
    processing_step = db.Column(db.String(100), nullable=True)
    processing_message = db.Column(db.Text, nullable=True)
    error_message = db.Column(db.Text, nullable=True)
    
    # File analysis information
    file_info = db.Column(JSON, nullable=True)
    parsed_details = db.Column(JSON, nullable=True)
    
    # Enhancement settings
    enhance_with_llm = db.Column(db.Boolean, default=False)
    llm_service = db.Column(db.String(50), nullable=True)
    
    # File paths
    upload_path = db.Column(db.String(500), nullable=True)
    results_path = db.Column(db.String(500), nullable=True)
    
    # Relationships
    documents = db.relationship('Document', backref='job', lazy=True, cascade='all, delete-orphan')
    iflow_matches = db.relationship('IFlowMatch', backref='job', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert job to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'filename': self.filename,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'processing_step': self.processing_step,
            'processing_message': self.processing_message,
            'error_message': self.error_message,
            'file_info': self.file_info,
            'parsed_details': self.parsed_details,
            'enhance_with_llm': self.enhance_with_llm,
            'llm_service': self.llm_service,
            'upload_path': self.upload_path,
            'results_path': self.results_path
        }
    
    def update_status(self, status, **kwargs):
        """Update job status and other fields."""
        self.status = status
        self.updated_at = datetime.utcnow()
        
        if status in ['completed', 'failed']:
            self.completed_at = datetime.utcnow()
        
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        
        db.session.commit()

class Document(db.Model):
    """
    Model for storing generated documents.
    """
    __tablename__ = 'documents'
    
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.String(36), db.ForeignKey('jobs.id'), nullable=False)
    document_type = db.Column(db.String(50), nullable=False)  # 'markdown', 'html', 'visualization'
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    content = db.Column(db.Text, nullable=True)  # Store content for small documents
    file_size = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert document to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'job_id': self.job_id,
            'document_type': self.document_type,
            'filename': self.filename,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class IFlowMatch(db.Model):
    """
    Model for storing SAP Integration Suite equivalent matches.
    """
    __tablename__ = 'iflow_matches'
    
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.String(36), db.ForeignKey('jobs.id'), nullable=False)
    status = db.Column(db.String(50), nullable=False, default='pending')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    # Match results
    matches_found = db.Column(db.Integer, default=0)
    match_data = db.Column(JSON, nullable=True)
    
    # Generated files
    report_path = db.Column(db.String(500), nullable=True)
    summary_path = db.Column(db.String(500), nullable=True)
    
    def to_dict(self):
        """Convert iflow match to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'job_id': self.job_id,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'matches_found': self.matches_found,
            'match_data': self.match_data,
            'report_path': self.report_path,
            'summary_path': self.summary_path
        }

class IFlowGeneration(db.Model):
    """
    Model for storing iFlow generation jobs and results.
    """
    __tablename__ = 'iflow_generations'
    
    id = db.Column(db.String(36), primary_key=True)  # UUID
    original_job_id = db.Column(db.String(36), db.ForeignKey('jobs.id'), nullable=False)
    status = db.Column(db.String(50), nullable=False, default='pending')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    # Generation details
    markdown_content = db.Column(db.Text, nullable=True)
    generated_iflow_path = db.Column(db.String(500), nullable=True)
    
    # Deployment information
    deployment_status = db.Column(db.String(50), nullable=True)
    deployment_details = db.Column(JSON, nullable=True)
    
    def to_dict(self):
        """Convert iflow generation to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'original_job_id': self.original_job_id,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'generated_iflow_path': self.generated_iflow_path,
            'deployment_status': self.deployment_status,
            'deployment_details': self.deployment_details
        }

class UserSession(db.Model):
    """
    Model for tracking user sessions and activity.
    """
    __tablename__ = 'user_sessions'
    
    id = db.Column(db.String(36), primary_key=True)  # Session UUID
    ip_address = db.Column(db.String(45), nullable=True)  # IPv6 support
    user_agent = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    last_activity = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Session statistics
    jobs_created = db.Column(db.Integer, default=0)
    documents_generated = db.Column(db.Integer, default=0)
    
    def to_dict(self):
        """Convert session to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'ip_address': self.ip_address,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_activity': self.last_activity.isoformat() if self.last_activity else None,
            'jobs_created': self.jobs_created,
            'documents_generated': self.documents_generated
        }

class SystemMetrics(db.Model):
    """
    Model for storing system metrics and usage statistics.
    """
    __tablename__ = 'system_metrics'
    
    id = db.Column(db.Integer, primary_key=True)
    metric_name = db.Column(db.String(100), nullable=False)
    metric_value = db.Column(db.Float, nullable=False)
    metric_data = db.Column(JSON, nullable=True)
    recorded_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert metric to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'metric_name': self.metric_name,
            'metric_value': self.metric_value,
            'metric_data': self.metric_data,
            'recorded_at': self.recorded_at.isoformat() if self.recorded_at else None
        }
