"""Add research models for RAG and resource tracking

Revision ID: 4d2c8f5e9a1b
Revises: 3cb799aa1ec5
Create Date: 2026-05-20 15:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '4d2c8f5e9a1b'
down_revision: Union[str, Sequence[str], None] = '3cb799aa1ec5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - add research models and update pipeline status enum."""
    
    # Create project_documents table (for RAG - firm history)
    op.create_table('project_documents',
        sa.Column('id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('project_name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('client_name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('description', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('industry', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('project_type', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('tech_stack', sa.JSON(), nullable=True),
        sa.Column('team_size', sa.Integer(), nullable=False),
        sa.Column('duration_weeks', sa.Integer(), nullable=False),
        sa.Column('budget_range', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('outcome', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('challenges', sa.JSON(), nullable=True),
        sa.Column('key_features', sa.JSON(), nullable=True),
        sa.Column('embedding_id', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('chroma_collection', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('document_status', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('completion_date', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_project_documents_client_name'), 'project_documents', ['client_name'], unique=False)
    op.create_index(op.f('ix_project_documents_document_status'), 'project_documents', ['document_status'], unique=False)
    op.create_index(op.f('ix_project_documents_embedding_id'), 'project_documents', ['embedding_id'], unique=False)
    op.create_index(op.f('ix_project_documents_industry'), 'project_documents', ['industry'], unique=False)
    op.create_index(op.f('ix_project_documents_project_name'), 'project_documents', ['project_name'], unique=False)
    op.create_index(op.f('ix_project_documents_project_type'), 'project_documents', ['project_type'], unique=False)
    
    # Create employees table
    op.create_table('employees',
        sa.Column('id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('email', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('skills', sa.JSON(), nullable=True),
        sa.Column('role', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('level', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('available', sa.Boolean(), nullable=False),
        sa.Column('utilization_rate', sa.Float(), nullable=False),
        sa.Column('current_project_id', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['current_project_id'], ['project_documents.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    op.create_index(op.f('ix_employees_available'), 'employees', ['available'], unique=False)
    op.create_index(op.f('ix_employees_current_project_id'), 'employees', ['current_project_id'], unique=False)
    op.create_index(op.f('ix_employees_name'), 'employees', ['name'], unique=False)
    
    # Create project_assignments table
    op.create_table('project_assignments',
        sa.Column('id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('employee_id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('project_id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('role_on_project', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('allocation_percentage', sa.Float(), nullable=False),
        sa.Column('priority', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('start_date', sa.DateTime(), nullable=False),
        sa.Column('end_date', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], ),
        sa.ForeignKeyConstraint(['project_id'], ['project_documents.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_project_assignments_employee_id'), 'project_assignments', ['employee_id'], unique=False)
    op.create_index(op.f('ix_project_assignments_project_id'), 'project_assignments', ['project_id'], unique=False)
    
    # Update pipeline_runs status enum to include research phases
    # Note: This is a PostgreSQL-specific operation
    # For SQLite, we need to recreate the table
    
    # Get the database dialect
    conn = op.get_bind()
    dialect = conn.dialect.name
    
    if dialect == 'postgresql':
        # PostgreSQL: Can alter enum directly
        op.execute("ALTER TYPE pipelinestatus ADD VALUE IF NOT EXISTS 'searching_firm_history'")
        op.execute("ALTER TYPE pipelinestatus ADD VALUE IF NOT EXISTS 'checking_resources'")
        op.execute("ALTER TYPE pipelinestatus ADD VALUE IF NOT EXISTS 'market_research'")
    else:
        # SQLite: Need to recreate the table with new enum
        # Create a temporary table with the new schema
        op.create_table('pipeline_runs_new',
            sa.Column('id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
            sa.Column('scope_request_id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
            sa.Column('langgraph_thread_id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
            sa.Column('status', sa.Enum('pending', 'searching_firm_history', 'checking_resources', 'market_research', 
                                       'classifying', 'paused', 'analyzing_risks', 'generating_scope', 
                                       'completed', 'failed', name='pipelinestatus'), nullable=False),
            sa.Column('current_node', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
            sa.Column('error_message', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
            sa.Column('started_at', sa.DateTime(), nullable=False),
            sa.Column('completed_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['scope_request_id'], ['scope_requests.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_pipeline_runs_new_langgraph_thread_id'), 'pipeline_runs_new', ['langgraph_thread_id'], unique=False)
        op.create_index(op.f('ix_pipeline_runs_new_scope_request_id'), 'pipeline_runs_new', ['scope_request_id'], unique=False)
        
        # Copy data from old table
        op.execute("INSERT INTO pipeline_runs_new SELECT * FROM pipeline_runs")
        
        # Drop old table and indexes
        op.drop_index(op.f('ix_pipeline_runs_langgraph_thread_id'), table_name='pipeline_runs')
        op.drop_index(op.f('ix_pipeline_runs_scope_request_id'), table_name='pipeline_runs')
        op.drop_table('pipeline_runs')
        
        # Rename new table
        op.rename_table('pipeline_runs_new', 'pipeline_runs')


def downgrade() -> None:
    """Downgrade schema - remove research models and revert pipeline status enum."""
    
    # Drop project_assignments table
    op.drop_index(op.f('ix_project_assignments_project_id'), table_name='project_assignments')
    op.drop_index(op.f('ix_project_assignments_employee_id'), table_name='project_assignments')
    op.drop_table('project_assignments')
    
    # Drop employees table
    op.drop_index(op.f('ix_employees_name'), table_name='employees')
    op.drop_index(op.f('ix_employees_current_project_id'), table_name='employees')
    op.drop_index(op.f('ix_employees_available'), table_name='employees')
    op.drop_table('employees')
    
    # Drop project_documents table
    op.drop_index(op.f('ix_project_documents_project_type'), table_name='project_documents')
    op.drop_index(op.f('ix_project_documents_project_name'), table_name='project_documents')
    op.drop_index(op.f('ix_project_documents_industry'), table_name='project_documents')
    op.drop_index(op.f('ix_project_documents_embedding_id'), table_name='project_documents')
    op.drop_index(op.f('ix_project_documents_document_status'), table_name='project_documents')
    op.drop_index(op.f('ix_project_documents_client_name'), table_name='project_documents')
    op.drop_table('project_documents')
    
    # Note: Downgrading the enum is complex and may require recreating the table
    # For safety, we leave the extended enum in place
