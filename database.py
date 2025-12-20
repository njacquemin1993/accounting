"""
Database models and configuration for the accounting app.
"""

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey,
    Boolean,
    func,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

Base = declarative_base()


class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True)
    account_code = Column(String(10), unique=True, nullable=False)
    account_name = Column(String(100), nullable=False)
    category = Column(String(50))  # Active, Passive, Expenses, Products
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, nullable=False, default=func.now())

    # Relationship with journal entries
    debit_entries = relationship(
        "JournalEntry", foreign_keys="JournalEntry.debit_account_id", viewonly=True
    )
    credit_entries = relationship(
        "JournalEntry", foreign_keys="JournalEntry.credit_account_id", viewonly=True
    )


class JournalEntry(Base):
    __tablename__ = "journal_entries"

    id = Column(Integer, primary_key=True)
    date = Column(DateTime, nullable=False, default=func.now())
    description = Column(String(200), nullable=False)
    debit_account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    credit_account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    amount = Column(Float, nullable=False)
    created_at = Column(DateTime, nullable=False, default=func.now())

    # Relationships
    debit_account = relationship("Account", foreign_keys=[debit_account_id])
    credit_account = relationship("Account", foreign_keys=[credit_account_id])


class DatabaseManager:
    def __init__(self, db_path="accounting.db"):
        self.db_path = db_path
        self.engine = create_engine(f"sqlite:///{db_path}", pool_pre_ping=True)
        self.create_tables()
        self.SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )

    def create_tables(self):
        """Create database tables."""
        Base.metadata.create_all(self.engine)

    def get_session(self):
        return self.SessionLocal()

    def dispose(self):
        """Dispose of the database engine and close all connections."""
        if hasattr(self, "engine"):
            self.engine.dispose()
