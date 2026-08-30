from sqlalchemy import Column, Integer, String, Numeric, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class QualityRun(Base):
    __tablename__ = "quality_runs"

    id = Column(Integer, primary_key=True, index=True)
    source_name = Column(String(255), nullable=False)
    source_type = Column(String(50), nullable=False)
    file_path = Column(Text)
    run_at = Column(DateTime, default=datetime.utcnow)
    health_score = Column(Numeric(5, 2))
    total_rows = Column(Integer)
    total_columns = Column(Integer)
    status = Column(String(20), default="running")
    triggered_by = Column(String(50), default="user")
    duration_secs = Column(Numeric(8, 2))

    anomalies = relationship("Anomaly", back_populates="run", cascade="all, delete")
    column_profiles = relationship("ColumnProfile", back_populates="run", cascade="all, delete")


class Anomaly(Base):
    __tablename__ = "anomalies"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(Integer, ForeignKey("quality_runs.id", ondelete="CASCADE"))
    column_name = Column(String(255))
    anomaly_type = Column(String(100))
    severity = Column(String(20))
    detected_value = Column(Text)
    expected_range = Column(Text)
    affected_rows = Column(Integer)
    ai_explanation = Column(Text)
    ai_recommendation = Column(Text)
    ai_fix_code = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    run = relationship("QualityRun", back_populates="anomalies")


class ColumnProfile(Base):
    __tablename__ = "column_profiles"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(Integer, ForeignKey("quality_runs.id", ondelete="CASCADE"))
    column_name = Column(String(255))
    data_type = Column(String(50))
    null_count = Column(Integer)
    null_pct = Column(Numeric(5, 2))
    distinct_count = Column(Integer)
    duplicate_count = Column(Integer)
    min_value = Column(Text)
    max_value = Column(Text)
    mean_value = Column(Numeric)
    std_dev = Column(Numeric)
    quality_score = Column(Numeric(5, 2))
    sample_values = Column(Text)

    run = relationship("QualityRun", back_populates="column_profiles")
