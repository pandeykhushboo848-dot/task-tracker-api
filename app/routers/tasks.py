from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session
from app import models, schemas
from app.database import get_db
from app.deps import get_current_user

router = APIRouter(prefix="/tasks", tags=["tasks"])

def get_owned_task(db: Session, task_id: int, user: models.User) -> models.Task:
    task = db.scalar(select(models.Task).where(
        models.Task.id == task_id, models.Task.owner_id == user.id))
    if task is None:
        raise HTTPException(404, "Task not found")
    return task

@router.post("", response_model=schemas.TaskOut, status_code=201)
def create_task(data: schemas.TaskCreate, db: Session = Depends(get_db),
                user: models.User = Depends(get_current_user)):
    task = models.Task(**data.model_dump(), owner_id=user.id)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task

@router.get("", response_model=list[schemas.TaskOut])
def list_tasks(task_status: schemas.Status | None = Query(None, alias="status"),
               skip: int = Query(0, ge=0), limit: int = Query(10, ge=1, le=100),
               db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    q = select(models.Task).where(models.Task.owner_id == user.id)
    if task_status:
        q = q.where(models.Task.status == task_status)
    return db.scalars(q.order_by(models.Task.id).offset(skip).limit(limit)).all()

@router.get("/{task_id}", response_model=schemas.TaskOut)
def get_task(task_id: int, db: Session = Depends(get_db),
             user: models.User = Depends(get_current_user)):
    return get_owned_task(db, task_id, user)

@router.patch("/{task_id}", response_model=schemas.TaskOut)
def update_task(task_id: int, data: schemas.TaskUpdate, db: Session = Depends(get_db),
                user: models.User = Depends(get_current_user)):
    task = get_owned_task(db, task_id, user)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(task, field, value)
    db.commit()
    db.refresh(task)
    return task

@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: int, db: Session = Depends(get_db),
                user: models.User = Depends(get_current_user)):
    db.delete(get_owned_task(db, task_id, user))
    db.commit()