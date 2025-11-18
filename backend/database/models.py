"""
Database Models
SQLAlchemy models for the application
"""

from sqlalchemy import Column, String, DateTime, Boolean, Integer, Float, Text, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List

Base = declarative_base()


# Pydantic models for API
class User(BaseModel):
    """User model"""
    id: str
    email: str
    full_name: str
    role: str
    is_active: bool = True


class UserDB(Base):
    """User database model"""
    __tablename__ = "users"

    id = Column(String, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    full_name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="radiologist")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    analyses = relationship("Analysis", back_populates="user")
    reports = relationship("Report", back_populates="user")


class Patient(Base):
    """Patient database model"""
    __tablename__ = "patients"

    id = Column(String, primary_key=True)
    patient_id = Column(String, unique=True, nullable=False)  # Hospital MRN
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    date_of_birth = Column(DateTime, nullable=False)
    gender = Column(String)
    phone = Column(String)
    email = Column(String)
    address = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    studies = relationship("Study", back_populates="patient")


class Study(Base):
    """Imaging study database model"""
    __tablename__ = "studies"

    id = Column(String, primary_key=True)
    patient_id = Column(String, ForeignKey("patients.id"), nullable=False)
    study_instance_uid = Column(String, unique=True)
    study_type = Column(String, nullable=False)  # xray, ct, mri
    body_part = Column(String, nullable=False)
    indication = Column(Text)
    referring_physician = Column(String)
    study_date = Column(DateTime, nullable=False)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    patient = relationship("Patient", back_populates="studies")
    series = relationship("Series", back_populates="study")
    analyses = relationship("Analysis", back_populates="study")


class Series(Base):
    """DICOM series database model"""
    __tablename__ = "series"

    id = Column(String, primary_key=True)
    study_id = Column(String, ForeignKey("studies.id"), nullable=False)
    series_instance_uid = Column(String, unique=True)
    series_number = Column(Integer)
    series_description = Column(String)
    modality = Column(String)
    num_instances = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    study = relationship("Study", back_populates="series")
    images = relationship("Image", back_populates="series")


class Image(Base):
    """DICOM image database model"""
    __tablename__ = "images"

    id = Column(String, primary_key=True)
    series_id = Column(String, ForeignKey("series.id"), nullable=False)
    sop_instance_uid = Column(String, unique=True)
    instance_number = Column(Integer)
    file_path = Column(String, nullable=False)
    thumbnail_path = Column(String)
    metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    series = relationship("Series", back_populates="images")


class Analysis(Base):
    """AI analysis database model"""
    __tablename__ = "analyses"

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    study_id = Column(String, ForeignKey("studies.id"))
    image_id = Column(String)
    modality = Column(String, nullable=False)
    body_part = Column(String, nullable=False)
    model_type = Column(String, default="ensemble")
    model_version = Column(String)

    # Results
    findings = Column(JSON)
    confidence_scores = Column(JSON)
    heatmap_path = Column(String)

    # Metadata
    status = Column(String, default="completed")
    processing_time = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("UserDB", back_populates="analyses")
    study = relationship("Study", back_populates="analyses")
    reports = relationship("Report", back_populates="analysis")


class Report(Base):
    """Radiology report database model"""
    __tablename__ = "reports"

    id = Column(String, primary_key=True)
    analysis_id = Column(String, ForeignKey("analyses.id"))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)

    # Report content
    findings = Column(Text)
    impression = Column(Text)
    recommendations = Column(Text)
    report_text = Column(Text)

    # Status
    status = Column(String, default="draft")  # draft, finalized
    finalized_by = Column(String)
    finalized_at = Column(DateTime)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    analysis = relationship("Analysis", back_populates="reports")
    user = relationship("UserDB", back_populates="reports")


class AuditLog(Base):
    """Audit log for HIPAA compliance"""
    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True)
    user_id = Column(String)
    action = Column(String, nullable=False)
    resource_type = Column(String)
    resource_id = Column(String)
    details = Column(JSON)
    ip_address = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
