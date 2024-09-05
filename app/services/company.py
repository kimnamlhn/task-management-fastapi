from typing import List
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from services import utils
from models.company import CompanyModel, SearchCompanyModel
from schemas.company import Company
from services.exception import ResourceNotFoundError

def get_company(db: Session, conds: SearchCompanyModel) -> List[Company]:
    query = select(Company)
    
    if conds.name is not None:
        query = query.filter(Company.name.like(f"%{conds.name}%"))
    
    query.offset((conds.page-1)*conds.size).limit(conds.size)
    
    return db.scalars(query).all()

def get_company_by_id(db: Session, company_id: UUID) -> Company:
    return db.scalars(select(Company).filter(Company.id == company_id)).first()

def add_new_company(db: Session, data: CompanyModel) -> Company:
    company = Company(**data.model_dump())

    company.created_at = utils.get_current_utc_time()
    company.updated_at = utils.get_current_utc_time()
    
    db.add(company)
    db.commit()
    db.refresh(company)
    
    return company

def update_company(db: Session, id: UUID, data: CompanyModel) -> Company:
    company = get_company_by_id(db, id)

    if company is None:
        raise ResourceNotFoundError()
    
    company.name = data.name
    company.description = data.description
    company.mode = data.mode
    company.rating = data.rating
 
    db.commit()
    db.refresh(company)

    return company

def delete_company(db: Session, id: UUID) -> None:
    company = get_company_by_id(db, id)

    if company is None:
        raise ResourceNotFoundError()
    
    db.delete(company)
    db.commit()
