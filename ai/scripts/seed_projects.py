"""Seed script to populate ChromaDB and database with sample project documents.

Run this to add test projects to the RAG system so the firm history search works:
    cd /home/zt113/Learning/ScopeWise/ai
    python scripts/seed_projects.py
"""

import asyncio
from datetime import datetime
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Patch sqlite3 BEFORE any chromadb/langchain_chroma import.
try:
    import pysqlite3  # type: ignore[import-untyped]
    sys.modules["sqlite3"] = pysqlite3
except ImportError:
    pass

from sqlmodel import Session, SQLModel, create_engine

from app.config import get_settings
from app.database.models import ProjectDocument, Employee, ProjectAssignment
from app.agents.retrievers import FirmHistoryRetriever


# Sample projects to seed
SAMPLE_PROJECTS = [
    {
        "project_name": "E-Commerce Platform for Fashion Retailer",
        "client_name": "StyleHub Inc",
        "description": "Built a modern e-commerce platform with real-time inventory, payment processing, and recommendation engine. Integrated with Shopify APIs and Stripe for payments.",
        "industry": "retail",
        "project_type": "e-commerce",
        "tech_stack": ["React", "Node.js", "PostgreSQL", "Redis", "AWS", "Stripe", "Elasticsearch"],
        "team_size": 6,
        "duration_weeks": 16,
        "budget_range": "$150k-$250k",
        "outcome": "Successfully launched with 99.9% uptime, handled Black Friday traffic surge of 10x normal load",
        "challenges": ["Real-time inventory sync across multiple warehouses", "Payment gateway reliability", "Search performance with 50k+ products"],
        "key_features": ["Real-time inventory", "AI recommendations", "Multi-currency support", "Mobile-first design"],
        "document_status": "active",
        "completion_date": datetime(2024, 6, 15),
    },
    {
        "project_name": "Healthcare Patient Portal",
        "client_name": "MedCare Systems",
        "description": "HIPAA-compliant patient portal for appointment scheduling, medical records access, and telemedicine. Integrated with existing EHR systems.",
        "industry": "healthcare",
        "project_type": "web application",
        "tech_stack": ["React", "Python", "FastAPI", "PostgreSQL", "AWS", "Docker", "Kubernetes"],
        "team_size": 8,
        "duration_weeks": 24,
        "budget_range": "$300k-$450k",
        "outcome": "Achieved HIPAA compliance certification, 40% reduction in appointment no-shows, 95% patient satisfaction",
        "challenges": ["HIPAA compliance requirements", "EHR integration complexity", "Video call quality for telemedicine"],
        "key_features": ["Secure messaging", "Video consultations", "Appointment scheduling", "Lab results access"],
        "document_status": "active",
        "completion_date": datetime(2024, 3, 20),
    },
    {
        "project_name": "Fintech Mobile Banking App",
        "client_name": "NeoBank",
        "description": "Full-featured mobile banking application with biometric auth, instant transfers, budget tracking, and investment features.",
        "industry": "finance",
        "project_type": "mobile app",
        "tech_stack": ["React Native", "Node.js", "PostgreSQL", "Redis", "AWS", "Plaid API", "Biometric Auth"],
        "team_size": 10,
        "duration_weeks": 32,
        "budget_range": "$400k-$600k",
        "outcome": "50k+ downloads in first month, 4.8 star rating, processed $2M+ in transactions",
        "challenges": ["Bank-grade security requirements", "Real-time transaction processing", "Biometric authentication reliability"],
        "key_features": ["Instant transfers", "Budget tracking", "Investment portfolio", "Bill payments", "Face ID login"],
        "document_status": "active",
        "completion_date": datetime(2024, 8, 1),
    },
    {
        "project_name": "SaaS Analytics Dashboard",
        "client_name": "DataViz Corp",
        "description": "Real-time analytics dashboard for SaaS companies with customizable widgets, data visualization, and automated reporting.",
        "industry": "technology",
        "project_type": "saas",
        "tech_stack": ["Vue.js", "Python", "FastAPI", "ClickHouse", "Redis", "AWS", "Docker", "D3.js"],
        "team_size": 5,
        "duration_weeks": 14,
        "budget_range": "$120k-$180k",
        "outcome": "Processing 1M+ events/day with <2s query times, 30+ enterprise clients onboarded",
        "challenges": ["Real-time data pipeline at scale", "Complex query optimization", "Multi-tenant data isolation"],
        "key_features": ["Real-time dashboards", "Custom widgets", "Scheduled reports", "Data export", "API access"],
        "document_status": "active",
        "completion_date": datetime(2024, 5, 10),
    },
    {
        "project_name": "AI-Powered Content Platform",
        "client_name": "ContentAI",
        "description": "Content management platform with AI writing assistance, SEO optimization, and automated publishing to multiple channels.",
        "industry": "media",
        "project_type": "web application",
        "tech_stack": ["Next.js", "Python", "FastAPI", "PostgreSQL", "OpenAI API", "AWS", "Vercel"],
        "team_size": 4,
        "duration_weeks": 12,
        "budget_range": "$100k-$150k",
        "outcome": "2x content production speed for clients, 50% better SEO scores, integrated with 5 social platforms",
        "challenges": ["LLM integration costs", "Content quality consistency", "Multi-platform publishing sync"],
        "key_features": ["AI content generation", "SEO scoring", "Multi-channel publishing", "Content calendar", "Analytics"],
        "document_status": "active",
        "completion_date": datetime(2024, 9, 5),
    },
    {
        "project_name": "Supply Chain Management System",
        "client_name": "LogisticsPro",
        "description": "End-to-end supply chain platform with real-time tracking, inventory management, and predictive analytics for demand forecasting.",
        "industry": "logistics",
        "project_type": "enterprise software",
        "tech_stack": ["React", "Node.js", "PostgreSQL", "MongoDB", "Redis", "AWS", "Kafka", "TensorFlow"],
        "team_size": 12,
        "duration_weeks": 40,
        "budget_range": "$600k-$800k",
        "outcome": "25% reduction in inventory costs, 30% faster order fulfillment, predictive accuracy of 85%",
        "challenges": ["Real-time tracking across global network", "Data consistency across systems", "ML model accuracy"],
        "key_features": ["Real-time tracking", "Demand forecasting", "Route optimization", "Supplier management", "Warehouse automation"],
        "document_status": "active",
        "completion_date": datetime(2024, 7, 30),
    },
]

SAMPLE_EMPLOYEES = [
    {
        "name": "Alice Chen",
        "email": "alice.chen@scopewise.io",
        "skills": ["React", "TypeScript", "Node.js", "AWS"],
        "role": "Senior Frontend Developer",
        "level": "senior",
        "available": True,
        "utilization_rate": 0.4,
    },
    {
        "name": "Bob Martinez",
        "email": "bob.martinez@scopewise.io",
        "skills": ["Python", "FastAPI", "PostgreSQL", "Docker", "Kubernetes"],
        "role": "Backend Lead",
        "level": "lead",
        "available": True,
        "utilization_rate": 0.3,
    },
    {
        "name": "Carol Kim",
        "email": "carol.kim@scopewise.io",
        "skills": ["React Native", "iOS", "Android", "Mobile Development"],
        "role": "Mobile Developer",
        "level": "senior",
        "available": False,
        "utilization_rate": 0.9,
    },
    {
        "name": "David Park",
        "email": "david.park@scopewise.io",
        "skills": ["Python", "Machine Learning", "TensorFlow", "Data Engineering"],
        "role": "ML Engineer",
        "level": "senior",
        "available": True,
        "utilization_rate": 0.2,
    },
    {
        "name": "Emma Wilson",
        "email": "emma.wilson@scopewise.io",
        "skills": ["Vue.js", "D3.js", "Data Visualization", "Frontend"],
        "role": "Frontend Developer",
        "level": "mid",
        "available": True,
        "utilization_rate": 0.5,
    },
    {
        "name": "Frank Liu",
        "email": "frank.liu@scopewise.io",
        "skills": ["DevOps", "AWS", "Terraform", "CI/CD", "Kubernetes"],
        "role": "DevOps Engineer",
        "level": "senior",
        "available": True,
        "utilization_rate": 0.1,
    },
    {
        "name": "Grace Taylor",
        "email": "grace.taylor@scopewise.io",
        "skills": ["Project Management", "Agile", "Scrum", "Client Relations"],
        "role": "Project Manager",
        "level": "senior",
        "available": False,
        "utilization_rate": 1.0,
    },
    {
        "name": "Henry Brown",
        "email": "henry.brown@scopewise.io",
        "skills": ["Node.js", "PostgreSQL", "Redis", "Backend"],
        "role": "Backend Developer",
        "level": "mid",
        "available": True,
        "utilization_rate": 0.6,
    },
]


async def seed_projects():
    """Seed database with sample projects and index them in ChromaDB."""
    settings = get_settings()
    
    # Create database engine
    engine = create_engine(settings.database_url)
    SQLModel.metadata.create_all(engine)
    
    print(f"Seeding projects to ChromaDB at: {settings.chroma_persist_directory}")
    print(f"Using OpenRouter for embeddings")
    print("-" * 60)
    
    with Session(engine) as session:
        # Create retriever
        retriever = FirmHistoryRetriever(settings)
        
        # Add projects
        for project_data in SAMPLE_PROJECTS:
            # Check if project already exists
            existing = session.query(ProjectDocument).filter_by(
                project_name=project_data["project_name"]
            ).first()
            
            if existing:
                print(f"  Skipping (exists): {project_data['project_name']}")
                continue
            
            # Create project document
            project = ProjectDocument(
                id=None,  # Will auto-generate
                **project_data,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            session.add(project)
            session.flush()  # Get the ID
            
            # Index in ChromaDB
            try:
                embedding_id = await retriever.index_project(project)
                project.embedding_id = embedding_id
                print(f"  ✓ Indexed: {project.project_name} (embedding: {embedding_id[:8]}...)")
            except Exception as e:
                print(f"  ✗ Failed to index {project.project_name}: {e}")
            
            session.commit()
        
        print("-" * 60)
        print("Projects seeded successfully!")
        
        # Add employees
        print("\nSeeding employees...")
        for emp_data in SAMPLE_EMPLOYEES:
            existing = session.query(Employee).filter_by(
                email=emp_data["email"]
            ).first()
            
            if existing:
                print(f"  Skipping (exists): {emp_data['name']}")
                continue
            
            employee = Employee(
                id=None,
                **emp_data,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            session.add(employee)
            print(f"  ✓ Added: {emp_data['name']} ({emp_data['role']})")
        
        session.commit()
        
        print("-" * 60)
        print("Employees seeded successfully!")
        
        # Print summary
        project_count = session.query(ProjectDocument).count()
        employee_count = session.query(Employee).count()
        
        print("\n" + "=" * 60)
        print("SEEDING COMPLETE")
        print("=" * 60)
        print(f"Projects in database: {project_count}")
        print(f"Employees in database: {employee_count}")
        print(f"ChromaDB location: {settings.chroma_persist_directory}")
        print("\nYou can now test the RAG search with queries like:")
        print('  - "e-commerce platform with React"')
        print('  - "healthcare app with HIPAA compliance"')
        print('  - "mobile banking fintech app"')


if __name__ == "__main__":
    asyncio.run(seed_projects())
