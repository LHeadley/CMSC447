from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker, declarative_base

from request_schemas import CreateRequest, ItemRequest, ActionRequest

DATABASE_URL = 'sqlite:///inventory.db'
engine = create_engine(DATABASE_URL, echo=True)  # echo=True logs SQL queries
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

app = FastAPI(root_path='/dev')


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class Item(Base):
    __tablename__ = 'items'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    unit_weight = Column(Integer, nullable=False)  # weight/quantity per unit
    price = Column(Integer, nullable=False)  # price per unit
    stock = Column(Integer, default=0)


class Log(Base):
    __tablename__ = 'logs'

    id = Column(Integer, primary_key=True)
    action = Column(String, nullable=False)  # 'checkout' or 'restock'
    item_name = Column(String, ForeignKey('items.name'))
    item_id = Column(Integer, ForeignKey('items.id'))
    quantity = Column(Integer, nullable=False)
    timestamp = Column(DateTime, default=func.now())


Base.metadata.create_all(engine)


@app.delete('/delete_all')
def delete_all_items(db: Session = Depends(get_db)):
    """Delete all items from the inventory and clears all logs."""
    db.query(Item).delete()
    db.query(Log).delete()
    db.commit()
    return {'message': 'All items deleted from inventory.'}


@app.get('/items')
def get_items(db: Session = Depends(get_db)):
    """Fetch all items in inventory."""
    return db.query(Item).all()


@app.get('/item')
def get_item(request: ItemRequest, db: Session = Depends(get_db)):
    """Gets data for a specific item in inventory"""
    item = db.query(Item).filter_by(name=request.name).first()
    if not item:
        raise HTTPException(status_code=404, detail='Item not found.')

    return item


@app.post('/create', status_code=201)
def create_item(request: CreateRequest, db: Session = Depends(get_db)):
    """Creates a new item in the inventory"""
    if db.query(Item).filter_by(name=request.name).first():
        raise HTTPException(status_code=409, detail='Item already exists.')

    item = Item(name=request.name, unit_weight=request.unit_weight, price=request.price, stock=request.initial_stock)
    db.add(item)
    db.commit()

    return {'message': f'Created item {item.name} with an initial stock of {item.stock}'}


@app.post('/checkout')
def checkout_item(request: ActionRequest, db: Session = Depends(get_db)):
    """Checkout an item from inventory."""
    item = db.query(Item).filter_by(name=request.name).first()

    if not item:
        raise HTTPException(status_code=404, detail='Not enough quantity or item not found.')

    item.stock -= request.quantity
    log_action(db, 'checkout', item.name, item.id, request.quantity)
    db.commit()

    return {'message': f'Checked out {request.quantity} {request.name}(s).'}


@app.post('/restock')
def restock_item(request: ActionRequest, db: Session = Depends(get_db)):
    """Restock an item in inventory."""
    item = db.query(Item).filter_by(name=request.name).first()

    if item:
        item.stock += request.quantity
    else:
        raise HTTPException(status_code=404, detail='Item not found.')

    log_action(db, 'restock', item.name, item.id, request.quantity)
    db.commit()

    return {'message': f'Restocked {request.quantity} {request.name}(s).'}


@app.get('/logs')
def get_logs(db: Session = Depends(get_db)):
    """Fetch all action logs."""
    return db.query(Log).all()


# Helper function to log actions
def log_action(db, action, name, item_id, quantity):
    log_entry = Log(action=action, item_name=name, item_id=item_id, quantity=quantity)
    db.add(log_entry)


# Create a database connection
DATABASE_URL = 'sqlite:///inventory.db'
engine = create_engine(DATABASE_URL, echo=True)
Session = sessionmaker(bind=engine)
Base = declarative_base()
