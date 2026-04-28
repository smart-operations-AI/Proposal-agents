from typing import Any, Dict, Optional
from libs.persistence.database import get_engine, Tenant
from sqlalchemy.orm import sessionmaker

class TenantConfigService:
    def __init__(self, db_url: str = "sqlite:///./revenue_agents.db"):
        self.engine = get_engine(db_url)
        self.Session = sessionmaker(bind=self.engine)

    def get_config(self, tenant_id: str) -> Dict[str, Any]:
        """
        Retrieve tenant-specific configuration from the database.
        If not found, return an empty dict (forcing external provision).
        """
        with self.Session() as session:
            tenant = session.query(Tenant).filter(Tenant.id == tenant_id).first()
            if tenant:
                return tenant.config or {}
        
        print(f"[WARNING] No configuration found for tenant {tenant_id}")
        return {}

    def update_config(self, tenant_id: str, new_config: Dict[str, Any]):
        with self.Session() as session:
            tenant = session.query(Tenant).filter(Tenant.id == tenant_id).first()
            if not tenant:
                tenant = Tenant(id=tenant_id, name=f"Tenant {tenant_id}")
                session.add(tenant)
            
            tenant.config = new_config
            session.commit()
