"""
Database Models and Setup for ALCHEMY

SQLAlchemy models for SQLite database with support for:
- Processing jobs tracking
- Package storage
- System metrics
- Error logging
"""

from sqlalchemy import create_engine, Column, String, Float, Integer, DateTime, Text, JSON, Boolean, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./alchemy.db")

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # Needed for SQLite
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


class ProcessingJob(Base):
    """
    Model for tracking processing jobs.

    Stores information about file processing jobs including
    status, timing, and error information.
    """
    __tablename__ = "processing_jobs"

    id = Column(String, primary_key=True)  # job_id
    file_path = Column(String, nullable=False)
    file_name = Column(String, nullable=False)
    file_size = Column(Integer, default=0)
    file_type = Column(String, default="unknown")

    status = Column(String, default="pending", index=True)  # pending, processing, completed, failed
    error_message = Column(Text, nullable=True)

    processing_time = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    package_id = Column(String, ForeignKey("packages.id"), nullable=True)
    package = relationship("Package", back_populates="jobs")

    # Step timing information
    step_times = Column(JSON, nullable=True)

    # Retry information
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)

    def __repr__(self):
        return f"<ProcessingJob(id={self.id}, status={self.status}, file_name={self.file_name})>"


class Package(Base):
    """
    Model for storing processed packages.

    Stores the complete package data including content chunks,
    tables, quality metrics, and handoff information.
    """
    __tablename__ = "packages"

    id = Column(String, primary_key=True)  # package_id
    version = Column(String, default="1.0")
    source_agent = Column(String, default="archaeologist")
    target_agent = Column(String, default="trend_jacker")

    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    # Package metadata
    metadata = Column(JSON, nullable=True)

    # Content and tables
    content = Column(JSON, nullable=True)
    tables = Column(JSON, nullable=True)

    # Quality assessment
    quality = Column(JSON, nullable=True)

    # Handoff information
    handoff = Column(JSON, nullable=True)

    # Relationships
    jobs = relationship("ProcessingJob", back_populates="package")

    def __repr__(self):
        return f"<Package(id={self.id}, source_agent={self.source_agent}, target_agent={self.target_agent})>"


class ExtractedContent(Base):
    """
    Model for storing extracted content chunks.

    Stores individual content chunks with semantic analysis
    results and quality metrics.
    """
    __tablename__ = "extracted_content"

    id = Column(String, primary_key=True)  # chunk_id
    job_id = Column(String, ForeignKey("processing_jobs.id"), nullable=False, index=True)
    package_id = Column(String, ForeignKey("packages.id"), nullable=True)

    text = Column(Text, nullable=False)
    content_type = Column(String, default="general")

    # Semantic analysis results
    evergreen_score = Column(Float, default=0.0)
    confidence_score = Column(Float, default=0.0)
    quality_level = Column(String, default="low", index=True)

    # Content metrics
    length = Column(Integer, default=0)
    word_count = Column(Integer, default=0)

    # Metadata
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    job = relationship("ProcessingJob")
    package = relationship("Package")

    def __repr__(self):
        return f"<ExtractedContent(id={self.id}, quality_level={self.quality_level}, evergreen_score={self.evergreen_score})>"


class ExtractedTable(Base):
    """
    Model for storing extracted tables.

    Stores table data with structure information and
    validation results.
    """
    __tablename__ = "extracted_tables"

    id = Column(String, primary_key=True)  # table_id
    job_id = Column(String, ForeignKey("processing_jobs.id"), nullable=False, index=True)
    package_id = Column(String, ForeignKey("packages.id"), nullable=True)

    format = Column(String, default="unknown")  # markdown, html, csv, grid
    headers = Column(JSON, nullable=False)
    rows = Column(JSON, nullable=False)

    row_count = Column(Integer, default=0)
    col_count = Column(Integer, default=0)

    # Validation
    is_valid = Column(Boolean, default=True)
    validation_errors = Column(JSON, nullable=True)

    # Metadata
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    job = relationship("ProcessingJob")
    package = relationship("Package")

    def __repr__(self):
        return f"<ExtractedTable(id={self.id}, format={self.format}, row_count={self.row_count})>"


class SystemMetric(Base):
    """
    Model for storing system metrics.

    Stores performance metrics and system health information
    for monitoring and analysis.
    """
    __tablename__ = "system_metrics"

    id = Column(String, primary_key=True)
    metric_name = Column(String, nullable=False, index=True)
    metric_value = Column(Float, nullable=False)

    # Metric metadata
    metric_type = Column(String, default="gauge")  # gauge, counter, histogram
    labels = Column(JSON, nullable=True)

    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f"<SystemMetric(id={self.id}, name={self.metric_name}, value={self.metric_value})>"


class ErrorLog(Base):
    """
    Model for storing error logs.

    Stores error information for debugging and analysis.
    """
    __tablename__ = "error_logs"

    id = Column(String, primary_key=True)
    job_id = Column(String, ForeignKey("processing_jobs.id"), nullable=True, index=True)

    error_type = Column(String, nullable=False, index=True)
    error_message = Column(Text, nullable=False)
    stack_trace = Column(Text, nullable=True)

    # Context information
    context = Column(JSON, nullable=True)

    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    resolved = Column(Boolean, default=False)

    # Relationship
    job = relationship("ProcessingJob")

    def __repr__(self):
        return f"<ErrorLog(id={self.id}, type={self.error_type}, resolved={self.resolved})>"


# Create indexes for better query performance
Index('idx_processing_jobs_status_created', ProcessingJob.status, ProcessingJob.created_at)
Index('idx_packages_timestamp', Package.timestamp)
Index('idx_extracted_content_quality', ExtractedContent.quality_level)
Index('idx_system_metrics_name_timestamp', SystemMetric.metric_name, SystemMetric.timestamp)


def init_db():
    """
    Initialize the database by creating all tables.

    This function should be called on application startup.
    """
    Base.metadata.create_all(bind=engine)


def drop_db():
    """
    Drop all tables from the database.

    WARNING: This will delete all data!
    """
    Base.metadata.drop_all(bind=engine)


def get_db():
    """
    Get database session.

    This is a dependency that can be used in FastAPI endpoints.

    Yields:
        Database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def reset_db():
    """
    Reset the database by dropping and recreating all tables.

    WARNING: This will delete all data!
    """
    drop_db()
    init_db()


if __name__ == "__main__":
    # Initialize database when run directly
    print("Initializing database...")
    init_db()
    print("Database initialized successfully!")
    print(f"Database URL: {DATABASE_URL}")
